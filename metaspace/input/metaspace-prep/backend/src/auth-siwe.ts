/**
 * =====================================================================
 * SIGN-IN WITH ETHEREUM (EIP-4361)
 * =====================================================================
 *
 * "How do players log in?" is a guaranteed question, and it has a clean
 * answer: they prove control of a private key by signing a structured
 * message. No password, no email, no credential for you to leak.
 *
 * THE MENTAL MODEL: this is challenge-response auth, the same shape as any
 * nonce-based protocol you have implemented. The wallet is the credential
 * store; ecrecover is the verification step. What is new is only WHAT can go
 * wrong.
 *
 * THE FOUR THINGS THE MESSAGE FORMAT DEFENDS AGAINST — worth naming one by one:
 *   nonce      replay of a captured signature (server-issued, single-use)
 *   domain     a phishing site relaying your signature to the real one
 *   chainId    cross-chain replay
 *   issuedAt /
 *   expiration an old signature valid forever
 *
 * AND THE ONE PEOPLE MISS: a smart-contract wallet has no private key, so
 * ecrecover returns nothing. You must fall back to EIP-1271
 * `isValidSignature(hash, sig)` on the account contract. Gaming wallets are
 * increasingly ERC-4337 smart accounts, so on a game backend this is not a
 * footnote — it is the majority case soon. Mentioning EIP-1271 unprompted is
 * a strong signal.
 *
 * AFTER VERIFICATION: issue a normal short-lived JWT and let the rest of the
 * API be ordinary bearer-token auth. Do not re-verify a signature on every
 * request — signature recovery is ~3000x more expensive than an HMAC check,
 * and you gain nothing.
 */

import { randomBytes } from "node:crypto";
import { getAddress, verifyMessage } from "ethers";
import { pool } from "./db.ts";

export interface SiweMessage {
  domain: string;
  address: string;
  statement: string;
  uri: string;
  version: "1";
  chainId: number;
  nonce: string;
  issuedAt: string;
  expirationTime: string;
}

/** EIP-4361 is a byte-exact plaintext format. Any deviation and the
 *  signature the wallet produced will not match what you reconstruct. */
export function formatSiweMessage(m: SiweMessage): string {
  return [
    `${m.domain} wants you to sign in with your Ethereum account:`,
    m.address,
    "",
    m.statement,
    "",
    `URI: ${m.uri}`,
    `Version: ${m.version}`,
    `Chain ID: ${m.chainId}`,
    `Nonce: ${m.nonce}`,
    `Issued At: ${m.issuedAt}`,
    `Expiration Time: ${m.expirationTime}`,
  ].join("\n");
}

export class SiweService {
  private readonly expectedDomain: string;
  private readonly expectedUri: string;
  private readonly chainId: number;
  private readonly ttlSeconds: number;

  constructor(expectedDomain: string, expectedUri: string, chainId: number, ttlSeconds = 300) {
    this.expectedDomain = expectedDomain;
    this.expectedUri = expectedUri;
    this.chainId = chainId;
    this.ttlSeconds = ttlSeconds;
  }

  /** Server-issued nonce. A client-chosen nonce defeats the entire point:
   *  an attacker replays a signature with a nonce they already know. */
  async createChallenge(address: string): Promise<{ message: string; nonce: string }> {
    const nonce = randomBytes(16).toString("hex");
    const now = new Date();
    const expires = new Date(now.getTime() + this.ttlSeconds * 1000);

    await pool.query(
      `INSERT INTO auth_nonce (nonce, wallet) VALUES ($1, $2)`,
      [nonce, getAddress(address).toLowerCase()]
    );

    const message = formatSiweMessage({
      domain: this.expectedDomain,
      address: getAddress(address),
      statement: "Sign in to Metaspace. This request will not trigger a blockchain transaction or cost any gas.",
      uri: this.expectedUri,
      version: "1",
      chainId: this.chainId,
      nonce,
      issuedAt: now.toISOString(),
      expirationTime: expires.toISOString(),
    });

    return { message, nonce };
  }

  /**
   * Verify, then BURN the nonce atomically.
   *
   * The UPDATE ... WHERE consumed_at IS NULL RETURNING pattern is the whole
   * trick: it is a compare-and-swap in one statement. Two concurrent requests
   * with the same captured signature race, and exactly one gets a row back.
   * A SELECT-then-UPDATE would let both through — which is the replay you
   * built the nonce to prevent.
   */
  async verify(message: string, signature: string): Promise<{ address: string }> {
    const fields = parseSiweFields(message);

    if (fields.domain !== this.expectedDomain) {
      throw new AuthError(`domain mismatch: signed for ${fields.domain}`);
    }
    if (Number(fields.chainId) !== this.chainId) {
      throw new AuthError(`chain mismatch: signed for ${fields.chainId}`);
    }
    if (fields.expirationTime && new Date(fields.expirationTime) < new Date()) {
      throw new AuthError("challenge expired");
    }

    // EOA path. A smart-contract wallet would fail here and needs the
    // EIP-1271 fallback described in the header comment.
    let recovered: string;
    try {
      recovered = verifyMessage(message, signature);
    } catch {
      throw new AuthError("malformed signature");
    }

    // Compare checksummed, never raw strings — case differences between
    // checksummed and lowercase forms are a real source of "valid signature
    // rejected" bugs.
    if (getAddress(recovered) !== getAddress(fields.address ?? "")) {
      throw new AuthError("signature does not match claimed address");
    }

    const { rowCount } = await pool.query(
      `UPDATE auth_nonce SET consumed_at = now()
        WHERE nonce = $1 AND consumed_at IS NULL
          AND issued_at > now() - ($2 || ' seconds')::interval
       RETURNING nonce`,
      [fields.nonce, String(this.ttlSeconds)]
    );
    if (rowCount === 0) throw new AuthError("nonce unknown, expired, or already used");

    return { address: getAddress(recovered) };
  }
}

export class AuthError extends Error {}

function parseSiweFields(message: string): Record<string, string | undefined> {
  const lines = message.split("\n");
  const out: Record<string, string | undefined> = {};
  out.domain = lines[0]?.split(" wants you to sign in")[0];
  out.address = lines[1]?.trim();
  for (const line of lines) {
    const match = /^(URI|Version|Chain ID|Nonce|Issued At|Expiration Time): (.+)$/.exec(line);
    if (!match) continue;
    const key = match[1]!.replace(/ /g, "");
    out[key.charAt(0).toLowerCase() + key.slice(1)] = match[2];
  }
  return out;
}
