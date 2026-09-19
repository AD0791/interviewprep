/**
 * Cross-language contract test: does the TypeScript signer produce the exact
 * digest the Solidity verifier recovers from?
 *
 * Run: node --experimental-strip-types --test src/voucher.test.ts
 *
 * WHY THIS TEST IS WORTH SHOWING SOMEONE
 * The struct lives in two places — Solidity and TypeScript — and nothing
 * enforces that they agree. Reorder two uint256 fields in the contract and
 * every compiler stays happy, every unit test on each side passes, and every
 * redemption in production reverts with InvalidSigner. This is integration
 * drift between two systems with no shared schema, which is the same class of
 * bug as a survey form whose field order changed under a flattening script.
 * The fix is the same: derive the contract from one source and assert it in CI.
 *
 * The test parses the typehash string straight out of the .sol file, so it
 * fails the moment the two definitions diverge.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { TypedDataEncoder, Wallet, verifyTypedData, keccak256, toUtf8Bytes } from "ethers";
import { MINT_VOUCHER_TYPES, domain, localDigest, type MintVoucher } from "./voucher.ts";

const CONTRACT_PATH = new URL("../../contracts/src/GameItems.sol", import.meta.url);
const CHAIN_ID = 80002; // Polygon Amoy
const VERIFYING_CONTRACT = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

describe("EIP-712 voucher", () => {
  it("the TS type definition produces the same canonical type string as the contract", () => {
    const solidity = readFileSync(CONTRACT_PATH, "utf8");

    // Pull the literal out of: keccak256("MintVoucher(address to,...)")
    const match = /keccak256\(\s*"(MintVoucher\([^"]*\))"\s*\)/.exec(solidity);
    assert.ok(match, "could not find MINT_VOUCHER_TYPEHASH literal in GameItems.sol");

    const fromSolidity = match[1]!;
    const fromTypeScript = TypedDataEncoder.from(
      MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>
    ).encodeType("MintVoucher");

    assert.equal(
      fromTypeScript,
      fromSolidity,
      "typehash drift: the Solidity struct and the TS types no longer agree"
    );
    assert.equal(keccak256(toUtf8Bytes(fromTypeScript)), keccak256(toUtf8Bytes(fromSolidity)));
  });

  it("round-trips: a signature we produce recovers to our own signer", async () => {
    const wallet = Wallet.createRandom();
    const voucher: MintVoucher = {
      to: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
      id: 3n,
      amount: 1n,
      nonce: 0n,
      deadline: BigInt(Math.floor(Date.now() / 1000) + 3600),
    };

    const types = MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>;
    const sig = await wallet.signTypedData(domain(CHAIN_ID, VERIFYING_CONTRACT), types, voucher);
    const recovered = verifyTypedData(domain(CHAIN_ID, VERIFYING_CONTRACT), types, voucher, sig);

    assert.equal(recovered, wallet.address);
  });

  it("is bound to the chain: the same voucher signed for another chain does not verify", async () => {
    const wallet = Wallet.createRandom();
    const types = MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>;
    const voucher: MintVoucher = {
      to: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
      id: 1n, amount: 1n, nonce: 0n, deadline: 9999999999n,
    };

    // Signed for Amoy (80002), presented as if for Polygon mainnet (137).
    const sig = await wallet.signTypedData(domain(80002, VERIFYING_CONTRACT), types, voucher);
    const recovered = verifyTypedData(domain(137, VERIFYING_CONTRACT), types, voucher, sig);

    // Recovery does not throw — it returns a DIFFERENT, meaningless address.
    // That is the subtlety worth stating in an interview: an invalid signature
    // does not error, it silently recovers to garbage. Any check that is not
    // an explicit comparison against an expected signer is not a check at all.
    assert.notEqual(recovered, wallet.address);
  });

  it("is bound to the contract: replaying against a second deployment fails", async () => {
    const wallet = Wallet.createRandom();
    const types = MINT_VOUCHER_TYPES as unknown as Record<string, Array<{ name: string; type: string }>>;
    const voucher: MintVoucher = {
      to: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
      id: 1n, amount: 1n, nonce: 0n, deadline: 9999999999n,
    };

    const other = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";
    const sig = await wallet.signTypedData(domain(CHAIN_ID, VERIFYING_CONTRACT), types, voucher);
    assert.notEqual(verifyTypedData(domain(CHAIN_ID, other), types, voucher, sig), wallet.address);
  });

  it("changing any field changes the digest", () => {
    const base: MintVoucher = {
      to: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
      id: 1n, amount: 1n, nonce: 0n, deadline: 9999999999n,
    };
    const d = localDigest(CHAIN_ID, VERIFYING_CONTRACT, base);

    assert.notEqual(localDigest(CHAIN_ID, VERIFYING_CONTRACT, { ...base, amount: 2n }), d);
    assert.notEqual(localDigest(CHAIN_ID, VERIFYING_CONTRACT, { ...base, nonce: 1n }), d);
    assert.notEqual(localDigest(CHAIN_ID, VERIFYING_CONTRACT, { ...base, deadline: 1n }), d);
  });
});
