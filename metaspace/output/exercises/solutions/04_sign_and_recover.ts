/**
 * Level 4 — Signing off-chain, verifying on the server.
 *
 * Use case:  A player connects a wallet to your game. There is no password to
 *            check and no account in your users table yet. The only thing you
 *            can ask for is a signature, and the only thing you can do with it
 *            is recover the address that produced it.
 * Purpose:   Understand that verification is *recovery* — you do not compare a
 *            signature to a stored secret, you reconstruct the signer from it.
 * Key facts: EIP-191 defines the "\x19Ethereum Signed Message:\n" prefix that
 *            makes a personal-signed message structurally unable to be a valid
 *            transaction. A signature is (r, s, v): 32 + 32 + 1 bytes.
 *
 * Run: npm run l4        (no network; throwaway key; nothing is sent anywhere)
 */

import {
  hashMessage,
  recoverMessageAddress,
  verifyMessage,
  keccak256,
  stringToHex,
  concatHex,
  slice,
  type Hex,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";

// Anvil account #0 again: published in every toolchain's documentation, holds
// nothing, and exists so that examples like this need no secrets.
const player = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);

// ---------------------------------------------------------------------------
// Part 1 — sign, then recover.
// ---------------------------------------------------------------------------

console.log("--- Part 1: the round trip ---");

const message = "Log me in to Metaspace";
const signature = await player.signMessage({ message });

console.log("signer address :", player.address);
console.log("signature      :", signature);
console.log("  r :", slice(signature, 0, 32));
console.log("  s :", slice(signature, 32, 64));
console.log("  v :", slice(signature, 64, 65));

const recovered = await recoverMessageAddress({ message, signature });
console.log("recovered      :", recovered);
console.log("matches signer :", recovered === player.address);

console.log(
  "\nNothing was looked up. The server holds no key, no public key, and no prior\n" +
    "record of this player, and it still learned the address with certainty. That\n" +
    "is the property ECDSA gives you: the signature plus the message is enough to\n" +
    "reconstruct the public key, and the address is a hash of that public key.\n" +
    "verifyMessage() is the same operation with the comparison folded in:",
);

console.log(
  "verifyMessage  :",
  await verifyMessage({ address: player.address, message, signature }),
);

// ---------------------------------------------------------------------------
// Part 2 — the prefix, and why it exists.
// ---------------------------------------------------------------------------

console.log("\n--- Part 2: what actually got signed ---");

const prefix = stringToHex(`\x19Ethereum Signed Message:\n${message.length}`);
const byHand = keccak256(concatHex([prefix, stringToHex(message)]));

console.log("hashMessage(message) :", hashMessage(message));
console.log("built by hand        :", byHand);
console.log("identical            :", byHand === hashMessage(message));

console.log(
  "\nThe key never signed your message. It signed a hash of your message with a\n" +
    "fixed prefix glued to the front, and that prefix is a safety interlock. A\n" +
    "raw Ethereum transaction is RLP-encoded and can never begin with 0x19, so a\n" +
    "prefixed signature is structurally incapable of being replayed as a transfer\n" +
    "of your funds. This is EIP-191. Any site that asks you to sign unprefixed\n" +
    "raw bytes is asking for something it should not have.\n",
);

// ---------------------------------------------------------------------------
// Part 3 — break it on purpose: the signature never expires.
// ---------------------------------------------------------------------------

console.log("--- Part 3: the replay ---");

/** A naive login check: does this signature belong to this address? */
async function naiveLogin(address: Hex, sig: Hex): Promise<boolean> {
  return verifyMessage({ address, message: "Log me in to Metaspace", signature: sig });
}

console.log("first login  :", await naiveLogin(player.address, signature));
console.log("same sig, an hour later :", await naiveLogin(player.address, signature));
console.log("same sig, from a different IP, forever :", await naiveLogin(player.address, signature));

console.log(
  "\nThat is a fatal bug, and it is the most common one in hand-rolled wallet\n" +
    "login. The signature is a bearer token with no expiry. Anyone who sees it —\n" +
    "in a log file, in a proxy, in a leaked database — can log in as that player\n" +
    "for the rest of time, without ever touching the key.\n\n" +
    "The fix has three parts, and together they are Sign-In With Ethereum\n" +
    "(EIP-4361), which level 5 builds. The server issues a random nonce and\n" +
    "records it; the message the player signs contains that nonce, the domain of\n" +
    "the site and an expiry; and the server deletes the nonce the moment it is\n" +
    "used, so the second presentation of the same signature finds nothing to\n" +
    "match. Notice that all three are server-side state. The wallet cannot make\n" +
    "a login secure on its own.",
);

// ---------------------------------------------------------------------------
// Part 4 — the other replay: across chains and contracts.
// ---------------------------------------------------------------------------

console.log("\n--- Part 4: the replay you cannot see ---");

const voucherish = "mint item 42 to 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
const voucherSig = await player.signMessage({ message: voucherish });

console.log("a 'voucher' signed as a plain string:", voucherish);
console.log("signature:", voucherSig);
console.log(
  "\nThis signature is valid on Polygon, on Ethereum, on every testnet, and to\n" +
    "every contract that happens to check the same string — because nothing in\n" +
    "what was signed says which chain or which contract it was meant for. A game\n" +
    "that authorised mints this way could have its testnet vouchers replayed on\n" +
    "mainnet.\n\n" +
    "EIP-712 fixes this by hashing a typed struct together with a domain\n" +
    "separator that pins the contract name, version, chainId and verifying\n" +
    "address. That is level 10, and it is the single most interview-relevant\n" +
    "thing in this whole ladder for a game studio that mints assets.",
);
