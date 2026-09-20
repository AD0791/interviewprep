# Sources — what to read, what it is good for, and what in it is already wrong

Every link here was checked on **19 September 2026** and returned a page. That matters more
than usual in this ecosystem: a Web3 tutorial written eighteen months ago is often not merely
dated but actively misleading, because the library it teaches has been sunset or the network
it targets has been renamed. Each entry therefore carries a note on what in it has drifted.

The ordering is by usefulness for *this* interview, not by prestige.

---

## 1. Primary specifications — the only things that settle an argument

When an interviewer and a candidate disagree about behaviour, one of these decides it. Knowing
an EIP *by number* is also a cheap, honest signal of having read primary sources.

| Source | What it settles | Read for |
|---|---|---|
| [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) | The fee market: base fee burned, priority fee to the proposer | Article 03; the fee question always comes |
| [EIP-712](https://eips.ethereum.org/EIPS/eip-712) | Typed structured data signing and the domain separator | Articles 05, 08; exercise L10 — the highest-value EIP here |
| [EIP-4361](https://eips.ethereum.org/EIPS/eip-4361) | Sign-In With Ethereum message format | Article 05; exercise L5 |
| [EIP-1155](https://eips.ethereum.org/EIPS/eip-1155) | Multi-token standard — the game inventory standard | Article 07; exercise L11 |
| [EIP-191](https://eips.ethereum.org/EIPS/eip-191) | The `\x19Ethereum Signed Message:` prefix | Article 05; exercise L4 |
| [EIP-55](https://eips.ethereum.org/EIPS/eip-55) | Address checksums encoded in letter case | Exercise L1, L3 |
| [EIP-2612](https://eips.ethereum.org/EIPS/eip-2612) | `permit` — approval by signature instead of a transaction | Article 07 |
| [EIP-170](https://eips.ethereum.org/EIPS/eip-170) | The 24,576-byte contract size limit | Article 06 |
| [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) | EOAs temporarily executing contract code (shipped in Pectra) | Article 05 — the current account-abstraction answer |

**Drift note:** none. EIPs are versioned by number and finalised EIPs do not change. This is
precisely why they are worth quoting instead of blog posts.

## 2. Official documentation

- **[Solidity docs](https://docs.soliditylang.org/en/latest/)** and the
  [release blog](https://www.soliditylang.org/blog/category/releases/). The current release is
  **0.8.37, dated 10 September 2026**; it already carries support for the `SLOTNUM` opcode of
  the forthcoming *Amsterdam* EVM version. *Drift note:* almost every Solidity book and course
  in existence was written against 0.8.1x–0.8.2x. Nothing fundamental has changed for a game
  contract, but custom errors, `unchecked`, and transient storage postdate a lot of material.
- **[Polygon PoS docs](https://docs.polygon.technology/pos/)**. Chain IDs, the POL token, and
  the current architecture. *Drift note:* every tutorial that says "MATIC" and "Mumbai" is
  stale twice over — the token is POL and the testnet is Amoy (chain ID 80002).
- **[viem](https://viem.sh/docs/getting-started)** — the client library the exercises use,
  currently **2.56.8**. *Drift note:* this is the one library here moving fast enough that its
  own docs are the only trustworthy reference.
- **[wagmi](https://wagmi.sh/react/getting-started)** — React hooks over viem, currently
  **3.7.7**. Article 11. *Drift note:* wagmi v1 material (ethers-based) is a different library
  in all but name; check the version on any tutorial before following it.
- **[ethers v6](https://docs.ethers.org/v6/)** — currently **6.17.0**, and still what most
  production Web3 backends actually run, including the reference repo in
  [../input/metaspace-prep](../input/metaspace-prep). *Drift note:* v5→v6 renamed a great deal
  (`providers.JsonRpcProvider` → `JsonRpcProvider`, `BigNumber` → native `bigint`); v5 answers
  in a v6 codebase read as out of date.
- **[OpenZeppelin Contracts 5.x](https://docs.openzeppelin.com/contracts/5.x/)** and its
  [source](https://github.com/OpenZeppelin/openzeppelin-contracts). Read `ERC1155.sol` and
  `ECDSA.sol` directly — they are short, and "I've read the OpenZeppelin implementation" is a
  much better sentence than "I've used OpenZeppelin." *Drift note:* v5 removed `Counters`,
  replaced `_beforeTokenTransfer` hooks with `_update`, and made `Ownable` take an initial
  owner argument. Tutorials using v4 patterns will not compile against v5.
- **[ethereum.org developer docs](https://ethereum.org/en/developers/docs/)** — the best free
  conceptual explanations of accounts, gas, transactions and the EVM.
- **[web3.py](https://web3py.readthedocs.io/en/stable/)** — currently **8.0.0**, a major
  version. Article 12. *Drift note:* the v6→v7→v8 line changed enough API surface that most
  Python-web3 blog posts no longer run; check the version banner on anything you copy.
- **[Foundry Book](https://book.getfoundry.sh/)** — the contract toolchain most studios use in
  2026. You are not expected to have used it; you are expected to know it is what people use
  and that Hardhat is the alternative.

## 3. Interview-question corpora — treat as data about what is asked, not about what is true

These are useful for *coverage* — they tell you which questions recur — and unreliable on
detail. Several still teach `web3.js`, which now carries an official sunset notice, and some
still describe Ethereum as proof-of-work.

- [web3.career — Top 32 Solidity developer interview questions](https://web3.career/learn-web3/solidity-developer-interview-questions)
- [huru.ai — Blockchain developer questions: EVM, smart contracts, audits](https://huru.ai/blockchain-developer-interview-questions-evm-audits-smart-contracts/)
- [Simplilearn — Top 30 blockchain interview questions](https://www.simplilearn.com/tutorials/blockchain-tutorial/blockchain-interview-questions)
- [DevTeam.Space — 21 blockchain interview questions](https://www.devteam.space/hiring-interview-tips/blockchain-interview-questions-and-answers/)

The distilled, corrected version of everything worth keeping from these lives in
[mock_interviews.md](mock_interviews.md) and in the existing
[qa-drill](../input/metaspace-prep/notes/qa-drill.md), which is already good and should be
reread rather than replaced.

## 4. Hands-on security material

You will not become an auditor in eleven days and should not claim to be one. The point of
this section is to be able to say, credibly, "here is the class of bug and here is how I would
avoid shipping it."

- **[Ethernaut](https://ethernaut.openzeppelin.com/)** — short, self-contained contract
  puzzles. Levels 1 (Fallback), 4 (Telephone), 10 (Re-entrancy) and 15 (Naught Coin) are the
  four that map to things a game contract actually gets wrong. Two evenings, not two weeks.
- **[Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz/)** — harder, DeFi-flavoured,
  and mostly beyond the scope of a game studio's contracts. Know that it exists.
- **[Cyfrin Updraft security course](https://updraft.cyfrin.io/courses/security)** — the
  current standard free curriculum. Useful *after* the interview if this becomes the job.

## 5. Academic material

Cite one of these only where it genuinely backs a claim; dropping arXiv numbers for effect is
transparent and counterproductive.

- [*Security Vulnerabilities in Ethereum Smart Contracts: A Systematic Analysis*](https://arxiv.org/abs/2504.05968) — a 2025 taxonomy, useful for organising the vulnerability classes in article 08.
- [*Vulnerability Detection in Smart Contracts: A Comprehensive Survey*](https://arxiv.org/pdf/2407.07922) — survey of the tooling landscape.
- [*EventSpec: Defining and Detecting Event-Semantic Issues in Blockchain Ecosystems*](https://arxiv.org/abs/2609.07865) — 2026, and unusually relevant here: it classifies defects where **emitted events do not match contract state**, which is exactly the failure mode that corrupts an indexer-backed game database. Worth one sentence in the interview if indexing comes up.

## 6. Working code to read

- **[../input/metaspace-prep](../input/metaspace-prep)** — your own repo, and the first thing
  to reread. `GameItems.sol` and `indexer.ts` are the two files to know line by line.
- **[OpenZeppelin ERC1155](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC1155/ERC1155.sol)** — the canonical implementation.
- **[Multicall3](https://www.multicall3.com/)** — deployed at the same address on nearly every
  EVM chain, which is why exercise L3's batched read works without any setup.

## 7. Networks, faucets and explorers you will actually use

- **Polygon Amoy testnet**, chain ID **80002**, native token **POL**, public RPC
  `https://polygon-amoy.drpc.org` (Polygon docs, *Network information*). Mainnet is **137**.
- **[Amoy PolygonScan](https://amoy.polygonscan.com/)** — paste a transaction hash here during
  the exercises; reading a real receipt is worth more than reading about one.
- Faucets for Amoy POL are linked from the Polygon documentation. They rate-limit and change
  hosts often, so find the current one from the docs rather than from a blog post.

**Safety rule that overrides everything in this file:** use a throwaway key with testnet funds
only, and never connect a wallet holding real value to anything that arrives during a hiring
process. The reasoning is in
[positioning.md](../input/metaspace-prep/notes/positioning.md) and it has not changed.
