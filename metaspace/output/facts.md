# The facts sheet — the numbers worth knowing cold

This is the memorisation layer. Everything here is a fact you can be asked for directly and
should be able to produce without hedging, and every one of them was verified on
**19 September 2026** — either against a primary specification, or by computing it, or by
reading it off Polygon Amoy with the code in [exercises/](exercises/).

Facts have a shelf life. The version numbers in section 6 will be wrong within months; the
EIP numbers in section 2 never will be. Where a number was measured rather than specified, it
says so, because "about a second, I measured it last week" is a strong answer and "one second"
stated as a law is a weak one.

---

## 1. Networks

| Network | Chain ID | Gas token | Note |
|---|---|---|---|
| Ethereum mainnet | 1 | ETH | |
| Polygon PoS mainnet | 137 | **POL** | not MATIC — the migration is essentially complete |
| Polygon Amoy testnet | **80002** | POL | replaced Mumbai, which is shut down |
| Sepolia (Ethereum testnet) | 11155111 | ETH | |
| Base | 8453 | ETH | OP-stack L2 |
| Arbitrum One | 42161 | ETH | |
| Optimism | 10 | ETH | |

Measured on Amoy and Polygon mainnet on 19 September 2026 with
[exercises/solutions/02_read_the_chain.ts](exercises/solutions/02_read_the_chain.ts): Amoy
produced blocks about every **1.0 s**, mainnet about every **1.5 s**, and on both the gap
between the `latest` and `finalized` tags was **2 blocks**. That last number is the important
one — it is the post-Rio fast-finality behaviour, and it is the difference between "wait a
minute before crediting a player" and "wait a few seconds."

Ethereum for comparison: a 12-second slot, 32 slots to an epoch, and finality after two
epochs, so roughly 13 minutes. A studio choosing Polygon for a game is choosing that
difference, plus fees measured in fractions of a cent.

## 2. EIPs by number

These are the ones to be able to name without reaching. Naming an EIP correctly is a cheap,
verifiable signal; naming one incorrectly is worse than not naming it at all.

| EIP | What it is |
|---|---|
| 20 / 721 / 1155 | Fungible token / unique token / multi-token standards |
| 55 | Address checksum encoded in hex letter casing |
| 137 (ENS) | Name service — occasionally confused with chain ID 137, which is Polygon |
| 155 | Chain ID inside the signature: cross-chain replay protection |
| 165 | Interface detection, `supportsInterface(bytes4)` |
| 170 | **24,576-byte** deployed contract size limit |
| 191 | The `\x19Ethereum Signed Message:\n` prefix for personal signing |
| 712 | Typed structured data signing, with a domain separator |
| 1559 | Base fee (burned) plus priority fee (to the proposer) |
| 2612 | `permit` — ERC-20 approval by signature |
| 2930 | Access lists (transaction type 1) |
| 3860 | 49,152-byte initcode limit |
| 4337 | Account abstraction via a separate UserOperation mempool |
| 4361 | Sign-In With Ethereum |
| 4844 | Blob transactions (type 3), the L2 data lane |
| 7623 | Raised the floor price of calldata |
| 7702 | An EOA may temporarily execute contract code (transaction type 4) |

## 3. Gas numbers

The base cost of any transaction is **21,000 gas**. Calldata costs **4 gas per zero byte** and
**16 gas per non-zero byte**, and since EIP-7623 there is also a floor: counting each zero byte
as one token and each non-zero byte as four, the transaction pays at least
**10 gas per token**, so data-heavy transactions that do no computation can no longer be cheap.
The exact formula is in [EIP-7623](https://eips.ethereum.org/EIPS/eip-7623).

Storage is the expensive part, and the numbers explain most contract design. Writing a storage
slot from zero to non-zero costs **20,000 gas** plus a **2,100** cold-access charge; changing an
already non-zero slot costs **5,000**; reading a cold slot costs **2,100** and a warm one
**100**. Clearing a slot to zero grants a refund, capped. Emitting a log costs **375** plus
**375 per indexed topic** plus **8 per byte** of data — which is why events are the cheap way to
publish information that only off-chain systems need to read, and why your indexer exists.

The practical consequence, and a good thing to say out loud: **an event is roughly two orders of
magnitude cheaper than a storage write**, so a well-designed game contract stores the minimum
the chain must enforce and emits everything else for the backend to index.

## 4. Selectors and topics you will recognise on sight

A function selector is the first four bytes of `keccak256` of the canonical signature; an event
topic0 is the full 32-byte hash of the event signature. All of these were computed with viem
rather than copied from memory.

| Selector | Signature |
|---|---|
| `0xa9059cbb` | `transfer(address,uint256)` |
| `0x70a08231` | `balanceOf(address)` |
| `0x095ea7b3` | `approve(address,uint256)` |
| `0x23b872dd` | `transferFrom(address,address,uint256)` |
| `0x18160ddd` | `totalSupply()` |
| `0x6352211e` | `ownerOf(uint256)` |
| `0xf242432a` | `safeTransferFrom(address,address,uint256,uint256,bytes)` (ERC-1155) |
| `0x4e1273f4` | `balanceOfBatch(address[],uint256[])` |
| `0x01ffc9a7` | `supportsInterface(bytes4)` |
| `0xd505accf` | `permit(address,address,uint256,uint256,uint8,bytes32,bytes32)` |

| topic0 | Event |
|---|---|
| `0xddf252ad…3b3ef` | `Transfer(address,address,uint256)` |
| `0xc3d58168…d0f62` | `TransferSingle(address,address,address,uint256,uint256)` |
| `0x4a39dc06…f7fb` | `TransferBatch(address,address,address,uint256[],uint256[])` |

Recognising `0xa9059cbb` at the head of some calldata in an explorer, and being able to say
"that's an ERC-20 transfer," is a small party trick that does a lot of work in an interview.

## 5. Signatures and keys

A private key is 32 bytes; the uncompressed public key is 65 bytes, being a `0x04` prefix plus
the 32-byte X and 32-byte Y coordinates; an address is the **last 20 bytes of `keccak256` of
those 64 coordinate bytes**. A signature is 65 bytes: `r` (32), `s` (32), `v` (1). Since EIP-2,
`s` must lie in the lower half of the curve order, which closes the original malleability
trick where flipping `s` produced a second valid signature for the same message — a detail that
matters if you ever use a signature hash as a database key, which you should not.

Recovery is the property to state clearly: given a message and a signature, you compute the
signer's address. You do not look anything up, and the server needs no prior knowledge of the
account. You proved this to yourself in
[exercises/solutions/04_sign_and_recover.ts](exercises/solutions/04_sign_and_recover.ts).

## 6. Versions current on 19 September 2026

These were read from the npm and PyPI registries on the day, not from memory.

| Thing | Version | Why it matters |
|---|---|---|
| Solidity | **0.8.37** (10 Sep 2026) | Ships `SLOTNUM` for the coming Amsterdam EVM |
| OpenZeppelin Contracts | 5.6.x | v5 removed `Counters`, replaced transfer hooks with `_update` |
| viem | **2.56.8** | The exercises' client library |
| wagmi | **3.7.7** | React hooks; v2+ is built on viem, not ethers |
| ethers | **6.17.0** | Still the most common production choice |
| web3.js | 4.16.0 | **Carries an official sunset notice** — do not start new work on it |
| web3.py | **8.0.0** | Major version; most Python tutorials predate it |
| Express | 5.2.1 | v5 finally changed async error handling |
| FastAPI | 0.141.1 | The Python path in article 12 |

Ethereum's recent forks, in order: **Pectra** (May 2025, brought EIP-7702 and EIP-7623),
**Fusaka** (3 December 2025, brought PeerDAS), and **Glamsterdam** next — Amsterdam on the
execution layer and Gloas on the consensus layer, still unshipped as of today, carrying
enshrined proposer-builder separation and block-level access lists. Polygon's own recent
upgrades are **Rio** (October 2025, the throughput and fast-finality release) and **Ithaca**
(July 2026, reliability and failover).

## 7. The five sentences to have ready

Not facts exactly, but the same drill: these are compressed answers you should be able to say
without assembling them on the spot.

An address is the last twenty bytes of the hash of a public key, so accounts are not created,
they are discovered — which is why you can receive funds at an address the chain has never
heard of.

A reorganisation is not corruption; it is the normal resolution of two valid histories, and any
system that writes to a database from chain events must be able to unwrite.

Gas is a market: the base fee is a clearing price the protocol sets and burns, and the priority
fee is a bid for queue position, so an underpriced transaction does not fail — it waits.

An event is cheap and storage is expensive, so contracts store what must be enforced on-chain
and emit what only the backend needs to know.

A signature with no nonce, no domain and no expiry is a bearer token that never expires, which
is why Sign-In With Ethereum and EIP-712 both exist.
