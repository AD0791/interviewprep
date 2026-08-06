# Generics, inference, and variance

*Three unsound things that compile clean, the one flag that catches a fourth, and what the compiler actually promises you.*

**Level:** L5 · **Prerequisites:** [`01` structural typing and erasure](00_syllabus.md)
**Syllabus:** [`TS-07`–`TS-12`](00_syllabus.md) · **Roles:** FS ●●● DE ●●
**Measurement:** `Measured` — TypeScript compiler via `npx -p typescript tsc` on `ENV-A`, Node v20.20.2. Every error message and every runtime traceback below came out of a terminal. Compiler behaviour is version-stable for these features; the flags named are current.

---

## 1. The thing you already do

A generic helper, of the kind in every codebase:

```typescript
// Gist: pick.ts
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const out = {} as Pick<T, K>;
  for (const k of keys) out[k] = obj[k];
  return out;
}
```

And a handler registration, of the kind in every event system:

```typescript
// Gist: handlers.ts
interface Animal { name: string }
interface Dog extends Animal { bark(): void }

type Handler = (a: Animal) => void;

const onAnimal: Handler = (d: Dog) => d.bark();     // is this legal?
```

The first is correct and worth being able to write from memory. The second is the interesting one — it is **unsound**, it will throw at runtime when a plain `Animal` arrives, and whether the compiler tells you depends on a single flag most people have never consciously set.

---

## 2. The questions you cannot answer about it

**Is a `(d: Dog) => void` assignable to a `(a: Animal) => void`?** Answer before reading on. Then answer the reverse. One of them is safe and one is not, and the reasoning is the definition of variance.

**Is TypeScript's type system sound?** There is a one-word answer and a counterexample you can write in four lines.

**What does `strict: true` actually turn on?** Naming the sub-flags matters, because one of them is the only thing standing between you and §1's bug.

**And the one that should bother you.** I wrote a file containing four deliberately unsound constructs and compiled it with `--strict`, the most aggressive setting available.

**The compiler reported two errors. Two of the four unsound constructs compiled clean** — and one of them throws `TypeError: dogs[1].bark is not a function` the moment you run it.

Then I turned off one flag, and the error count dropped to **one**.

If you can name which construct is which, skip to §6.

---

## 3. What the machine actually does

### 3.1 The analogy: the compiler is a proof-checker with a deadline

TypeScript is not verifying that your program is correct. It is checking that your program is **internally consistent with the types you declared**, and it is doing so under a hard constraint: it must be fast enough to run on every keystroke, and it must accept the JavaScript people actually write.

Those two constraints buy pragmatism at the cost of rigour. Where full soundness would reject too much idiomatic code or cost too much time, the designers chose to let something through. Those choices are documented and deliberate, not bugs — and knowing where they are is the difference between trusting the compiler and understanding it.

### 3.2 Variance, derived from substitutability

Variance answers one question: if `Dog` is a subtype of `Animal`, when is a *thing containing* `Dog` a subtype of a *thing containing* `Animal`?

The rule follows from asking what a caller can safely do.

**Return positions are covariant.** A function promising to return an `Animal` can safely be one that returns a `Dog`, because every caller expecting an `Animal` gets something that is one. Narrower output is always safe.

**Parameter positions are contravariant** — the reverse. A function that must accept any `Animal` cannot be one that only handles `Dog`, because a caller is entitled to pass a cat. But a function that accepts *any* `Animal` can safely stand in where only `Dog`s will be passed. **Wider input is safe; narrower input is not.**

That is §1's bug: `(d: Dog) => void` used as a `Handler` promises to accept any animal and secretly requires `bark`.

Here is the compiler's verdict, measured:

```typescript
// Gist: variance.ts
type Handler = (a: Animal) => void;
const dogHandler = (d: Dog) => d.bark();
const h: Handler = dogHandler;
```

```text
=== strict: true ===
variance.ts(19,7): error TS2322: Type '(d: Dog) => void' is not assignable to type 'Handler'.
  Types of parameters 'd' and 'a' are incompatible.
    Property 'bark' is missing in type 'Animal' but required in type 'Dog'.
```

Caught, with an explanation that names the exact property ([`TS-VAR-01`](../MEASUREMENTS.md)).

Now the same file with one flag changed:

```text
=== same file, strictFunctionTypes OFF ===
variance.ts(27,30): error TS2353: Object literal may only specify known properties...
```

**The variance error is gone.** `strictFunctionTypes` is the only thing that was catching it, and before TypeScript 2.6 nothing did — function parameters were bivariant, accepted in both directions, because that is what made the DOM's event-handler types usable.

### 3.3 Methods are still bivariant, on purpose, even under `strict`

Here is the exception that surprises people who have just learned the rule.

```typescript
// Gist: variance.ts
interface Box { handle(a: Animal): void }
const b: Box = { handle: (d: Dog) => d.bark() };   // method syntax
```

Under full `--strict`, that produced **no error at all** ([`TS-VAR-02`](../MEASUREMENTS.md)).

The identical unsoundness written as a property — `handle: (a: Animal) => void` — is caught. Written with **method shorthand**, it is not.

`strictFunctionTypes` deliberately exempts method declarations. The reason is `Array<T>`: `push`, `indexOf` and `concat` are methods whose parameters would make arrays uninvariant under a strict rule, and the ecosystem depends on arrays being assignable. Rather than break every codebase, the exemption was carved out.

So the practical rule is that **the syntax you choose changes whether the check runs.** Property syntax gets contravariance checking, method syntax does not. If you want the check on a callback field in an interface, write it as a property.

### 3.4 Array covariance: the unsoundness that compiles and then throws

The most demonstrable hole, in four lines.

```typescript
// Gist: cov.ts
const dogs: Dog[] = [{ name: "rex", bark(){ console.log("woof"); } }];
const animals: Animal[] = dogs;      // allowed: arrays are covariant
animals.push({ name: "cat" });       // allowed: pushing an Animal into an Animal[]
dogs[1].bark();                      // dogs and animals are the SAME array
```

```text
  tsc errors: none
TypeError: dogs[1].bark is not a function
```

**Zero compile errors under `--strict`, and a `TypeError` at runtime** ([`TS-VAR-03`](../MEASUREMENTS.md)).

Every individual step is permitted. `Dog[]` is assignable to `Animal[]` because arrays are covariant in their element type. Pushing an `Animal` into an `Animal[]` is obviously fine. But `animals` and `dogs` are the *same object*, so a cat is now in an array typed `Dog[]`, and reading it as a `Dog` finds no `bark`.

Arrays are **mutable**, and mutable containers cannot be soundly covariant — a sound system would make them invariant, which would reject enormous amounts of correct everyday code. TypeScript chose usability, and this is the documented price.

`ReadonlyArray<T>` *is* soundly covariant, because without `push` there is no way to introduce the bad element. Using `readonly T[]` for parameters you do not mutate is the practical mitigation, and it is worth doing for its own sake.

### 3.5 `as` is a claim, not a check

The other way to lose type safety, and the one most likely to appear in your own code.

```typescript
// Gist: claim.ts
const raw: unknown = JSON.parse('{"id":"acc_1"}');
interface Account { id: string; balance: { amount: number } }
const a = raw as Account;
console.log(a.balance.amount);
```

```text
  tsc errors: none
TypeError: Cannot read properties of undefined (reading 'amount')
```

Clean compile, runtime failure ([`TS-VAR-04`](../MEASUREMENTS.md)).

`as` does not convert, validate or check anything. It **asserts** — it tells the compiler to stop reasoning and trust you. The JSON had no `balance` field, the compiler had no way to know, and it did exactly as instructed.

This matters most at system boundaries, and it is the single largest source of runtime type errors in TypeScript codebases. `JSON.parse` returns `any`. A `fetch().json()` returns `Promise<any>`. An untyped dependency returns `any`. Every one of those is an unchecked claim about data that came from outside your program.

The correct move is `unknown` plus a parse step — a runtime validator such as Zod, or a hand-written type guard — so the type is *earned* rather than asserted. That is the subject of module 04, and it is the most consequential thing in this topic.

### 3.6 Excess property checking fires on literals only

A rule that looks like a bug until you know it is deliberate.

```typescript
// Gist: variance.ts
interface Cfg { host: string }
const c1: Cfg = { host: "x", port: 5432 };    // error
const tmp = { host: "x", port: 5432 };
const c2: Cfg = tmp;                          // no error
```

```text
variance.ts(27,30): error TS2353: Object literal may only specify known properties,
  and 'port' does not exist in type 'Cfg'.
```

The literal is rejected; the identical object via a variable is accepted ([`TS-VAR-05`](../MEASUREMENTS.md)).

Ordinary structural assignability only requires that the source have *at least* the target's members — extras are irrelevant, because anything reading it as a `Cfg` will only touch `host`. By that rule both lines should pass.

The literal case gets an extra **freshness** check, added because an object literal written directly at an assignment is almost always a typo or a misunderstanding, not intentional extra data. Once the object has been assigned to a variable it is no longer "fresh" and the normal rule applies.

The consequence to internalise: **excess property checking is not a guarantee.** Data arriving from a function, a variable, or a network response is never checked for extra properties, so it cannot be relied on to catch a shape mismatch.

### 3.7 Where inference comes from, and why it widens

Inference works from **inference sites** — the positions the compiler can read a type from — with a priority order: explicit type arguments beat contextual types, which beat inference from actual arguments.

Widening is the behaviour people trip on:

```typescript
const a = "HTG";           // type is "HTG"  — literal, because const can't be reassigned
let   b = "HTG";           // type is string — widened, because let can
const c = { cur: "HTG" };  // type is { cur: string } — the property is mutable
```

A mutable location widens a literal type to its base type, because the value could be reassigned to any other string. `as const` prevents it by making everything deeply readonly.

The modern tool is `satisfies`, which checks conformance *without* widening:

```typescript
// Gist: satisfies.ts
const routes = {
  accounts: "/api/accounts",
  transfers: "/api/transfers",
} satisfies Record<string, `/api/${string}`>;

routes.accounts;   // type is "/api/accounts" — the literal survives
```

An annotation would have widened every value to `` `/api/${string}` ``; `as const` would preserve literals but check nothing. `satisfies` does both: validates the shape and keeps the narrow inferred type. It is the right default for configuration objects.

For generics, `const` type parameters do the same job at the call site — `function f<const T>(x: T)` infers literal types from arguments without the caller writing `as const`.

### 3.8 Constraints and `infer`

A constraint does two things at once, and people usually notice only the first.

```typescript
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K>
```

`K extends keyof T` **rejects invalid keys** at the call site — the obvious job. It also **gives the return type something to be built from**, so `Pick<T, K>` describes exactly the selected subset rather than a vague object. Without the constraint, `K` has no relationship to `T` and the result cannot be expressed.

`infer` introduces a type variable bound during conditional-type matching:

```typescript
type ElementOf<T> = T extends (infer U)[] ? U : never;
type Unwrap<T>    = T extends Promise<infer U> ? U : T;
```

This is the mechanism behind the built-ins — `ReturnType`, `Parameters`, `Awaited` are all conditional types with `infer`. Being able to write `ReturnType` from scratch is a reasonable proxy for understanding conditional types:

```typescript
type MyReturnType<T> = T extends (...args: never[]) => infer R ? R : never;
```

When inference fails and a generic collapses to `unknown` or `{}`, the fix is usually structural rather than more annotations: reorder parameters so the inferable one comes first, add a constraint so the compiler has something to relate the variables through, or supply the type argument explicitly at the one call site that needs it. Annotating everything defeats the purpose of the generic.

---

## 4. Break it on purpose

### 4.1 Four unsound constructs, two errors

The §2 result, stated plainly. One file, `--strict`, four deliberate holes:

| Construct | Sound? | Caught under `--strict`? |
|---|---|---|
| Structurally identical named types interchangeable | Debatable — by design | **No** |
| Array covariance then `push` | **No** — throws at runtime | **No** |
| Method-syntax parameter bivariance | **No** | **No** (exempted deliberately) |
| Property-syntax parameter contravariance | **No** | **Yes** — via `strictFunctionTypes` |

Two of four caught, and the one that actually throws is not among them.

This is the honest characterisation of what the compiler buys you. It is enormously valuable — it catches the overwhelming majority of real mistakes — and it is **not a proof of correctness**. Treating a clean `tsc` run as a guarantee is the mistake.

### 4.2 The refactor that silently disabled a check

```text
=== strict: true ===              2 errors
=== strictFunctionTypes off ===   1 error
```

Someone adopting TypeScript on a legacy codebase turns flags off one at a time to get a clean build, planning to re-enable them later. `strictFunctionTypes` is an easy one to disable because it produces confusing errors in DOM-heavy code.

From that moment, every callback assignment in the codebase is unchecked in the direction that matters, and nothing announces it. The build is green.

The mitigation is to treat each strict sub-flag as a separate migration with its own ticket, and to turn them on **per-directory** using project references or overrides rather than globally off. Getting to strict incrementally is legitimate; getting there and quietly staying at 80% is how codebases end up with a type system they trust more than it deserves.

### 4.3 The API response that was a lie

```typescript
const account = await (await fetch(url)).json() as Account;
```

```text
TypeError: Cannot read properties of undefined (reading 'amount')
```

This one line contains the whole problem. `.json()` returns `Promise<any>`, the `as` asserts a shape nobody verified, and from that point the compiler reasons confidently about a structure that may not exist.

The failure surfaces far from the cause — at the first property access on a nested field, often several modules away — and it looks like a null-safety bug rather than a validation one. Developers then add optional chaining, which suppresses the symptom and leaves the data unvalidated.

The fix is `unknown` at the boundary and a parse step that either produces a correctly typed value or throws with a useful message. The cost is a schema per boundary type and a small runtime overhead, which is trivially worth it.

**Run this one yourself** with a deliberately wrong `as`. Watching a clean `tsc` produce a `TypeError` is what makes "the compiler checks consistency, not truth" concrete.

### 4.4 The `any` that unchecked everything downstream

```typescript
// Gist: leak.d.ts
declare module "legacy-fx" {
  export function getRate(cur: string): any;      // one `any` in a .d.ts
}
```

Every value derived from `getRate` is `any`, and `any` is contagious: it propagates through property access, arithmetic and function calls, disabling checking on every expression it touches. Three call sites later nothing is being checked and the editor still shows no errors.

`noImplicitAny` does **not** catch this — the `any` is explicit, in a file you may not own. `--strict` does not either.

The mitigations are to type the boundary yourself with a local declaration and `unknown` rather than `any`, and to use `@typescript-eslint/no-unsafe-*` rules, which flag *usage* of `any`-typed values rather than their declaration. That lint family catches what the compiler structurally cannot.

---

## 5. The judgment call

### The options, honestly costed

| Choice | Use when | Because | Real cost |
|---|---|---|---|
| **`as` assertion** | You genuinely know more than the compiler and the data is internal | Escape hatch when a guard is impossible | **No check whatsoever** — measured: clean compile, runtime `TypeError` |
| **Type guard (`x is T`)** | Narrowing a union you control | Real runtime check, and the compiler trusts it | The compiler trusts it **absolutely** — a wrong guard is a lie it can never catch |
| **Schema parse (Zod etc.)** | Any external boundary | The type is **derived from** a check that actually ran | A schema per type, and per-object runtime cost |
| **`unknown`** | Anything from outside the program | Forces narrowing before use | Slightly more code at the boundary — that is the point |
| **`readonly T[]`** | Array parameters you do not mutate | **Soundly covariant**, unlike `T[]` | Cannot pass to APIs expecting mutable arrays |
| **Property-syntax callbacks** | Interface fields holding functions | Gets contravariance checking | Method shorthand looks nicer and **skips the check** |
| **`satisfies`** | Config objects and lookup tables | Validates shape **and** keeps literal types | 4.9+; unfamiliar to reviewers |
| **Branded types** | Ids that must not be mixed | Restores nominality structurally | Construction needs a factory or a cast |

### When you would not do this

**Do not treat a clean `tsc` as a correctness proof.** §4.1 measured two of four unsound constructs passing under `--strict`, including one that throws immediately. The compiler is checking consistency with what you declared. If what you declared is a lie — via `as`, an untyped dependency, or an unvalidated response — it will reason confidently from the lie.

**Do not use `as` to silence an error.** An error is information. `as` deletes the information without changing the program. The two legitimate uses are a genuine escape hatch on data you control, and the `{} as T` accumulator idiom inside a function that provably fills it. Anywhere else it should be a guard or a parse.

**Do not disable strict sub-flags globally to get a green build.** §4.2. Migrate per-directory, one flag at a time, with the intent recorded.

**Do not write type-level programs.** Conditional and mapped types are the right tool for a utility type; recursive template-literal arithmetic is not. The costs are real and compound: error messages become unreadable, compile times degrade measurably, and the next maintainer cannot modify it. The threshold I would defend is that if the type is harder to understand than the runtime code it describes, it has failed.

**Do not rely on excess property checking.** §3.6 measured it firing on literals only. It catches typos in code you write and never checks data that arrives.

---

## 6. Interview angles

**"Is a function taking `Animal` assignable to one taking `Dog`?"**

> Yes, that direction is safe — and the reverse is not, which is the whole of variance. The reasoning is substitutability: if a caller is entitled to pass any animal, a function that handles any animal is fine, and one that only handles dogs is not, because a cat will show up and there's no `bark`. So parameters are contravariant — wider input is safe — and return types are covariant, narrower output is safe. Two things I'd add that people usually miss. First, TypeScript only checks this under `strictFunctionTypes`; I compiled a file with the unsound assignment and got a clean, specific error naming the missing property, then turned that one flag off and the error vanished while the rest of `strict` stayed on. Before 2.6 nothing caught it at all, because bivariance was what made DOM event handlers usable. Second, and this is the part that surprised me: **methods are still bivariant even under full strict.** The same unsoundness written as `handle(a: Animal): void` compiles clean, while `handle: (a: Animal) => void` is caught. That exemption exists because `Array<T>`'s methods would make arrays invariant otherwise and break the ecosystem. So the syntax you pick determines whether the check runs, which is worth knowing when you're declaring a callback field.

**"Is TypeScript's type system sound?"**

> No, deliberately, and I can give you a four-line counterexample. Assign a `Dog[]` to an `Animal[]` — allowed, arrays are covariant. Push a plain `Animal` onto it — obviously allowed. But they're the same array, so now there's a cat in something typed `Dog[]`, and calling `.bark()` on it throws. I compiled that under `--strict` and got **zero errors**, then ran it and got `TypeError: dogs[1].bark is not a function`. Mutable containers can't be soundly covariant — a sound system would make arrays invariant, which would reject a huge amount of correct everyday code, so the designers traded soundness for usability. That's a documented decision, not a bug. `ReadonlyArray` *is* soundly covariant, because without `push` there's no way to introduce the bad element, which is a good reason to use `readonly T[]` for parameters you don't mutate. The broader point I'd make is about what the compiler actually promises: internal consistency with the types you declared. Not soundness, and not validation. Which is exactly why a runtime validator at the boundary isn't optional.

**"How do you type the response from `fetch`?"**

> Not with `as`, which is the answer people expect. `.json()` returns `Promise<any>`, and writing `as Account` is a claim rather than a check — it tells the compiler to stop reasoning and trust you. I tested it: parsed a JSON object that was missing a nested field, asserted it as a type that declared the field, got a completely clean compile, and then `TypeError: Cannot read properties of undefined` at runtime. The compiler did exactly what I told it. So the shape I'd write is `unknown` at the boundary and then a parse step — Zod or an equivalent — where the type is *derived from* a check that actually ran, rather than asserted over data nobody looked at. That's a nice symmetry with Python, actually, and it's a comparison I like: Python keeps annotations at runtime, so Pydantic reads the types and builds validation from them; TypeScript erases them entirely, so Zod goes the other way and infers the type from the validator. Same destination, opposite direction of travel. The other thing I'd watch for is a single `any` in a dependency's `.d.ts`, because `any` is contagious — it propagates through every expression it touches and `noImplicitAny` won't catch it since it's explicit. The `no-unsafe-*` lint rules catch usage of `any`-typed values, which is what the compiler structurally can't do.

**"A generic collapsed to `unknown`. How do you debug it?"**

> I'd work out which inference site failed rather than start annotating, because annotating everything defeats the point of the generic. Inference has a priority order — explicit type arguments beat contextual types beat inference from arguments — so the question is which position the compiler was supposed to read the type from and why it couldn't. Usually it's one of three things. The parameter order means the inferable argument comes after the one that needs it. Or there's no constraint, so the type variable has no relationship to anything else and there's nothing to solve for — that's why `K extends keyof T` in a `pick` helper does double duty: it rejects bad keys *and* gives the return type something to build `Pick<T, K>` from. Or a literal got widened because it landed in a mutable position, in which case `as const`, a `const` type parameter, or `satisfies` fixes it. I reach for `satisfies` a lot now for config objects specifically, because an annotation widens the values and `as const` preserves them but checks nothing — `satisfies` does both, validates the shape and keeps the narrow literal types.

---

## 7. To add to `RECALL.md`

- **Parameters are contravariant** (wider input safe), **returns covariant** (narrower output safe). Derive it from substitutability
- **Measured:** the unsound callback assignment errors under `--strict` and the error **disappears** with only `strictFunctionTypes` off
- **Methods stay bivariant even under full strict** — `handle(a: Animal): void` compiles, `handle: (a: Animal) => void` is caught. Exempted so `Array<T>` stays assignable
- **Measured: array covariance — zero compile errors under `--strict`, then `TypeError: dogs[1].bark is not a function`**
- Mutable containers **cannot** be soundly covariant. `ReadonlyArray<T>` can, because there is no `push`
- **Four unsound constructs, `--strict` caught two** — and not the one that throws
- **`as` is a claim, not a check.** Measured: clean compile → `TypeError: Cannot read properties of undefined`
- A type guard `x is T` is trusted **absolutely** — a wrong guard is a lie the compiler can never catch
- The compiler promises **internal consistency with declared types**. Not soundness, not validation
- **Excess property checking fires on object literals only** (freshness). Via a variable the same object passes
- Mutable locations **widen** literal types; `as const` preserves, annotation widens, **`satisfies` checks *and* preserves**
- `K extends keyof T` does double duty: rejects bad keys **and** gives the return type something to build from
- `infer` binds a type variable during conditional matching — the mechanism behind `ReturnType`, `Parameters`, `Awaited`
- **`any` is contagious** and propagates through everything it touches; `noImplicitAny` misses an explicit `any` in a `.d.ts`. Use `no-unsafe-*` lint rules
- **Python keeps annotations at runtime → Pydantic derives validation from types. TS erases them → Zod derives types from validators.** Opposite directions

---

← [TypeScript syllabus](00_syllabus.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
