# Pydantic v2, From Zero

Every bug class that starts with "the API sent something we didn't expect" has the same root cause: JSON has no types, and Python happily passes untyped dictionaries around until something explodes three layers deep. Pydantic is the fix, and FastAPI is built on top of it. This article builds your understanding the same way you'd build a model: start with untrusted input, add guarantees one at a time.

---

## 1. The Problem: Dictionaries Don't Make Promises

Here's request handling without validation:

```python
def create_transfer(payload: dict):
    amount = payload["amount"]          # KeyError if missing
    if amount > limits[payload["tier"]]:  # TypeError if amount is the string "50"
        ...
```

Three things are wrong, and none of them are visible at this line. `amount` might be missing. It might be the *string* `"50"` because JavaScript serialized it that way. And `tier` might be `"golld"` because a mobile client has a typo. Each failure surfaces later, somewhere else, as a confusing traceback — or worse, doesn't surface at all and writes bad data.

Type hints alone don't help: `payload: dict` is checked by mypy against your *code*, but nothing checks it against *reality at runtime*. What you need is a gate: a declaration of what valid input looks like, enforced at the moment data enters, producing either a typed object or an immediate, precise error. That gate is a Pydantic model.

## 2. The First Model, and What Validation Actually Does

```bash
pip install pydantic
```

```python
# Gist: first_model.py
from pydantic import BaseModel, ValidationError

class TransferRequest(BaseModel):
    source_account: int
    destination_account: int
    amount: float
    note: str | None = None   # optional, with a default

raw = {"source_account": "17", "destination_account": 22, "amount": "150.50"}
transfer = TransferRequest(**raw)
print(transfer.source_account, transfer.amount)   # 17 150.5 — real int, real float
```

Look at what happened to `"17"` and `"150.50"`: they arrived as strings and came out as numbers. By default Pydantic runs in **lax mode** — it coerces values that are *safely convertible* to the declared type. That's usually what you want at a web boundary, where everything from query strings arrives as text anyway.

Now feed it garbage:

```python
try:
    TransferRequest(source_account="abc", amount=-5)
except ValidationError as e:
    print(e.errors())
# [{'loc': ('source_account',), 'msg': 'Input should be a valid integer', ...},
#  {'loc': ('destination_account',), 'msg': 'Field required', ...}, ...]
```

Every problem, reported at once, each with the exact field path. This structured error list is what FastAPI serializes into its 422 responses — which means when you use FastAPI, you've been using Pydantic all along; the model in your endpoint signature *is* the gate.

When coercion itself is the risk — machine-to-machine APIs where a string arriving in a numeric field means the *sender* has a bug you want exposed, not papered over — switch to **strict mode** with `model_config = ConfigDict(strict=True)`, and `"17"` becomes a validation error instead of `17`. Lax for humans and forms; strict for services. Knowing the dial exists is the point.

## 3. Constraints and Custom Rules, Added As You Need Them (How)

Types catch shape errors. Business rules need more, and Pydantic layers them on in increasing order of power. First, declarative constraints with `Field`:

```python
from pydantic import BaseModel, Field

class TransferRequest(BaseModel):
    source_account: int = Field(gt=0)
    destination_account: int = Field(gt=0)
    amount: float = Field(gt=0, le=10_000)   # positive, capped per transaction
    note: str | None = Field(None, max_length=200)
```

When a rule doesn't fit a keyword argument, write a **field validator** — a function attached to one field:

```python
from pydantic import field_validator

class TransferRequest(BaseModel):
    # ...fields as above...
    currency: str = "USD"

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        return v.strip().upper()          # " usd " becomes "USD" BEFORE type checks

    @field_validator("currency")
    @classmethod
    def currency_supported(cls, v: str) -> str:
        if v not in {"USD", "EUR", "HTG"}:
            raise ValueError(f"unsupported currency: {v}")
        return v
```

The `mode="before"` validator runs on the raw input — the right place to clean and normalize. The default (`mode="after"`) runs on the already-typed value — the right place to enforce rules. And when a rule spans *multiple* fields, use a **model validator**, which sees the whole object:

```python
from pydantic import model_validator

    @model_validator(mode="after")
    def no_self_transfer(self) -> "TransferRequest":
        if self.source_account == self.destination_account:
            raise ValueError("cannot transfer an account to itself")
        return self
```

Notice the progression you just walked: type → constraint → single-field rule → cross-field rule. That's also the order to reach for them in real code — use the least powerful tool that expresses the rule, because the declarative layers are self-documenting and appear in the generated OpenAPI schema for free.

## 4. Two Directions: Parsing In, Serializing Out

Validation is the inbound half. The outbound half is serialization — turning your typed objects back into JSON — and the friction point is naming: JavaScript clients speak `camelCase`, Python speaks `snake_case`. Aliases resolve it without either side compromising:

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class TransferOut(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    transfer_id: int
    amount: float
    created_at: datetime

out = TransferOut(transfer_id=1, amount=99.5, created_at=datetime.now())
print(out.model_dump_json(by_alias=True))
# {"transferId": 1, "amount": 99.5, "createdAt": "2026-07-19T14:02:11.183"}
```

Python code keeps `snake_case`, the wire keeps `camelCase`, and no one writes a mapping table. Notice the datetime became an ISO string on its own — serialization understands types the way validation does. When an output value is *derived* rather than stored, `@computed_field` declares it on the model (a `balance_display` formatted from `balance`, say), so the derivation lives with the schema instead of being repeated in every handler.

One more inbound tool completes the picture. Sometimes the data you're validating isn't naturally a model — it's a bare list from an external API. `TypeAdapter` runs any type annotation through the same engine: `TypeAdapter(list[TransferOut]).validate_json(raw_bytes)` type-checks a whole JSON array in one call.

## 5. Two Patterns Worth Owning: Tagged Unions and Settings

**Tagged unions.** A webhook endpoint receives several event shapes — deposits, transfers, reversals — distinguished by a `kind` field. The naive approach (one mega-model of optionals) validates nothing well. A **discriminated union** gives each shape its own model and dispatches on the tag:

```python
# Gist: tagged_events.py
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class DepositEvent(BaseModel):
    kind: Literal["deposit"]
    amount: float = Field(gt=0)

class TransferEvent(BaseModel):
    kind: Literal["transfer"]
    amount: float = Field(gt=0)
    destination_account: int

Event = Annotated[Union[DepositEvent, TransferEvent], Field(discriminator="kind")]
```

Pydantic reads `kind` first, picks the one matching model, and validates against it alone — so errors say what's wrong with a *transfer*, not a wall of failures from every branch. In FastAPI, annotating a body as `Event` renders a proper `oneOf` in the OpenAPI schema. (The same idea exists on the frontend as `z.discriminatedUnion` — [08_zod_formik.md](08_zod_formik.md).)

**Settings.** Configuration is also untrusted input — it arrives from the environment, and a missing `DATABASE_URL` should fail loudly at startup, not at the first query twenty minutes into traffic. `pydantic-settings` runs env vars through the same validation engine:

```python
# Gist: settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str            # required: the app refuses to boot without it
    pool_size: int = 10          # env string "10" coerced to int
    debug: bool = False          # "true"/"1"/"yes" all coerce correctly

settings = Settings()  # reads from environment (and .env in dev)
```

This is the 12-factor config pattern ([04/03](../04_architecture_and_system_design/03_twelve_factor_config.md)) with types on: wrong-shaped config is a crash at boot with a named field, which is the cheapest possible place to fail.

## 6. The Philosophy, Stated Once

Everything above is one idea applied repeatedly: **validate at the boundary, then trust.** Request bodies, webhook payloads, external API responses, environment variables — each crosses from "outside" to "inside" exactly once, through a model. Inside, functions take `TransferRequest`, not `dict`, and never re-check. This is why Pydantic v2's speed matters (its core is compiled Rust — validation is cheap enough to afford at every boundary), and why models double as documentation: the schema *is* the contract, and FastAPI publishing it as OpenAPI is what lets the frontend generate matching types ([06/02](../06_testing_and_migrations/02_test_pyramid_mocking_contracts.md)).

## 7. Interview Angles

**"Where should validation live in a layered application?"** At the edges, once, in both directions — request models inbound (so handlers never see malformed data) and response models outbound (which also filter: fields not in the schema can't leak). If you find re-validation deep in the service layer, the boundary has a hole; fix the boundary rather than sprinkling checks.

**"Lax or strict mode, and why?"** Lax for human-facing input, where `"150.50"` for a float is normal life; strict for service-to-service payloads, where a wrong type means the *sender* is broken and silent coercion would hide their bug. The mature answer names it per-boundary rather than picking one globally.

**"How do you handle an endpoint that accepts multiple payload shapes?"** A discriminated union: one model per shape, dispatched on a literal tag field. It buys precise errors, exhaustive handling downstream (the type checker knows every variant), and an honest `oneOf` in the OpenAPI schema — versus the optionals-mega-model, which validates nothing and documents less.
