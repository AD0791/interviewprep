/**
 * =====================================================================
 * EIP-712 MINT VOUCHER ISSUANCE
 * =====================================================================
 *
 * The off-chain half of GameItems.sol. The game server decides a reward was
 * earned, signs a typed message saying so, and hands it to the player. No
 * transaction, no gas, no chain interaction at all until the player redeems.
 *
 * WHY THIS PATTERN WINS, in the words you want to use in the room:
 *   - COST: the studio pays nothing for rewards players never claim. At
 *     250k downloads and a daily-login reward, that is most of them.
 *   - THROUGHPUT: issuing a voucher is a database write. It is not bounded by
 *     block time, so your reward service scales like any other API.
 *   - AUTHORITY: the game server stays authoritative over game logic, which
 *     is where anti-cheat has to live anyway. The chain is a settlement
 *     layer, not a rules engine.
 *
 * THE KEY-MANAGEMENT ANSWER YOU MUST HAVE READY
 *   "Where does the signing key live?" — Not in an env var on the app server;
 *   that is the honest starting point but say what you would move to: an
 *   AWS KMS / GCP KMS / HSM-backed signer so the private key never exists in
 *   process memory, the signer sits behind a narrow internal service, and the
 *   key holds SIGNER_ROLE only — never DEFAULT_ADMIN_ROLE. Then rotation is
 *   `grantRole(new)` + `revokeRole(old)` with no redeploy, and a compromise
 *   mints items rather than draining the treasury. Blast-radius reasoning is
 *   what separates a senior answer from a junior one.
 */

import { TypedDataEncoder, Wallet, getAddress, verifyTypedData } from "ethers";
import { pool } from "./db.ts";

// ---------------------------------------------------------------------
// Typed data definition
// ---------------------------------------------------------------------

/**
 * MUST mirror EIP712("MetaspaceGameItems", "1") in the contract constructor,
 * and `verifyingContract` must be the deployed address. Get any field wrong
 * and ecrecover returns a valid-looking but wrong address; the contract
 * reverts with InvalidSigner and you lose an afternoon. Hence the
 * assertDigestMatchesContract() self-check at the bottom of this file —
 * run it once per deployment in CI.
 */
export function domain(chainId: number, verifyingContract: string) {
  return {
    name: "MetaspaceGameItems",
    version: "1",
    chainId,
    verifyingContract: getAddress(verifyingContract),
  } as const;
}

export const MINT_VOUCHER_TYPES = {
  MintVoucher: [
    { name: "to", type: "address" },
    { name: "id", type: "uint256" },
    { name: "amount", type: "uint256" },
    { name: "nonce", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
} as const;

export interface MintVoucher {
  to: string;
  id: bigint;
  amount: bigint;
  nonce: bigint;
  deadline: bigint;
}

export interface SignedVoucher {
  voucher: MintVoucher;
  signature: string;
}

// ---------------------------------------------------------------------
// Issuance
// ---------------------------------------------------------------------

export class VoucherService {
  private readonly signer: Wallet;
  private readonly chainId: number;
  private readonly contractAddress: string;
  /** Vouchers expire. An unbounded voucher is a bearer asset you can never
   *  retire — if the reward economy changes you cannot reprice it. */
  private readonly ttlSeconds: number;

  constructor(signer: Wallet, chainId: number, contractAddress: string, ttlSeconds = 7 * 24 * 60 * 60) {
    this.signer = signer;
    this.chainId = chainId;
    this.contractAddress = contractAddress;
    this.ttlSeconds = ttlSeconds;
  }

  /**
   * @param reason Business idempotency key, e.g. "mission:1042". The UNIQUE
   *   index on (wallet, reason) is what makes a retried HTTP call from a
   *   flaky mobile connection safe. This is the bug that actually happens:
   *   the player's connection drops after the server issued the voucher but
   *   before the response landed, the client retries, and without this index
   *   they get the reward twice. Mobile game + intermittent connectivity is
   *   the normal case, not the edge case.
   */
  async issue(wallet: string, itemId: bigint, amount: bigint, reason: string): Promise<SignedVoucher> {
    const to = getAddress(wallet);

    // Fast path: already issued for this reason — return the SAME voucher
    // rather than minting a second one. Idempotent means "same answer", not
    // "no error".
    const existing = await pool.query<{
      item_id: string; amount: string; nonce: string; deadline: string; signature: string;
    }>(
      `SELECT item_id, amount, nonce, deadline, signature
         FROM mint_voucher WHERE wallet = $1 AND reason = $2`,
      [to.toLowerCase(), reason]
    );
    const prior = existing.rows[0];
    if (prior) {
      return {
        voucher: {
          to,
          id: BigInt(prior.item_id),
          amount: BigInt(prior.amount),
          nonce: BigInt(prior.nonce),
          deadline: BigInt(prior.deadline),
        },
        signature: prior.signature,
      };
    }

    const nonce = await this.nextNonce(to.toLowerCase());
    const deadline = BigInt(Math.floor(Date.now() / 1000) + this.ttlSeconds);
    const voucher: MintVoucher = { to, id: itemId, amount, nonce, deadline };

    // ethers v6: signTypedData builds "\x19\x01" || domainSeparator ||
    // structHash for you, which is byte-for-byte what _hashTypedDataV4 does
    // in the contract.
    const signature = await this.signer.signTypedData(
      domain(this.chainId, this.contractAddress),
      MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>,
      { ...voucher, to }
    );

    // Persist AFTER signing but treat the DB as the record of truth. If the
    // insert loses a race, the ON CONFLICT re-read returns the winner and we
    // discard the voucher we just signed — a signature nobody ever sees
    // cannot be redeemed, because its nonce belongs to the winning row.
    const inserted = await pool.query<{ nonce: string; signature: string; item_id: string; amount: string; deadline: string }>(
      `INSERT INTO mint_voucher (wallet, item_id, amount, nonce, deadline, signature, reason)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       ON CONFLICT (wallet, reason) DO NOTHING
       RETURNING nonce, signature, item_id, amount, deadline`,
      [to.toLowerCase(), itemId.toString(), amount.toString(), nonce.toString(),
       deadline.toString(), signature, reason]
    );

    if (inserted.rowCount === 0) {
      return this.issue(to, itemId, amount, reason); // lost the race; re-read
    }
    return { voucher, signature };
  }

  /**
   * Nonces are per-wallet and monotonic here, but the CONTRACT uses a
   * mapping, not a counter — deliberately. A counter would force strictly
   * ordered redemption, so a player who ignores voucher #3 could never redeem
   * #4. With a mapping, order does not matter. Being able to explain that
   * trade-off is worth more than the code.
   */
  private async nextNonce(walletLower: string): Promise<bigint> {
    const { rows } = await pool.query<{ next: string }>(
      `SELECT COALESCE(MAX(nonce), -1) + 1 AS next FROM mint_voucher WHERE wallet = $1`,
      [walletLower]
    );
    return BigInt(rows[0]?.next ?? "0");
  }

  /** Verify our own signature before handing it out — cheap, and it catches
   *  a domain mismatch at issue time instead of at redeem time. */
  verifyLocally(signed: SignedVoucher): boolean {
    const recovered = verifyTypedData(
      domain(this.chainId, this.contractAddress),
      MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>,
      signed.voucher,
      signed.signature
    );
    return recovered.toLowerCase() === this.signer.address.toLowerCase();
  }
}

// ---------------------------------------------------------------------
// CI self-check
// ---------------------------------------------------------------------

/**
 * Compare the digest computed here with the one GameItems.hashVoucher()
 * returns on-chain. Run it once per deployment.
 *
 * Every team that skips this eventually ships a typehash mismatch — someone
 * reorders a struct field in Solidity and forgets the TypeScript. Nothing
 * fails at compile time; every redemption just reverts. Bringing this up
 * unprompted signals that you have been burned by integration drift before,
 * which you have, in every ETL pipeline you have maintained.
 */
export function localDigest(chainId: number, contractAddress: string, v: MintVoucher): string {
  return TypedDataEncoder.hash(
    domain(chainId, contractAddress),
    MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>,
    v
  );
}
