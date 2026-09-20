# Wallet integration on the client, and what Unity and Unreal have to do with any of it

The advert asks for "wallet integration," and that phrase covers two quite different jobs. One
is the server side — nonces, signature recovery, sessions — which
[article 05](05_wallets_keys_signatures.md) covered and which is where a backend engineer
actually lives. The other is the client: connecting a wallet, asking for signatures, and
showing a player what is happening to a transaction they cannot cancel.

You are not applying for a frontend role. But the client is where every one of your backend
decisions becomes visible, and the studio will expect you to know what the browser half looks
like — including the question their advert raises and does not answer, which is what any of
this has to do with Unity.

---

## Life without a connection library

A browser wallet injects an object at `window.ethereum` speaking the EIP-1193 interface. You
can use it directly:

```ts
const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
const chainId = await window.ethereum.request({ method: "eth_chainId" });
```

Two lines, no dependencies, and it works — until it meets reality. The player has three wallets
installed and they fight over `window.ethereum`. They are on mainnet and your game is on
Polygon, so you must detect the chain, ask them to switch, and handle the switch being rejected
or the chain not being added yet. They open your game on a phone, where there is no injected
provider at all and connection happens over WalletConnect. They disconnect in the wallet UI and
your app does not notice. They switch accounts mid-session and your app keeps showing the
previous player's inventory.

Every one of those is an event to subscribe to, a state to model, and an error to recover from.
That is the entire reason the connection libraries exist: not because talking to a wallet is
hard, but because **wallet state is a distributed system with a human in it**.

## The 2026 stack, stated precisely

**viem** is the low-level client — the same library the exercises use on the server. **wagmi**
is React hooks over viem, with TanStack Query underneath for caching and request deduplication.
On top sits a connector UI kit — RainbowKit or ConnectKit — which supplies the modal, the wallet
list and the chain switcher, and which requires wagmi as a peer dependency rather than replacing
it.

Two changes in **wagmi v3** are worth knowing by name, because most tutorials and most
candidates are still on v2 and the
[official migration guide](https://wagmi.sh/react/guides/migrate-from-v2-to-v3) is explicit
about them.

First, the account hooks were **renamed**: `useAccount` became `useConnection`,
`useAccountEffect` became `useConnectionEffect`, and `useSwitchAccount` became
`useSwitchConnection`. The reasoning is that what these hooks describe is a *connection between
an app and a provider*, not an account in any deeper sense — which is a genuinely better name,
because the distinction between "a wallet is connected" and "a user is authenticated" is exactly
the one people get wrong.

Second, **all connector dependencies are now optional peer dependencies**. wagmi no longer
bundles the wallet SDKs, so `@coinbase/wallet-sdk` and `@walletconnect/ethereum-provider` are
installed explicitly by you. That is a smaller bundle and an extra install step, and it is the
sort of change that breaks a copied tutorial in a way that looks like your fault.

## Connected is not logged in

This is the single most important thing on the client, and it is a security point rather than a
UX one.

When a wallet connects, your app learns an address. **An address is public information.** Anyone
can claim any address by typing it; there is nothing secret about it and nothing has been
proven. An app that treats "wallet connected" as "user authenticated" has no authentication at
all — it has a self-declared username.

Authentication is the SIWE round trip from [level 5](../exercises/solutions/05_siwe_express.ts):
the server issues a nonce, the wallet signs a message containing that nonce along with the
domain, the chain ID and an expiry, and the server recovers the signer and burns the nonce in a
single statement. Only then does a session exist.

So the client has **two** pieces of state that look similar and are not: a connection, owned by
wagmi, and a session, owned by your backend. They can disagree in both directions — the player
can disconnect while holding a valid session cookie, or reconnect a different account while the
old session is still live. The rule that keeps this sane is that a change of address **ends the
session**, unconditionally, which is what `useConnectionEffect` is for.

## Signing: three prompts that look identical and are not

The wallet shows a prompt. What the player is agreeing to differs enormously, and your interface
is responsible for the difference being legible.

A **personal signature** (SIWE login) costs nothing, moves nothing, and is reversible in the
sense that it does nothing by itself. A **typed-data signature** (EIP-712) is the voucher case —
still free, still no transaction, but it authorises something specific later, and because
EIP-712 carries named fields the wallet can display them. A **transaction** costs gas and is
irreversible.

The one that deserves care is the token approval, for the reason
[article 07](07_token_standards_digital_assets.md) gave: an unlimited approval is a standing
authorisation that a contract can act on at any future moment. If a game's marketplace asks for
one, the interface should say what it is asking for, and `permit` should be preferred where the
token supports it.

## Transaction states, which are a UX problem you caused

A transaction is not a request and response. It passes through states that have no equivalent in
a normal API, and the interface must show all of them because the player cannot cancel any of
them.

It is **signed**, then **broadcast**, then **pending** for an unbounded time, then **included**
— which is not yet final — and then **finalised**, or **replaced**, or reverted. On Polygon
after Rio the gap between inclusion and finality is a couple of blocks, so a game can reasonably
show "confirming" for a second or two and then settle
([level 2](../exercises/solutions/02_read_the_chain.ts)). On a slower chain the same flow needs
a genuinely pending state that survives a page reload, because the player will close the tab.

The other half is that **your database is not the chain**. The mint succeeded on chain; the
inventory the client reads comes from your indexer, which is a second or two behind
([article 10](10_backend_architecture_web3_game.md)). So a naive client refetches the inventory
the instant the receipt arrives, sees nothing, and tells the player their sword is missing.
Either poll until the item appears, or have the API report the pending claim alongside confirmed
inventory. This is the kind of detail that makes an interviewer think you have shipped one of
these.

## So what do Unity and Unreal have to do with it?

The advert says game-engine experience "is a plus, it's not necessary," and the honest technical
answer to why is worth giving because it reframes the whole question: **almost nothing on chain
happens in the engine.**

A Unity or Unreal client is a client like any other. It talks to your backend over HTTPS, and
your backend does what this entire track has described. The engine is not a good place to hold
keys — it ships to players' devices, and anything in it is extractable. It is not a good place
to talk to an RPC, because you would be shipping provider credentials to every player and
trusting a modified client. And it cannot show a browser wallet prompt at all.

So the integration lives in three places, none of which is gameplay code. **Your backend** does
everything discussed so far. **A wallet SDK** — Sequence, Immutable, Thirdweb, Privy and similar
vendors all ship engine packages — handles connection and signing, usually by opening a system
browser or an embedded view, because that is where wallets live. And **a deep link or embedded
browser** carries the player between the game and the wallet.

The one genuinely engine-specific concern is the asset pipeline: an item that exists on chain
still needs a mesh, an icon and stats inside the game, and the mapping between token ID and game
asset has to be authoritative somewhere. That is a content problem, and it belongs in the same
database as everything else.

The answer to give, then, is not "I have not used Unity." It is that the engine is a client,
the integration burden sits in the backend and a wallet SDK, and the piece that would actually
need designing is how token IDs map onto game assets and who owns that mapping.

## Trace one claim, from the player's side

The player taps "claim" in the game.

The client already holds a session from the SIWE login, so it posts to your claim endpoint and
receives a voucher and a signature. Nothing has cost anything.

The client asks the wallet to send a transaction calling `mintWithVoucher`. The wallet shows a
prompt with a fee estimate. The player may reject it, which is not an error — it is a normal
outcome your code must handle without a red banner.

The transaction is broadcast. The interface shows pending, with the hash linked to a block
explorer, because being able to see it independently is the one thing that calms a player whose
item has not appeared.

The receipt arrives. The interface does **not** declare victory yet: it waits for the indexer,
polling the inventory endpoint until the item appears — a second or two on Polygon.

The item appears. The client refetches and the sword is in the bag.

```mermaid
sequenceDiagram
    participant P as Player
    participant C as Client (wagmi/viem or engine SDK)
    participant W as Wallet
    participant B as Backend
    participant N as Chain
    P->>C: tap claim
    C->>B: POST /rewards/:id/claim  (session from SIWE)
    B-->>C: voucher + signature
    C->>W: request mintWithVoucher transaction
    W-->>P: prompt (fee shown; may be rejected)
    W->>N: broadcast
    N-->>C: receipt (included, not yet indexed)
    C->>B: poll GET /inventory
    B-->>C: item appears once the indexer catches up
```

## Interview Angles

**"How does a player connect a wallet, and what does your backend do with that?"**

Two separate things, and keeping them separate is the answer. Connecting is a client concern:
wagmi over viem talks to the wallet through EIP-1193, handles multiple injected providers,
mobile connections over WalletConnect, and chain switching, with a kit like RainbowKit supplying
the modal. What the backend does with it is nothing, at first — connecting only tells you an
address, and an address is public, so treating "connected" as "logged in" is the same as
trusting a username with no password. Authentication is the separate SIWE step: my server issues
a nonce, the wallet signs a message naming the domain, chain ID, expiry and that nonce, and the
server recovers the signer and burns the nonce in one statement so two concurrent requests
cannot both use it. After that it is an ordinary session token. The rule I would enforce on the
client is that a change of connected address ends the session immediately, because otherwise a
player who switches accounts is looking at someone else's inventory.

**"What does the frontend need to show that a normal web app doesn't?"**

The states of something it cannot cancel. A transaction is signed, broadcast, pending for an
unbounded time, included, and then finalised — and "included" is not final, because the block
can still be reorganised. On Polygon that window is a couple of blocks so it is seconds, but the
pending state still has to survive a page reload, because players close tabs. The subtler one,
which is really a backend decision showing through, is that the inventory does not come from the
chain — it comes from my database, which the indexer fills a second or two later. So a client
that refetches the moment the receipt arrives will show nothing and tell the player their item
is missing. Either poll until it appears or have the API return pending claims alongside
confirmed holdings. And rejection is not an error state: players decline prompts all the time
and that should return them cleanly to where they were.

**"We use Unity. Does that change anything for you?"**

Not much, and I think that is the accurate answer rather than a convenient one. The engine is a
client: it talks to my backend over HTTPS like any other client, and everything on-chain —
signing vouchers, relaying, indexing, reconciling — stays on the server where it belongs. It
actively should not hold keys or RPC credentials, because the build ships to players' devices
and anything in it is extractable, and it cannot show a browser wallet prompt anyway, so
connection and signing go through a wallet SDK from someone like Sequence, Immutable or Thirdweb
that opens a system browser or an embedded view. The piece that would genuinely need designing
with the game team is the mapping between token IDs and in-game assets — which item ID is which
mesh and which stats, who owns that table, and what the client does when it encounters a token
ID it has no art for, because that will happen the first time you add items without shipping a
client build.
