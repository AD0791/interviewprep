/**
 * Level 11 — The contract side: mintWithVoucher, and the reentrancy in it.
 *
 * Use case:  This is the contract your backend's vouchers are redeemed
 *            against. If it is wrong, every other correct thing you built is
 *            irrelevant, because assets can be created from nothing.
 * Purpose:   Run the attack. Not describe it, not reason about it — deploy the
 *            broken contract into a real EVM, attack it with a real malicious
 *            recipient, watch one voucher mint four items, then move three
 *            lines and watch the same attack fail.
 * Key facts: ERC-1155 REQUIRES notifying a contract recipient via
 *            onERC1155Received, so every mint is a call into untrusted code.
 *            Checks-effects-interactions is what makes that safe. The fix in
 *            this file costs two bytes of bytecode.
 *
 * Requires:  cd ../contracts && npm install && node compile.mjs
 *
 * Run: npm run l11       (no network, no funds, no testnet — the EVM is local)
 */

import { createEVM } from "@ethereumjs/evm";
import { createAddressFromString, hexToBytes, bytesToHex, type Address } from "@ethereumjs/util";
import {
  encodeDeployData,
  encodeFunctionData,
  decodeFunctionResult,
  type Abi,
  type Hex,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { readFileSync } from "node:fs";
import { join } from "node:path";

function requireArtifacts(): Record<string, { abi: Abi; bytecode: Hex; deployedBytecode: Hex }> {
  const path = join(import.meta.dirname, "..", "contracts", "artifacts.json");
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    console.error(
      "No compiled contracts found.\n\n" +
        "This level executes real Solidity in a local EVM, so it needs the\n" +
        "artifacts first. They are build output and are not committed:\n\n" +
        "  cd ../contracts && npm install && node compile.mjs\n",
    );
    process.exit(1);
  }
}

const artifacts = requireArtifacts();

const backendSigner = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);

const CALLER = createAddressFromString("0x1111111111111111111111111111111111111111");
const CHAIN_ID = 1n; // whatever the local EVM reports; the voucher must match it

// ---------------------------------------------------------------------------
// A tiny harness: deploy a contract, call a function, read a value.
// ---------------------------------------------------------------------------

type Evm = Awaited<ReturnType<typeof createEVM>>;

async function deploy(evm: Evm, name: string, args: readonly unknown[]): Promise<Address> {
  const artifact = artifacts[name];
  if (!artifact) throw new Error(`no artifact for ${name}`);

  const data = encodeDeployData({
    abi: artifact.abi,
    bytecode: artifact.bytecode,
    args: args as never,
  });

  const result = await evm.runCall({
    caller: CALLER,
    origin: CALLER,
    gasLimit: 10_000_000n,
    data: hexToBytes(data),
  });

  if (result.execResult.exceptionError) {
    throw new Error(`deploy ${name} failed: ${result.execResult.exceptionError.error}`);
  }
  const address = result.createdAddress;
  if (!address) throw new Error(`deploy ${name} produced no address`);
  return address;
}

async function call(
  evm: Evm,
  to: Address,
  name: string,
  functionName: string,
  args: readonly unknown[],
): Promise<{ ok: boolean; error: string | undefined; returnValue: Uint8Array }> {
  const artifact = artifacts[name]!;
  const data = encodeFunctionData({
    abi: artifact.abi,
    functionName,
    args: args as never,
  });

  const result = await evm.runCall({
    caller: CALLER,
    origin: CALLER,
    to,
    gasLimit: 10_000_000n,
    data: hexToBytes(data),
  });

  return {
    ok: !result.execResult.exceptionError,
    error: result.execResult.exceptionError?.error,
    returnValue: result.execResult.returnValue,
  };
}

async function readBalance(
  evm: Evm,
  token: Address,
  name: string,
  owner: Address,
  id: bigint,
): Promise<bigint> {
  const result = await call(evm, token, name, "balanceOf", [owner.toString(), id]);
  return decodeFunctionResult({
    abi: artifacts[name]!.abi,
    functionName: "balanceOf",
    data: bytesToHex(result.returnValue) as Hex,
  }) as bigint;
}

// ---------------------------------------------------------------------------
// The scenario, run against either contract.
// ---------------------------------------------------------------------------

const ITEM_ID = 42n;
const VOUCHER_ID = 9001n;
const REENTRIES = 3n;

async function runScenario(
  contractName: string,
  reentries_: bigint,
): Promise<{ balance: bigint; reentries: bigint }> {
  const evm = await createEVM();

  // 1. The studio deploys its item contract, trusting one backend signer.
  const token = await deploy(evm, contractName, [backendSigner.address]);

  // 2. The attacker deploys an ordinary-looking ERC-1155 receiver aimed at it.
  const attacker = await deploy(evm, "ReentrantReceiver", [token.toString()]);

  // 3. The backend issues ONE voucher, for ONE item, to the attacker's address.
  //    Everything about this voucher is legitimate: correct signer, correct
  //    domain, unexpired, never used before.
  const voucher = {
    to: attacker.toString() as Hex,
    itemId: ITEM_ID,
    amount: 1n,
    voucherId: VOUCHER_ID,
    deadline: BigInt(Math.floor(Date.now() / 1000) + 3600),
  };

  const signature = await backendSigner.signTypedData({
    domain: {
      name: "Metaspace Items",
      version: "1",
      chainId: Number(CHAIN_ID),
      verifyingContract: token.toString() as Hex,
    },
    types: {
      Voucher: [
        { name: "to", type: "address" },
        { name: "itemId", type: "uint256" },
        { name: "amount", type: "uint256" },
        { name: "voucherId", type: "uint256" },
        { name: "deadline", type: "uint256" },
      ],
    },
    primaryType: "Voucher",
    message: voucher,
  });

  // 4. The attacker redeems it.
  await call(evm, attacker, "ReentrantReceiver", "attack", [voucher, signature, reentries_]);

  const balance = await readBalance(evm, token, contractName, attacker, ITEM_ID);

  const reentriesResult = await call(evm, attacker, "ReentrantReceiver", "reentries", []);
  const reentries = decodeFunctionResult({
    abi: artifacts.ReentrantReceiver!.abi,
    functionName: "reentries",
    data: bytesToHex(reentriesResult.returnValue) as Hex,
  }) as bigint;

  return { balance, reentries };
}

// ---------------------------------------------------------------------------
// Run it.
// ---------------------------------------------------------------------------

console.log("One voucher. One item. A recipient that implements onERC1155Received.\n");

const broken = await runScenario("GameItemsBroken", REENTRIES);
console.log("--- 1. GameItemsBroken, attacked ---");
console.log(`  re-entries attempted : ${REENTRIES}`);
console.log(`  re-entries that ran  : ${broken.reentries}`);
console.log(`  items minted         : ${broken.balance}   <-- from ONE voucher for ONE item`);

const fixed = await runScenario("GameItemsFixed", REENTRIES);
console.log("\n--- 2. GameItemsFixed, attacked with exactly the same voucher ---");
console.log(`  re-entries attempted : ${REENTRIES}`);
console.log(`  re-entries that ran  : ${fixed.reentries}`);
console.log(`  items minted         : ${fixed.balance}   <-- the whole claim reverted`);

// A recipient that does NOT re-enter is an ordinary, well-behaved contract
// wallet. It must still be able to claim, or the "fix" would be a denial of
// service dressed up as security.
const honest = await runScenario("GameItemsFixed", 0n);
console.log("\n--- 3. GameItemsFixed, honest contract recipient ---");
console.log(`  re-entries attempted : 0`);
console.log(`  items minted         : ${honest.balance}   <-- minting still works`);

const brokenSize = (artifacts.GameItemsBroken!.deployedBytecode.length - 2) / 2;
const fixedSize = (artifacts.GameItemsFixed!.deployedBytecode.length - 2) / 2;

console.log(`\ncontract sizes      : broken ${brokenSize} bytes, fixed ${fixedSize} bytes`);

if (broken.balance <= 1n || fixed.balance !== 0n || honest.balance !== 1n) {
  console.error("\nFAILED: the demonstration did not behave as expected.");
  process.exitCode = 1;
}

console.log(
  "\n" +
    "Read those three results together, because the comparison is the whole\n" +
    "lesson. The same voucher, the same signature, the same signer check, the\n" +
    "same replay mapping, the same deadline — and the first contract creates\n" +
    "items out of nothing while the second refuses. The difference is the order\n" +
    "of three lines, and it costs two bytes of bytecode.\n\n" +
    "The third result is the one that makes the second meaningful. When the\n" +
    "attacker re-enters the fixed contract it finds the voucher already marked\n" +
    "used, reverts, and because the mint requires the recipient callback to\n" +
    "succeed, the attacker's entire claim unwinds — it gets nothing at all. An\n" +
    "ordinary contract recipient that simply acknowledges the transfer still\n" +
    "receives its one item. That is the shape you want: the honest path works,\n" +
    "and the attack is not merely limited but wasted.\n\n" +
    "Notice what did NOT save the broken version. The signature was verified\n" +
    "correctly. The voucher-used mapping existed and was written to. The deadline\n" +
    "was checked. Every individual security control was present and functioning,\n" +
    "and the contract was still drained — because a control that runs after\n" +
    "control has left the building is not a control, it is a comment.\n\n" +
    "Notice also that nothing about the attacker is suspicious. Implementing\n" +
    "onERC1155Received is REQUIRED of any contract meant to hold ERC-1155 tokens;\n" +
    "the standard demands the callback precisely so that tokens cannot be sent to\n" +
    "a contract that would be unable to move them. So 'do not call untrusted\n" +
    "code' is not available to you here. The callback is mandatory, the recipient\n" +
    "is arbitrary, and safety has to come from ordering instead.\n\n" +
    "That is checks-effects-interactions: validate, then settle every piece of\n" +
    "state you own, and only then talk to anyone else. A nonReentrant guard is\n" +
    "worth adding as a backstop, but it is not the mechanism, and it protects one\n" +
    "function at a time — two functions sharing state can still be played against\n" +
    "each other, which is the cross-function reentrancy an interviewer will push\n" +
    "you toward once you have answered the easy version.",
);
