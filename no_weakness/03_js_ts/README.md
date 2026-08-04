# JavaScript and TypeScript

*One track, two halves. JavaScript mechanism first, then the TypeScript type system on top of it.*

TypeScript is a type layer over the JavaScript runtime — it changes what you are allowed to write and nothing about what executes. Studying TS syntax without the JS object model and async model underneath is how people end up writing TypeScript that compiles and fails, so the order here is not negotiable even though the folder is shared.

---

## Half one — JavaScript mechanism

| # | Module | Level | Status |
|---|---|---|---|
| 01 | [The event loop, microtasks, and the single thread](01_event_loop_and_microtasks.md) | L3–L4 | **Written** |
| 03 | Scope, hoisting, and the execution context | L3 | Planned |
| 04 | Closures in depth — memoization, and the stale-closure bug | L3–L4 | Planned |
| 05 | Prototypes, `class`, and what `extends` actually does | L3 | Planned |
| 06 | Event propagation and delegation — capture, bubble, and `stopPropagation` | L3 | Planned |
| 07 | Multi-threading: Web Workers, `worker_threads`, `cluster`, `SharedArrayBuffer` | L4 | Planned |
| 08 | How Node.js works — libuv, the phases, and the thread pool | L3–L4 | Planned |

Module 01 already covers the event-loop portion of what would be 08, and the `worker_threads` measurement that anchors 07. Those two modules extend rather than repeat it.

## Half two — the TypeScript type system

| # | Module | Level | Status |
|---|---|---|---|
| 02 | [The type system — structural typing, erasure, unsoundness](02_the_type_system.md) | L3–L4 | **Written** |
| 09 | Generics and inference — where it fails and what to do | L3–L4 | Planned |
| 10 | Conditional, mapped and template literal types | L4 | Planned |
| 11 | Narrowing — guards, discriminated unions, `satisfies` | L3–L4 | Planned |
| 12 | Typing the boundary — Zod, inference, and the API contract | L4–L5 | Planned |

Order past 01 and 02 is decided by [the diagnostic](../00_self_assessment.md), sections C and D.

---

## Coverage against the syllabus

The video syllabus in `../assets/` lists: Scope, Closure, Hoisting, Execution Context, Prototype, OOP, Event Propagation, Event Delegation, Asynchronous JavaScript, Memoization, Multi-threading in Browser, Multi-threading in Node.js, and How Node.js works.

Modules 01 and 07–08 cover the async, threading and Node internals. Modules 03–05 cover scope, hoisting, execution context, closures, memoization and prototypes. Module 06 covers propagation and delegation. Watching the video and then working the corresponding module is a good pairing — **the video teaches the topic, the module makes it explainable under pressure**, which is the gap this repo exists to close.
