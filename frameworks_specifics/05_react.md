# React, From Zero

This article rebuilds React from its founding idea — UI as a function of state — and then walks straight into the four places beginners get hurt: state updates, list keys, effects, and stale closures. Each one is shown breaking before it's shown fixed, because the broken version is what interviews ask you to explain.

---

## 1. The Problem: Keeping the Screen in Sync With the Data

Before React, updating a page meant updating the DOM by hand: find the element, change its text, remember to also update the counter over there, and the badge in the corner, and don't forget the empty-state message when the list hits zero. The state of your app lived *implicitly in the DOM itself*, smeared across a hundred elements, and every change had to touch all the right ones. Miss one and the UI lies.

React's founding idea is to stop synchronizing by hand. You write a function that answers one question — *given the current data, what should the screen look like?* — and React's job is making the real DOM match. When data changes, you don't update the page; you update the data, and React re-runs your function and applies the difference.

```tsx
function Balance({ amount }: { amount: number }) {
  return <h2>Balance: ${amount.toFixed(2)}</h2>;
}
```

That's a component: a function from props to UI. The HTML-looking syntax is JSX — sugar for function calls that build a lightweight description of the desired DOM. Nothing has touched the browser yet; you've described, not commanded. The gap between describing and commanding is where everything else in this article lives.

## 2. State: The Data That Makes Time Pass

Props flow in from the parent; **state** is what a component remembers between renders. This is the whole loop in one component:

```tsx
import { useState } from 'react';

function TransferCounter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Transfers today: {count}
    </button>
  );
}
```

Trace one click, slowly, because this cycle is React. The user clicks. Your handler calls `setCount(1)`. Here is the part that surprises everyone: **`count` does not change.** `count` is a local constant in a function that already ran. What `setCount` does is schedule a re-render — React calls `TransferCounter()` again, and *that* call's `useState(0)` returns the stored value `1`. New render, new constant, new JSX. React diffs the new description against the old one, sees only the text changed, and updates only that text node.

Two rules fall out of this mechanism, and both are interview staples. First, **state updates are asynchronous batches**: calling `setCount(count + 1)` twice in one handler sets `1` twice, because both calls read the same stale `count` from the current render. When the next value depends on the previous one, pass a function — `setCount(c => c + 1)` — which React feeds the *latest* value. Second, **state must be replaced, never mutated**: `items.push(x)` changes the array in place, the reference stays identical, React sees "nothing changed" and skips the re-render. Always produce a new value: `setItems([...items, x])`. If you later use Redux Toolkit, this is exactly the tedium its Immer integration automates ([06_redux_toolkit.md](06_redux_toolkit.md)).

## 3. Lists and Keys: Identity Across Renders

Render a list and React demands a `key` for each item. It's tempting to silence the warning with the array index. Here's the bug that decision buys you:

```tsx
// Each row has an input (imagine "add a note to this transaction")
{transactions.map((tx, i) => (
  <TransactionRow key={i} tx={tx} />   // index as key: looks fine...
))}
```

Type a note into the first row. Now a new transaction arrives at the *top* of the list. Every row shifts down one position — but the keys, being indexes, stay `0, 1, 2...`. React matches old and new rows *by key*, concludes row `0` is still row `0`, and keeps its state. Your typed note now sits on the wrong transaction. Nothing crashed; the data is just quietly wrong, which is worse.

The key is how React tracks *identity* across renders: "this is the same logical item as last time, keep its DOM and state; that key vanished, unmount it." Indexes encode position, not identity. Use the stable id your data already has — `key={tx.id}` — and the note stays with its transaction no matter how the list reorders. Index keys are defensible only for lists that never reorder, insert, or delete.

## 4. Effects: Escaping to the Outside World

Rendering must be pure — same props and state, same JSX, no side effects. But real components need side effects: subscribe to a WebSocket, start a timer, talk to the browser. `useEffect` is the designated exit: it runs your effect *after* the render is on screen, and — the part everyone under-weights — it takes a **cleanup function** to undo the effect.

```tsx
function LivePrice({ symbol }: { symbol: string }) {
  const [price, setPrice] = useState<number | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`wss://feed.example.com/${symbol}`);
    ws.onmessage = (e) => setPrice(JSON.parse(e.data).price);
    return () => ws.close();   // cleanup: THIS is what makes the effect correct
  }, [symbol]);                // re-run only when symbol changes

  return <span>{price ?? '—'}</span>;
}
```

The mental model that prevents whole bug classes: an effect is not "code that runs on mount." It's a **synchronization contract** — "while this component shows `symbol`, a socket for `symbol` should exist." The dependency array says when the outside world must re-sync; the cleanup says how to tear down the old sync before setting up the new one. When `symbol` changes from `EURUSD` to `USDHTG`, React runs the cleanup (closes the old socket) and then the effect (opens the new one). Without cleanup, sockets accumulate — a leak that dev mode actively hunts: React's Strict Mode mounts every component twice *on purpose*, so an effect whose cleanup is missing or wrong misbehaves immediately on your machine instead of eventually in production. If Strict Mode breaks your effect, your effect was already broken.

One honest warning about the most common effect: data fetching. A hand-rolled fetch effect has a race condition (change `symbol` quickly and the slow, stale response can arrive last and win) plus loading/error boilerplate in every component. The fix is either an `AbortController` in cleanup — or recognizing that this problem is so universal it has a library: that's the opening argument of [07_swr_axios.md](07_swr_axios.md).

## 5. The Stale Closure: One Bug, Many Costumes

The single most common "React is broken!" report. Watch it happen:

```tsx
function AutoRefresh() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setSeconds(seconds + 1), 1000);
    return () => clearInterval(id);
  }, []);   // runs once on mount

  return <p>Up for {seconds}s</p>;   // shows 1... and stays at 1 forever
}
```

Why does it freeze at 1? The effect ran once, on the first render, and its arrow function *closed over that render's* `seconds` — which was `0`. Every tick executes `setSeconds(0 + 1)`. The interval isn't broken; it's faithfully repeating a snapshot. Remember section 2: each render's variables are constants belonging to that render. Any long-lived callback — intervals, socket handlers, event listeners — keeps the snapshot from the render that created it.

The fix is one you already know: the functional update, `setSeconds(s => s + 1)`, which asks React for the current value instead of trusting the snapshot. When you meet this bug wearing other costumes — a WebSocket handler using an old filter value, a debounced search reading old text — the diagnosis is identical: *who captured this variable, and at which render?*

## 6. Performance: How React Decides What to Re-Render, and When You Should Care

The default behavior surprises people: when a component's state changes, React re-renders it **and its entire subtree**, children included, whether or not their props changed. That sounds wasteful and usually isn't — re-rendering means re-running functions and diffing descriptions, and the actual DOM (the expensive part) is only touched where the diff found changes. Internally, React's Fiber architecture even splits this into an interruptible *render phase* (computing the diff, pausable to keep typing responsive) and a synchronous *commit phase* (applying it).

So the professional posture is: **don't optimize until something is measurably slow, then measure first.** The measuring tool is the React DevTools Profiler, and the workflow is in [02/03](../02_react_redux_swr_dashboard/03_error_boundaries_suspense_profiling.md). When the profiler convicts a specific subtree, you have three tools: `React.memo(Child)` skips a child's re-render when its props are shallow-equal; `useMemo` caches an expensive computation; `useCallback` keeps a function's reference stable so it doesn't break the first two. The classic trap is memoizing a child and then passing it a fresh inline arrow every render — the always-new prop defeats the memo, and you've added cost without benefit. Stabilize the props, not just the component. (React 19's compiler automates most of this memoization, but interviewers still ask *why* it works, and the answer is reference equality.)

## 7. Interview Angles

**"Walk me through what happens when I click a button that calls setState."** The handler calls the setter, which doesn't change anything in place — it schedules a re-render with the new value. React re-runs the component function, gets a fresh JSX description, diffs it against the previous one (render phase, interruptible), and applies the minimal DOM changes (commit phase, synchronous). The precise thing to say: state variables are per-render constants; setters request the *next* render.

**"Why is my interval/subscription seeing old state?"** Stale closure: the callback captured variables from the render that created it, and long-lived callbacks outlive their render. Functional updates fix the setter case; for reads, either add the value to the effect's dependencies so it re-syncs, or hold the latest value in a ref. The framing that shows depth: this isn't a React quirk, it's JavaScript closures meeting React's render-snapshot model.

**"When do you reach for React.memo?"** After the Profiler shows a specific expensive subtree re-rendering without visual change — not preemptively. And memoization is a chain: memo only helps if the props are referentially stable, which is what useCallback and useMemo exist to provide. Wrapping everything "to be safe" adds comparison overhead and famously breaks the moment someone passes an inline object.
