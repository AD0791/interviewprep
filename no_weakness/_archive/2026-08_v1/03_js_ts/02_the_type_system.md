# The TypeScript type system

*Structural typing, erasure, and the four ways `strict` mode still lets you crash.*

**Level: L3–L4.** Every error message and every runtime crash below was produced by running **TypeScript 7.0.2** with `--strict` and executing the emitted JavaScript on Node v22. Read [01 — the event loop](01_event_loop_and_microtasks.md) first; TypeScript is a type layer over that runtime and nothing here changes what executes.

---

## 1. The thing you already do

```ts
interface Transfer {
  amount: number;
  to: string;
}

async function send(t: Transfer): Promise<boolean> {
  const res = await api.post("/transfers", t);
  return res.ok;
}
```

Types on the arguments, a typed return, red squiggles when you get it wrong. It catches real bugs and you would not go back.

---

## 2. The question you cannot answer about it

You have `AccountId` and `UserId`, both `{ id: string }`, meaning entirely different things. Does TypeScript stop you passing one where the other is expected? It does not. Why not, and what do you do about it?

`const t: Transfer = { amount: 10, currency: "HTG" }` is an error — `currency` is not on `Transfer`. Assign the identical object through a variable first and it compiles. Why does the same object pass one way and fail the other?

You have `--strict` on. Can you still write code that type-checks perfectly and throws `TypeError` at runtime? **Yes — four different ways, all shown below, all with zero compile errors.**

And: an API returns JSON, you annotate it `Transfer`, you ship. What did the compiler actually verify about that data?

---

## 3. What the machine actually does

### 3.1 Structural typing: shape is identity

Most typed languages you have met are **nominal** — a `UserId` is a `UserId` because it is declared as one. TypeScript is **structural**: a type is a description of a shape, and anything of that shape belongs.

```ts
interface AccountId { id: string }
interface UserId    { id: string }
function closeAccount(a: AccountId) {}

const user: UserId = { id: "u-1" };
closeAccount(user);              // compiles cleanly
```

No error. Two concepts that must never be confused are, to the compiler, the same type — because they have the same shape.

This is a deliberate design choice, not a bug. TypeScript describes JavaScript, and JavaScript objects do not carry nominal identity; a function that reads `.id` works on anything with an `.id`. Structural typing is what lets you type existing untyped code without rewriting it.

The cost is that **your domain distinctions are invisible to the compiler**, and mixing up two ID types is exactly the bug you most want caught. The fix is to make the shapes genuinely different — *branding*:

```ts
type Branded<T, B> = T & { readonly __brand: B };
type AcctId = Branded<string, "acct">;
declare function close2(a: AcctId): void;
close2("u-1");
```

```
error TS2345: Argument of type 'string' is not assignable to parameter of type 'AcctId'.
  Type 'string' is not assignable to type '{ readonly __brand: "acct"; }'.
```

The `__brand` property never exists at runtime — it is a phantom that only the type checker sees — but it makes the shapes different, so structural typing now works *for* you. In a banking domain where account numbers, user IDs and transaction references are all strings, this is worth doing.

### 3.2 Erasure: none of this exists at runtime

Compile a file of types and look at what comes out:

```ts
interface Transfer { amount: number }
type Currency = "HTG" | "USD";
enum Status { Open, Closed }
function send(t: Transfer, c: Currency): boolean { return t.amount > 0; }
```

```js
"use strict";
var Status;
(function (Status) {
    Status[Status["Open"] = 0] = "Open";
    Status[Status["Closed"] = 1] = "Closed";
})(Status || (Status = {}));
function send(t, c) { return t.amount > 0; }
```

The `interface` is gone. The `type` is gone. The parameter annotations and the return type are gone. **`enum` survived**, because it is one of the few TypeScript constructs that emits real JavaScript — which is why `const enum` and `as const` unions are often preferred, and why an enum is the one thing here you can inspect at runtime.

Two consequences worth stating precisely, because they are the root of most TypeScript disappointment.

**There is no runtime type checking, ever.** Types constrain what you can write, not what can arrive. Data crossing a boundary — an HTTP response, `JSON.parse`, `localStorage`, a form — is unchecked no matter what you annotate it.

**You cannot branch on a type.** `typeof Transfer` will not compile because `Transfer` is not a value. Narrowing at runtime requires something that exists at runtime: a discriminant property, `typeof`, `instanceof`, or a validation library.

Which is why the correct pattern at a boundary is a schema validator — Zod, Valibot, io-ts — that performs a real runtime check *and* infers the static type from the same declaration, so the two cannot drift apart. Annotating a `fetch` result as `Transfer` is a claim about data you have not inspected.

### 3.3 Excess property checks, and why they seem inconsistent

```ts
interface Transfer { amount: number }

const t1: Transfer = { amount: 10, currency: "HTG" };   // error
const tmp = { amount: 10, currency: "HTG" };
const t2: Transfer = tmp;                                // fine
```

```
error TS2353: Object literal may only specify known properties,
              and 'currency' does not exist in type 'Transfer'.
```

The first errors. The second — the identical object — does not.

Structurally, `{amount, currency}` *is* assignable to `Transfer`: it has everything `Transfer` requires. Extra properties are fine under structural typing, and they have to be, or subtyping would not work.

So excess property checking is a **special case bolted on for object literals only**, because a literal with an unexpected property is almost always a typo or a misread API — you meant `currency` to do something and it will not. Once the object has been through a variable, TypeScript assumes you know what you are doing and falls back to plain structural assignability.

Knowing this stops you concluding the checker is unreliable when the same value behaves differently in two places.

---

## 4. Break it on purpose

Four programs. All compile under `--strict` with **zero errors**. Two of them throw `TypeError`.

### 4.1 `as` is a claim, not a check

```ts
interface Transfer { amount: number }
const raw: unknown = { amont: 10 };      // typo in the incoming data
const bad = raw as Transfer;
console.log(bad.amount.toFixed(2));
```

Compiles clean. Runs:

```
as -> TypeError: Cannot read properties of undefined (reading 'toFixed')
```

`as` does not convert, validate, or inspect anything. It tells the compiler *stop checking, I know better* — and the compiler complies. Every assertion is an unverified promise, and this one was wrong because the field was misspelled upstream.

Which makes `as` most dangerous exactly where it is most used: at API boundaries, where you know least about the data. `response.json() as Transfer` is the single most common way a strict TypeScript codebase crashes in production.

The rule: reach for a **type guard** or a schema parse instead, and treat every `as` in a diff as a question — *what verified this?*

### 4.2 Array covariance is unsound by design

```ts
class Animal {}
class Dog extends Animal { bark(){ return "woof"; } }

const dogs: Dog[] = [new Dog()];
const animals: Animal[] = dogs;   // allowed
animals.push(new Animal());       // allowed
dogs[1].bark();
```

Zero compile errors. Runs:

```
covariance -> TypeError: dogs[1].bark is not a function
```

`Dog[]` is assignable to `Animal[]`, which is fine for reading and unsafe for writing — `animals` and `dogs` are the same array, so pushing an `Animal` puts a non-`Dog` into a `Dog[]`.

TypeScript knows this is unsound and permits it anyway, which is the important thing to be able to say. Full soundness here would require rejecting enormous amounts of correct, ordinary JavaScript, and the team made an explicit trade: **usability over soundness**. `ReadonlyArray<Dog>` is the safe alternative when you only need to read.

Being able to state that TypeScript is deliberately unsound, and name a case, is a strong signal. It shows you understand the tool as an engineering compromise rather than a guarantee.

### 4.3 `any` is a hole, and it spreads

```ts
function parse(json: string): any { return JSON.parse(json); }
const n: number = parse("{}").deeply.nested.thing;
```

No error anywhere. `any` disables checking for the value *and everything reached through it* — property access, calls, the eventual assignment to `number`. One `any` at a boundary silently unchecks an entire subtree of your program.

`JSON.parse` returns `any` by default, which is why parsing is where `any` usually enters a codebase.

The alternative is `unknown`: the same "I don't know what this is," but it forces you to prove something before use.

```ts
const u: unknown = "12";
u.length;        // error
const a2: any = "12";
a2.length;       // fine, unchecked
```

`unknown` is the type-safe top type — assignable *from* anything, assignable *to* nothing without narrowing. Turn on `noImplicitAny`, and treat every explicit `any` as debt with a comment attached.

### 4.4 Function parameter variance, and the one place `strict` protects you

```ts
type Handler = (a: Animal) => void;
const dogHandler = (d: Dog) => d.bark();
const h: Handler = dogHandler;
```

```
error TS2322: Type '(d: Dog) => void' is not assignable to type 'Handler'.
  Types of parameters 'd' and 'a' are incompatible.
    Property 'bark' is missing in type 'Animal' but required in type 'Dog'.
```

This one is caught, and the reason is instructive. A `Handler` may be called with any `Animal`; `dogHandler` calls `.bark()`, which a plain `Animal` does not have. Function parameters must be **contravariant** — a substitute must accept *at least* as much as the original.

Note the asymmetry with 4.2: arrays are unsoundly covariant and permitted, function parameters are correctly contravariant and rejected — but only under `strictFunctionTypes`, which is part of `strict` and off without it. Methods declared with method syntax are still checked bivalently even under strict, for backwards-compatibility reasons. TypeScript's soundness is a patchwork of deliberate decisions, and knowing where the holes are is more useful than believing there are none.

---

## 5. The judgment call

### 5.1 What TypeScript actually guarantees

Stated plainly, because this is the question underneath all four failures above: **TypeScript guarantees that the code you wrote is internally consistent with the types you declared.** It guarantees nothing about data entering the program from outside, and it is deliberately unsound in specific documented places.

So the contract is: types are a design and refactoring tool, and a documentation tool, and they eliminate a large class of typos and shape errors at zero runtime cost. They are not a validation layer. Any codebase treating them as one has an unguarded boundary somewhere.

### 5.2 Where to spend effort

Put real effort at the **boundaries** — HTTP responses, form input, `localStorage`, environment variables, message queues, anything from a database driver typed loosely. Validate there with a schema that both checks at runtime and infers the static type, so one declaration serves both and they cannot drift.

Inside the boundary, keep types simple. Deeply generic, conditional, recursive type machinery is where TypeScript stops paying for itself: compile times climb, error messages become unreadable, and colleagues stop touching the file. A mapped type that saves fifty lines of duplication is worth it; a type-level parser is a hobby.

And prefer making illegal states unrepresentable over checking for them. A discriminated union — `{status:"pending"} | {status:"settled", settledAt: Date}` — means "settled without a date" cannot be written, which is stronger than any runtime check and costs nothing.

### 5.3 Against Python's type hints, since you use both

| | TypeScript | Python |
|---|---|---|
| Typing discipline | Structural | Structural for `Protocol`, nominal for classes |
| Checked by | The compiler, before emit | Nothing at runtime; `mypy`/`pyright` separately |
| At runtime | **Fully erased** (except `enum`) | **Present** in `__annotations__` |
| Runtime validation | Zod / Valibot | Pydantic — which reads the annotations directly |
| Soundness | Deliberately unsound in places | Deliberately optional everywhere |

The interesting row is the third, and it is the comparison worth having ready. Python keeps annotations as real objects at runtime, which is precisely how Pydantic and FastAPI work — FastAPI reads your type hints and builds a validator from them. TypeScript erases everything, so the equivalent requires a *separate* schema declaration and a library that infers the type from it. Same destination, opposite direction of travel: Python derives validation from types, TypeScript derives types from validation.

---

## 6. Interview angles

### "What's structural typing, and what does it cost you?"

> "A type in TypeScript is a description of a shape rather than a name, so anything with the right shape is assignable. That's what lets you put types over existing JavaScript without rewriting it, which is the whole design goal.
>
> The cost is that domain distinctions disappear. I tested this: an `AccountId` and a `UserId`, both `{ id: string }`, and passing one where the other is expected compiles cleanly — because to the compiler they're the same type. In a banking system that's exactly the bug you most want caught.
>
> The fix I'd use is branding — intersect the type with a phantom property that never exists at runtime, so the shapes genuinely differ and structural typing starts working for you instead of against you. Then passing a bare string where an `AcctId` is expected is a compile error, which is what you wanted all along."

### "You have `--strict` on. Can you still crash?"

> "Yes, and I'd give two examples because they fail for different reasons.
>
> The first is `as`. An assertion isn't a check, it's an instruction to stop checking — so `response.json() as Transfer` compiles no matter what actually arrives. I ran a case where the incoming field was misspelled: zero compile errors, and a `TypeError` on the first property access. That's the most common way a strict codebase crashes in production, because `as` gets used exactly at boundaries where you know least about the data.
>
> The second is more interesting because it's deliberate. Arrays are covariant — `Dog[]` is assignable to `Animal[]` — which is safe to read from and unsafe to write to. So you can alias a `Dog[]` as an `Animal[]`, push a plain `Animal`, and then call `.bark()` on it. Compiles clean, throws at runtime. TypeScript knows that's unsound and allows it anyway, because rejecting it would reject a huge amount of ordinary correct JavaScript. That's the thing I'd want to convey: TypeScript is an engineering compromise, not a proof system, and knowing where the holes are is more useful than assuming there aren't any."

### "How do you handle data from an API?"

> "I don't annotate it, I validate it — because types are fully erased. If I write `as Transfer` on a fetch result, the compiler has verified nothing at all about the bytes that arrived; it's just stopped asking.
>
> So at the boundary I'd use a schema validator like Zod, which does a real runtime check and infers the static type from the same declaration. One source of truth, and the type can't drift from the validation. Inside the boundary I trust the types and keep them simple.
>
> The comparison I find useful is with Python, since I work in both. Python keeps annotations at runtime, in `__annotations__`, which is exactly how Pydantic and FastAPI work — FastAPI reads your type hints and builds the validator from them. TypeScript erases everything, so you have to go the other way: declare the schema and infer the type from it. Same destination, opposite direction."

### "`any` versus `unknown`?"

> "Both mean 'I don't know what this is', and the difference is what happens next. `any` switches off checking for that value and everything reached through it, so one `any` at a boundary silently unchecks a whole subtree — I tested a function returning `any` and then read `.deeply.nested.thing` off it and assigned that to a `number`, with no error anywhere.
>
> `unknown` is the safe version: assignable from anything, assignable to nothing until you narrow it. So it forces you to prove something before use — a `typeof` check, a discriminant, or a schema parse.
>
> My rule is `unknown` at boundaries, `noImplicitAny` on, and any explicit `any` treated as debt with a comment saying why. `JSON.parse` returning `any` is usually where it gets into a codebase in the first place."

---

## 7. To add to `RECALL.md`

- **Structural**, not nominal: `AccountId` and `UserId` both `{id:string}` are interchangeable. Fix = **branding**
- Erasure: `interface` and `type` emit **nothing**; `enum` emits **real JS**
- No runtime type checking, ever. `typeof Transfer` is not even valid — not a value.
- Excess property check fires on **object literals only**; via a variable it passes
- `as` is a claim, not a check → `TypeError: Cannot read properties of undefined`
- Arrays are **unsoundly covariant by design** → `dogs[1].bark is not a function`, zero compile errors
- `any` unchecks the whole subtree; `unknown` forces narrowing
- Function **parameters are contravariant** — caught, but only under `strictFunctionTypes`; methods stay bivalent
- Guarantee: **internal consistency with declared types.** Not validation, not soundness.
- Boundaries get Zod/Valibot; interiors get simple types; prefer discriminated unions to runtime checks
- Python keeps annotations at runtime (Pydantic reads them); TS erases them (infer the type from the schema)

---

← [JS/TS index](README.md) · [01 — event loop](01_event_loop_and_microtasks.md) · [repo plan](../README.md)
