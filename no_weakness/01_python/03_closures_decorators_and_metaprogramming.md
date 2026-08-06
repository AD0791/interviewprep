# Closures, decorators, and metaprogramming

*Cells, the three-level nesting, and the four tools that all do the same job at different prices.*

**Level:** L4–L5 · **Prerequisites:** [`01` the object model](01_object_model_and_attribute_lookup.md)
**Syllabus:** [`PY-12`–`PY-17`](00_syllabus.md) · **Roles:** DE ● FS ●
**Measurement:** `Measured` — CPython 3.14.6, arm64, 8 cores, macOS 26.5.2. Every output below came out of a terminal on this machine. Claims about SQLAlchemy's and Pydantic's internals are tagged `documented` inline; neither is installed here and I did not read their source.

---

## 1. The thing you already do

You have written this decorator, or something close enough:

```python
# Gist: deps.py
def require_role(role: str):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, current_user: User, **kwargs):
            if current_user.role != role:
                raise HTTPException(403, "forbidden")
            return await fn(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


@router.post("/accounts/{account_id}/transfer")
@require_role("teller")
async def transfer(account_id: int, amount: float, current_user: User = Depends(auth)):
    ...
```

And you have written this model, which is the same machinery from the other side:

```python
# Gist: models.py
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(120))
    balance_cents: Mapped[int] = mapped_column(default=0)
```

The second one should bother you more than the first. There is no `__init__` in that class, yet `Account(owner="alexandro")` works. There is no code that reads `__tablename__`, yet the table gets named. The annotations — `Mapped[int]` — are doing something, even though annotations are supposed to be inert. Something ran at the moment the `class` statement executed and rewired the class before you ever instantiated it.

That something is metaprogramming, and the decorator above is the entry-level version of it. Both are built from the same three ideas: functions that capture their environment, functions that take functions, and hooks that fire while a class is being built.

---

## 2. The questions you cannot answer about it

**What does `functools.wraps` actually restore?** You add it because the docs say to, or because a linter complains. Name the attributes it copies. Then name what breaks without it in a FastAPI application specifically — because the answer is not "the function name looks wrong in a traceback," it is considerably worse than that.

**Why three levels of nesting for a decorator with arguments?** You have written the pattern. Explain why `@retry(times=3)` needs `def retry` → `def decorator` → `def wrapper` while `@retry` needs only two. The `@` symbol applies exactly one thing; knowing what it applies is the whole answer.

**Have you ever written a metaclass?** Almost certainly not. But two of them are running in the code you wrote this month, and being able to say which — and why the library authors chose that over the alternatives — is the difference between using a framework and understanding it.

**And the one that should bother you.** Write the same three-line decorator twice, once with `functools.wraps` and once without. Ask each version for its type annotations:

```text
  type hints via naive:  {}
  type hints via proper: {'from_id': <class 'int'>, 'to_id': <class 'int'>, ...}
```

The naive decorator did not merely lose a cosmetic name. **It erased the type information that FastAPI uses to build the route, parse the request body, and generate the OpenAPI schema.** A missing one-line import silently turns a typed endpoint into an untyped one.

If you can answer all four cleanly, go to §6 and rehearse. Otherwise, section 3.

---

## 3. What the machine actually does

### 3.1 The analogy: a cell is a shared mailbox

Here is the image to carry. When an inner function refers to a variable from an enclosing scope, Python does not hand it a copy of the value. It gives both functions a key to the same **mailbox** — a `cell` object. The outer function can drop new contents in; the inner function reads whatever is in there *at the moment it looks*, not what was there when it was handed the key.

Nearly every closure bug in Python is someone assuming they were given a photograph when they were given a mailbox key.

### 3.2 Closures are cells, and you can look inside them

The compiler decides at compile time which variables are free. If an inner function references a name from an enclosing function, that name becomes a **cell variable**, and the inner function object carries a tuple of cells in `__closure__`.

```python
# Gist: c1_closures.py
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
print("  c.__closure__      =", c.__closure__)
print("  cell contents      =", c.__closure__[0].cell_contents)
c(); c()
print("  after two calls    =", c.__closure__[0].cell_contents)
print("  co_freevars        =", c.__code__.co_freevars)
```

```text
  c.__closure__      = (<cell at 0x10550e230: int object at 0x1050d0888>,)
  cell contents      = 0
  after two calls    = 2
  co_freevars        = ('count',)
```

Three things worth reading carefully ([`PY-CLO-01`](../MEASUREMENTS.md)).

`__closure__` is a real, inspectable tuple of cell objects — closures are not a compiler abstraction, they are data you can print. `co_freevars` on the code object shows the compiler recorded `count` as free *at compile time*, before the function ever ran. And the cell's contents changed from 0 to 2 as the function was called, which proves the cell holds a live reference rather than a snapshot.

`nonlocal` is what permits the *write*. Without it, `count += 1` would treat `count` as local to `increment`, and you would get `UnboundLocalError` — because assignment anywhere in a function body makes the name local for the whole body, which is a rule that catches people who only ever read from the enclosing scope and then add one assignment.

### 3.3 The late-binding bug, and why two different fixes work

Now the consequence. One mailbox, many keys.

```python
# Gist: c1_closures.py (part 2)
bad = [lambda: i for i in range(3)]
print("  [f() for f in bad]           =", [f() for f in bad])
print("  same cell object in all 3?   =",
      bad[0].__closure__[0] is bad[1].__closure__[0] is bad[2].__closure__[0])

good = [lambda i=i: i for i in range(3)]
print("  default-arg fix              =", [f() for f in good])
print("  good[0].__closure__          =", good[0].__closure__, " <- no closure at all")
print("  good[0].__defaults__         =", good[0].__defaults__)

good2 = [(lambda x: lambda: x)(i) for i in range(3)]
print("  factory fix                  =", [f() for f in good2])
print("  distinct cells now?          =",
      good2[0].__closure__[0] is not good2[1].__closure__[0])
```

```text
  [f() for f in bad]           = [2, 2, 2]
  same cell object in all 3?   = True
  default-arg fix              = [0, 1, 2]
  good[0].__closure__          = None  <- no closure at all
  good[0].__defaults__         = (0,)
  factory fix                  = [0, 1, 2]
  distinct cells now?          = True
```

`[2, 2, 2]` is the classic, and the second line explains it without ambiguity: **all three functions hold the identical cell object**, so all three see whatever the loop variable ended at ([`PY-CLO-02`](../MEASUREMENTS.md)).

The two fixes are genuinely different mechanisms, and knowing which one you reached for matters.

The default-argument fix works by **not making a closure at all**. `good[0].__closure__` is `None` — there is no cell, no free variable, nothing captured. The value was evaluated at function-definition time and stored in `__defaults__`. It is a snapshot precisely because defaults are evaluated once, at `def` time, which is the same rule that produces the famous mutable-default-argument bug. The same mechanism causes one bug and cures another.

The factory fix works by **making three separate cells**. Each call to the outer lambda creates a fresh frame with its own `x`, so each inner lambda gets its own mailbox — confirmed by the final line.

Prefer the factory when the value should be genuinely private, and the default argument when brevity matters and you can accept that a caller could override it by passing the parameter.

### 3.4 A decorator is function application with syntax

`@decorator` above a `def` means exactly one thing: after the function is created, rebind the name to `decorator(function)`. That is all.

Which is why arguments require a third level. `@retry(times=3)` is not "apply `retry` with an extra argument" — the `@` applies whatever expression follows it, and `retry(times=3)` is a **call** that must therefore *return a decorator*.

```python
# Gist: c2_wraps.py (part 2)
def retry(times=3):                       # 1. takes the args
    def decorator(fn):                    # 2. takes the function
        @functools.wraps(fn)
        def wrapper(*a, **kw):            # 3. takes the call
            for attempt in range(1, times + 1):
                try:
                    return fn(*a, **kw)
                except ValueError as e:
                    print(f"    attempt {attempt} failed: {e}")
            raise RuntimeError(f"all {times} attempts failed")
        return wrapper
    return decorator

calls = {'n': 0}

@retry(times=3)
def flaky():
    calls['n'] += 1
    if calls['n'] < 3: raise ValueError(f"boom {calls['n']}")
    return "ok"

print("  flaky() ->", flaky())
```

```text
    attempt 1 failed: boom 1
    attempt 2 failed: boom 2
  flaky() -> ok
```

Each level has exactly one job and they are easy to name: the outer takes the configuration, the middle takes the function, the inner takes the call. Note also that `times` is reached from `wrapper` through a closure cell — the retry decorator is the mailbox mechanism from §3.2 doing production work.

### 3.5 What `functools.wraps` restores, and the FastAPI consequence

A wrapper is a different function object from the one it wraps. It has its own name, its own docstring, and — critically — **its own signature**. `functools.wraps` copies the identity across.

```python
# Gist: c2_wraps.py
def naive(fn):
    def wrapper(*a, **kw): return fn(*a, **kw)
    return wrapper

def proper(fn):
    @functools.wraps(fn)
    def wrapper(*a, **kw): return fn(*a, **kw)
    return wrapper

def transfer(from_id: int, to_id: int, amount: float = 0.0) -> bool:
    """Move money between two accounts."""
    return True

n, p = naive(transfer), proper(transfer)
```

```text
                     naive            proper
  __name__     wrapper          transfer
  __doc__      None             Move money between t
  __module__   __main__         __main__
  __qualname__ naive.<locals>.  transfer
  signature    (*a, **kw)       (from_id: int, to_id: int, amount: float
  __wrapped__  False            True

  type hints via naive: {}
  type hints via proper: {'from_id': <class 'int'>, 'to_id': <class 'int'>, 'amount': <class 'float'>, 'return': <class 'bool'>}
```

The first four rows are cosmetic — better tracebacks, working `help()`. The last three are not ([`PY-CLO-03`](../MEASUREMENTS.md)).

`inspect.signature` reports `(*a, **kw)` for the naive version. `inspect.get_annotations` returns an **empty dictionary**. Every type annotation on the original function is gone.

Now recall what FastAPI does with a route handler. It reads the signature to determine which parameters come from the path, which from the query string, and which from the request body. It reads the annotations to know how to parse and validate each one, and to generate the OpenAPI schema. Hand it `(*a, **kw)` with no annotations and it has nothing to work with — the endpoint either fails to register correctly or silently accepts unvalidated input.

`functools.wraps` restores this because it sets `__wrapped__` to the original function, and `inspect.signature` follows `__wrapped__` by default. That single attribute is what makes introspection see through the wrapper.

The rule: **any decorator applied to a function a framework will introspect must use `functools.wraps`.** That covers FastAPI routes, Pydantic validators, pytest fixtures, Click commands, and Celery tasks.

### 3.6 The class-creation hooks, in the order they actually fire

Executing a `class` statement is a multi-stage process with several hooks. Instrumenting all of them at once settles the ordering questions permanently:

```python
# Gist: c3_meta.py
class Tracked:
    def __set_name__(self, owner, name):
        print(f"    3. __set_name__     -> {owner.__name__}.{name}")
        self.name = name
    def __get__(self, obj, t=None): return self if obj is None else obj.__dict__.get(self.name)
    def __set__(self, obj, v): obj.__dict__[self.name] = v

class Meta(type):
    def __new__(mcls, name, bases, ns, **kw):
        print(f"    1. Meta.__new__     -> building {name}, namespace keys={[k for k in ns if not k.startswith('__')]}")
        return super().__new__(mcls, name, bases, ns, **kw)
    def __init__(cls, name, bases, ns, **kw):
        print(f"    4. Meta.__init__    -> {name} fully built")
        super().__init__(name, bases, ns, **kw)
    def __call__(cls, *a, **kw):
        print(f"    5. Meta.__call__    -> instantiating {cls.__name__}")
        return super().__call__(*a, **kw)

class Base(metaclass=Meta):
    def __init_subclass__(cls, **kw):
        print(f"    2b. __init_subclass__ -> {cls.__name__}")
        super().__init_subclass__(**kw)

class Account(Base):
    balance = Tracked()

a = Account()
a.balance = 500
```

```text
    1. Meta.__new__     -> building Base, namespace keys=[]
    4. Meta.__init__    -> Base fully built
  Defining Account(Base):
    1. Meta.__new__     -> building Account, namespace keys=['balance']
    3. __set_name__     -> Account.balance
    2b. __init_subclass__ -> Account
    4. Meta.__init__    -> Account fully built

  Instantiating:
    5. Meta.__call__    -> instantiating Account
  a.balance = 500
```

Read the ordering ([`PY-CLO-04`](../MEASUREMENTS.md)). The metaclass's `__new__` runs **first**, and it receives the class body as an ordinary dictionary before the class object exists — which is what lets a metaclass inspect, rewrite, or reject what was written in the body. Then `__set_name__` fires on every descriptor, then `__init_subclass__` on the parent, then the metaclass's `__init__`. Instantiation later goes through the metaclass's `__call__`, which is the hook that makes singletons and instance caching possible.

The important detail for §5's argument: **`__set_name__` fires before `__init_subclass__`**, so by the time a parent class gets to react to a new subclass, every descriptor in that subclass already knows its own name.

This ordering is the mechanism behind the SQLAlchemy model in §1. The metaclass receives a namespace containing `id`, `owner` and `balance_cents`, collects the ones that are `mapped_column` objects, reads the `Mapped[...]` annotations to determine column types, builds a table definition, and generates an `__init__`. That is why a class with no constructor accepts keyword arguments. *(`documented` — SQLAlchemy is not installed here; I did not read its source. The mechanism is metaclass-plus-descriptor, and the reconstruction above shows the same machinery working.)* Pydantic's model machinery does the equivalent, reading annotations to build validators.

---

## 4. Break it on purpose

### 4.1 The decorator that erased the API contract

The §2 result, now as a failure with consequences.

```python
# Gist: broken_route.py
def log_calls(fn):                        # no functools.wraps
    def wrapper(*a, **kw):
        print(f"calling {fn.__name__}")
        return fn(*a, **kw)
    return wrapper

@log_calls
def transfer(from_id: int, to_id: int, amount: float = 0.0) -> bool:
    """Move money between two accounts."""
    return True

print(inspect.signature(transfer))
print(inspect.get_annotations(transfer))
```

```text
  signature    (*a, **kw)
  type hints via naive: {}
```

Nothing raised. The function still works when called directly. Tests that invoke `transfer(1, 2, 50.0)` all pass.

But a framework that introspects this function sees a callable taking arbitrary arguments with no types. In FastAPI that means the route's parameters, validation and OpenAPI schema are built from nothing. The failure surfaces as a 422 on a request that should be valid, or worse, as an endpoint that accepts anything.

The fix is one line — `@functools.wraps(fn)` on the wrapper — and the cost is nothing. This is a defect with no trade-off.

**Run this one yourself.** The reason to feel it rather than read it is that the symptom appears nowhere near the cause: you will be looking at a request-parsing error while the bug is in a logging decorator someone added three files away.

### 4.2 The mutable default argument, which is the same mechanism

§3.3 used default arguments as a *fix*. Here is the identical rule causing the language's most notorious bug.

```python
# Gist: mutable_default.py
def add_transaction(amount, ledger=[]):
    ledger.append(amount)
    return ledger

print(add_transaction(100))
print(add_transaction(200))
print(add_transaction(300))
print("__defaults__ is:", add_transaction.__defaults__)
```

```text
[100]
[100, 200]
[100, 200, 300]
__defaults__ is: ([100, 200, 300],)
```

Three independent calls, and the ledger accumulated across all of them. The last line shows why: `__defaults__` holds **one list object**, created once when the `def` executed, and every call that omits the argument gets that same object.

This is exactly the property that made `lambda i=i: i` work in §3.3 — defaults are evaluated once at definition time. There, evaluating once was the point. Here, it is the bug. The mechanism did not change; only whether the value is immutable did.

The fix is `ledger=None` with `if ledger is None: ledger = []` inside. The cost is two extra lines and one branch, and it is not negotiable for any mutable default.

### 4.3 Two metaclasses, one class, no way forward

This is the failure that decides the tool-choice argument in §5.

```python
# Gist: c3_meta.py (part 3)
class MetaA(type): pass
class MetaB(type): pass
class A(metaclass=MetaA): pass
class B(metaclass=MetaB): pass
class C(A, B): pass
```

```text
  TypeError: metaclass conflict: the metaclass of a derived class must be a
  (non-strict) subclass of the metaclasses of all its bases
```

`A` and `B` are perfectly good classes. Combining them is impossible ([`PY-CLO-06`](../MEASUREMENTS.md)).

There is no fix available to the person writing `class C(A, B)`. The only resolution is to construct a new metaclass inheriting from both `MetaA` and `MetaB` — which requires the authority to change one of the libraries, and is why combining two frameworks that each use a metaclass can be flatly impossible rather than merely awkward.

This is the strongest practical argument against metaclasses in library code. A metaclass is not a local decision: it constrains every future user of your class in ways they cannot work around. `__init_subclass__` composes cleanly through `super()` and has no equivalent failure.

### 4.4 The decorator that broke the method

Applying a function decorator to a method looks like it works, right up until it does not.

```python
# Gist: broken_method.py
import functools

def cache_it(fn):
    store = {}
    @functools.wraps(fn)
    def wrapper(*args):
        if args not in store:
            store[args] = fn(*args)
        return store[args]
    return wrapper

class Account:
    def __init__(self, owner): self.owner = owner
    @cache_it
    def slow_balance(self): return f"balance for {self.owner}"

a, b = Account("alexandro"), Account("someone else")
print(a.slow_balance())
print(b.slow_balance())
```

```text
balance for alexandro
balance for someone else
entries retained in the decorator's dict: 2
after `del a` + gc.collect(), entries still retained: 2
-> the instance cannot be collected; the cache is holding it
```

This one *works* — and that is what makes it dangerous. The cache key is `args`, which includes `self`, so different instances get different entries. Correct by accident.

The last two lines are the leak proved rather than asserted ([`PY-CLO-07`](../MEASUREMENTS.md)). After `del a` and a forced `gc.collect()`, the entry is still in the dictionary — so the `Account` object cannot be collected, because `store` holds a strong reference to it as part of the cache key. `store` lives as long as the class does. **Every `Account` instance that ever called `slow_balance` is immortal.** In a long-running service that is an unbounded leak whose retainer path leads back to a decorator nobody suspects.

`functools.lru_cache` on a method has exactly this problem, and it is the reason `functools.cached_property` exists — it stores the computed value in the *instance's* `__dict__`, so it dies with the instance. The general fix is to key the cache on something other than the object, or to store per-instance rather than in a decorator-level dictionary.

The cost of `cached_property`: it requires the class to have a `__dict__`, so it is incompatible with `__slots__` unless `__dict__` is declared — which links directly back to [module 01's `__slots__` discussion](01_object_model_and_attribute_lookup.md).

---

## 5. The judgment call

### The options, honestly costed

Four tools, one job: react to or modify a class. Ordered cheapest first.

| Tool | Use when | Because | Real cost |
|---|---|---|---|
| **Function decorator** | Wrapping behaviour around a callable | Simplest thing that works; composes freely | Breaks introspection without `wraps`; stacking order is bottom-up and easy to get wrong |
| **Class decorator** | Modifying or registering **one specific class** | Explicit at the point of use — a reader sees it on the class | Does not apply to subclasses; must be repeated on each |
| **`__init_subclass__`** | Every subclass must register, validate, or be configured | Automatic, inherited, composes through `super()`, accepts class keyword arguments | Cannot alter the namespace *during* construction — it runs after the class exists |
| **`__set_name__`** | A descriptor needs to know its own attribute name | Fires automatically at class creation; removes the repeated-name boilerplate | Only useful on descriptors |
| **Metaclass** | You must control class **construction** — rewrite the namespace, alter bases, change the type | The only hook that runs before the class object exists | **Metaclass conflicts make your class uncombinable** (§4.3); raises the bar for every future maintainer |

### When you would not do this

**Do not write a metaclass.** That is close to an absolute rule for application code, and §4.3 is why: it is not a local decision. A metaclass propagates to every subclass and collides with any other metaclass in the hierarchy, and the person who hits that `TypeError` is usually not the person who chose it. The exceptions are real but narrow — SQLAlchemy and Pydantic need to read the class body and rewrite it before the class exists, which nothing else can do, and they are libraries whose entire purpose justifies the cost. If you are reaching for one, try `__init_subclass__` first; it covers registration, validation and configuration, which is most of what metaclasses get used for.

**Do not decorate what you have not thought about caching.** §4.4 shows a cache decorator quietly making every instance immortal. Any decorator holding a dictionary at module level is a memory retainer, and the question "what keeps this key alive?" has to be answered before it ships. `cached_property` where you want per-instance, an explicit bounded cache where you want shared.

**Do not use closures where a class is clearer.** A closure over mutable state and a small class with one method are the same thing; the class has a name, a docstring, and a place to put a second method later. The counter in §3.2 is fine as a closure. Anything with three captured variables and two returned functions has become an object with extra steps, and `nonlocal` in more than one place is the signal.

**Be careful stacking decorators.** They apply bottom-up — the one nearest the `def` runs first — and in the `@router.post` / `@require_role` pair from §1 the order is load-bearing. Register the route with the *wrapped* function, not the raw one, or the authorisation check never runs. This is the one place where getting the order wrong produces a security hole rather than a crash, and it is worth a comment in the code.

---

## 6. Interview angles

**"Why do you need `functools.wraps`?"**

> Most people say it preserves the function name for tracebacks, and that's true but it's the least important part. What it actually does is copy `__name__`, `__doc__`, `__module__`, `__qualname__` and `__dict__`, and — the one that matters — set `__wrapped__` to the original function. `inspect.signature` follows `__wrapped__`, so that attribute is what makes introspection see through the wrapper. I checked this rather than trusting it: a naive decorator reports its signature as `(*a, **kw)` and `inspect.get_annotations` on it returns an empty dict. Every type hint is gone. And that's the real consequence, because FastAPI builds the route from the signature and the annotations — which parameters are path versus query versus body, how to validate them, what the OpenAPI schema looks like. So a logging decorator without `wraps` doesn't make your traceback uglier, it silently strips the API contract off the endpoint. Nothing raises, the tests pass because they call the function directly, and it shows up as a 422 on a request that should be valid.

**"Have you ever written a metaclass?"**

> No, and I'd rather say that plainly than pretend. I've never had a problem that needed one. But I can tell you what they do and I've built small ones to make sure I actually understood the ordering. A class statement runs the body into a namespace dict, hands it to the metaclass's `__new__`, and that's the only hook that runs *before* the class object exists — so it's the only place you can inspect or rewrite what was written in the body. I instrumented all the hooks at once to get the sequence straight: metaclass `__new__`, then `__set_name__` on every descriptor, then `__init_subclass__` on the parent, then metaclass `__init__`, and `__call__` later at instantiation. That's what SQLAlchemy's declarative base is doing when a model class with no `__init__` somehow accepts keyword arguments, and Pydantic does the same shape of thing reading annotations to build validators — though I should flag I'm going on documentation for those two specifically rather than having read the source. The part I'd actually argue in a design review is that you usually shouldn't. I reproduced the metaclass conflict — two independent classes with different metaclasses simply cannot be combined, you get a `TypeError` and the person hitting it has no fix available unless they can edit one of the libraries. `__init_subclass__` composes through `super()` and has no equivalent failure, so it's my default for anything that's reacting to class creation rather than controlling it.

**"Explain the classic loop-closure bug and how you'd fix it."**

> The one where you build a list of lambdas in a loop and they all return the last value. The reason is that a closure captures a *cell*, not a value — I like thinking of it as a shared mailbox rather than a photograph. I printed the cells to confirm it: all three functions hold the identical cell object, `is` comparison returns True, so of course they all see whatever the loop variable ended at. There are two fixes and they work by completely different mechanisms, which I think is the interesting part. The default-argument version, `lambda i=i: i`, works by not creating a closure at all — `__closure__` is literally `None` and the value sits in `__defaults__`, because defaults are evaluated once at definition time. The factory version, calling an outer lambda that returns an inner one, creates a genuinely separate cell per iteration. And the thing I find neat is that the default-argument rule — evaluated once at `def` time — is the exact same rule that causes the mutable default argument bug. Same mechanism, and whether it's a fix or a bug depends only on whether the value is mutable. If it's a private value I want nobody able to override, I use the factory; otherwise the default argument is shorter.

**"You've got a memory leak in a long-running Python service. Walk me through it."**

> I'd want the retainer path, not the allocation site — `tracemalloc` tells you where the memory was allocated, which is often not where the bug is. What I'm looking for is what's holding a reference that should have been dropped. And decorators are a place I've learned to check early, because a decorator that keeps a dictionary at module scope holds strong references for the lifetime of the process. I built the case to see it clearly: a caching decorator on a method, keyed on `args`, which includes `self`. It's *correct* — different instances get different cache entries — and that's what makes it nasty, there's no wrong behaviour to notice. But every instance that ever called that method is now immortal, because the module-level dict holds it. That's exactly why `functools.cached_property` exists rather than putting `lru_cache` on methods: it stores the value in the instance's own `__dict__` so it dies with the instance. The trade-off there is it needs the class to have a `__dict__`, so it doesn't work with `__slots__` unless you declare one. The general question I'd ask about any cache is "what keeps this key alive," and if the answer is "the cache does," that's the leak.

---

## 7. To add to `RECALL.md`

- A closure captures a **cell, not a value** — `f.__closure__` is a real tuple you can print; `cell_contents` changes as the outer variable changes
- `co_freevars` shows the compiler decided which names are free **at compile time**
- `nonlocal` permits the *write*; without it any assignment makes the name local for the whole body → `UnboundLocalError`
- Loop-closure bug: **all closures share one cell** (`is` returns True), so they see the final value → `[2, 2, 2]`
- Fix A, default arg: **creates no closure at all** — `__closure__` is `None`, value lives in `__defaults__`
- Fix B, factory: creates **distinct cells** per iteration
- **Same rule, opposite outcome:** defaults evaluated once at `def` time is the fix in A *and* the mutable-default bug
- `@` applies **exactly one** expression; `@retry(times=3)` is a call whose return value decorates — hence three levels: args → function → call
- `functools.wraps` copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__dict__`, and sets **`__wrapped__`**, which `inspect.signature` follows
- **Without `wraps`: signature becomes `(*a, **kw)` and `get_annotations` returns `{}`** — FastAPI loses parameters, validation and the OpenAPI schema
- Class-creation order: **metaclass `__new__` → `__set_name__` → `__init_subclass__` → metaclass `__init__` → `__call__`** at instantiation
- Only metaclass `__new__` runs **before the class exists**, so only it can rewrite the namespace
- **Metaclass conflict:** two classes with different metaclasses cannot be combined — `TypeError`, and no fix available to the caller
- Prefer `__init_subclass__` (composes via `super()`) and `__set_name__`; reserve metaclasses for controlling *construction*
- A module-level cache in a decorator keyed on `self` makes **every instance immortal** — that is why `cached_property` exists
- Decorators stack **bottom-up**; with `@router.post` above `@require_role`, wrong order means the auth check never runs

---

← [Python syllabus](00_syllabus.md) · [repo index](../README.md) · [measurement ledger](../MEASUREMENTS.md)
