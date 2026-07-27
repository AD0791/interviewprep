# Battle Card 05 — React & Frontend

## 30-Second Answers

**State ownership.** "Server state is a *cache* — staleness, revalidation, dedupe — that's SWR's job. Client state is owned truth — filters, modals — local state or Redux Toolkit. Jamming API data into Redux hand-rolls a worse SWR; what stays in Redux is genuinely global client-owned state."

**Re-renders & memoization.** "A state change re-renders the subtree; reconciliation patches the DOM minimally, so re-renders are cheap until measured otherwise. `React.memo` backfires when unstable object or function props break equality every render — stabilize the prop with `useCallback`/`useMemo`, don't just wrap the child."

**Error containment.** "Without boundaries, one widget throwing during render unmounts the entire tree — blank page. Per-widget error boundaries make it one broken card; the reset must also revalidate SWR (`onReset` → `mutate`) or Retry replays the poisoned cache. Boundaries miss event handlers and async — those need try/catch."

**Suspense.** "It moves loading UI from per-component `isLoading` ternaries to declarative tree structure: the component suspends, the nearest `<Suspense>` shows the fallback. Paired with an error boundary it makes each widget load, fail, and retry independently."

**Jank diagnosis.** "React Profiler: record the interaction, read the commit bar — storm vs one expensive commit — flamegraph to the widest leaf, then 'why did this render' names the unstable prop or over-broad context. Fix, re-record. Cheap commits but janky page = not React; browser Performance tab."

**Tokens in the browser.** "Refresh tokens never touch localStorage — XSS reads it. HttpOnly cookies (with SameSite/CSRF thinking) or memory-only access tokens with silent refresh."

## Numbers & Facts

| Fact | Value |
|---|---|
| Error boundary API | Class lifecycles only → use `react-error-boundary` |
| Boundary blind spots | Event handlers, async callbacks, SSR |
| SWR suspense opt-in | `useSWR(key, fetcher, { suspense: true })` |
| Long list threshold | Virtualize (~thousands of rows) — [02/01](../../02_react_redux_swr_dashboard/01_react_dashboard_rendering_state.md) |
| Zod's double win | Runtime validation + inferred static type, one source of truth |

## Rapid Fire

- **`useTransition` vs memoization?** → Responsiveness under CPU pressure (deprioritize an update) vs avoiding wasted work — different diseases.
- **Why keys on lists?** → Reconciliation identity; index-as-key breaks state on reorder.
- **SWR's name?** → Stale-while-revalidate: serve cached, refresh in background — same pattern as Redis serve-stale, one tier up.
- **`unknown` vs `any`?** → `unknown` forces narrowing; `any` switches the compiler off.
- **Axios interceptor's auth job?** → Catch 401, single-flight one refresh, replay queued requests with the new token.

## Trap Questions

- *"Wrap everything in `React.memo` to be safe?"* — Equality checks cost too, and unstable props void them; memoize what the Profiler convicts, nothing else.
- *"Put API data in Redux so it's global?"* — You'll rebuild dedupe, revalidation, and staleness by hand; server cache belongs to SWR/React Query, Redux keeps client truth.

## Deep Dives

[02/01 rendering & state](../../02_react_redux_swr_dashboard/01_react_dashboard_rendering_state.md) · [02/03 boundaries, Suspense, profiling](../../02_react_redux_swr_dashboard/03_error_boundaries_suspense_profiling.md) · [02/02 storage & tokens](../../02_react_redux_swr_dashboard/02_browser_apis_and_storage.md)
