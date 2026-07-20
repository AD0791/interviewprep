# Pydantic v2 validation Specification (Comprehensive Masterclass)

Pydantic (v2.12+ stable in 2026) is Python's leading data validation and serialization library. Pydantic v2 represents a complete rewrite in Rust, offering massive performance gains, full compatibility with Python 3.14 type annotations, and a redesigned validation API.

---

## 1. Core Validation Mechanics (Why & What)

### Why Use Pydantic?
FastAPI uses Pydantic to parse and validate incoming JSON payloads. It maps strings to integers, parses ISO date strings to datetime objects, and converts dictionaries to typed class objects.
* **Lax vs. Strict Validation Mode**:
  * **Lax Mode (Default)**: Pydantic attempts to coerce data to match the target type (e.g. converting the string `"123"` to the integer `123`, or `"true"` to the boolean `True`).
  * **Strict Mode**: Pydantic does not perform data coercion, raising a validation error if types do not match exactly. Enforcing strict mode prevents bugs caused by accidental type conversions.

### Model Configurations & Aliases
Web frameworks often accept API payloads using camelCase (`transactionAmount`), but Python style guides (PEP-8) dictate using snake_case variables (`transaction_amount`). Pydantic handles this mismatch using field aliases and serialization mappings.

---

## 2. Basic Validation & Field Constraints (How)

### Declaring Basic Models
Set constraints using the `Field` helper to enforce bounds and pattern matching on input parameters.

```python
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class UserProfile(BaseModel):
    # Enforce type checking strictly, allowing serialization using aliases
    model_config = {
        "strict": True,
        "populate_by_name": True  # Allows instantiating model using snake_case or alias key
    }

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Built-in RFC validation
    age: int = Field(..., ge=18, le=120)  # Must be >= 18 and <= 120
    postal_code: str = Field(..., pattern=r"^\d{5}$")  # Exact 5 digit regex pattern
    company_name: Optional[str] = Field(None, alias="companyName")
```

---

## 3. Advanced Custom Validation & Serialization (How)

### Gist: advanced_pydantic_validation.py
Demonstrates field validators, model validators, aliases mapping, and serialization outputs.

```python
# Gist: advanced_pydantic_validation.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, field_serializer

class TransactionRequest(BaseModel):
    model_config = {
        "strict": True,
        "populate_by_name": True
    }

    account_id: int = Field(..., alias="accountId")
    amount: float = Field(..., gt=0.0)
    transaction_type: str = Field(..., alias="transactionType")
    signature: str
    timestamp: Optional[datetime] = None

    # 1. FIELD VALIDATOR (mode='before')
    # Why: Cleans up input strings before standard type-checking runs
    @field_validator("transaction_type", mode="before")
    @classmethod
    def clean_transaction_type(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    # 2. FIELD VALIDATOR (mode='after')
    # Why: Runs validation checks on the resolved type
    @field_validator("transaction_type", mode="after")
    @classmethod
    def validate_type_options(cls, v: str) -> str:
        options = ["deposit", "withdrawal"]
        if v not in options:
            raise ValueError(f"transactionType must be one of: {options}")
        return v

    # 3. MODEL VALIDATOR (mode='after')
    # Why: Cross-compares multiple fields after all fields resolve
    @model_validator(mode="after")
    def verify_withdrawal_limits(self) -> "TransactionRequest":
        if self.transaction_type == "withdrawal" and self.amount > 10000.0:
            raise ValueError("Withdrawals cannot exceed $10,000 in a single transaction")
        return self

    # 4. CUSTOM FIELD SERIALIZER
    # Why: Formats output data structures during serialization (model.model_dump())
    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: Optional[datetime]) -> Optional[str]:
        if dt:
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return None

# Usage & Testing
try:
    # Invalid amount validation test
    tx = TransactionRequest(
        accountId=101,
        amount=-5.0,
        transactionType=" Deposit ",
        signature="sha256hash"
    )
except Exception as e:
    # e.errors() returns a structured list of validation errors
    print("Validation failed:", e)

# Valid instance mapping using camelCase input keys
valid_tx = TransactionRequest(
    accountId=101,
    amount=250.0,
    transactionType=" deposit ", # gets cleaned to "deposit"
    signature="sha256hash",
    timestamp=datetime.utcnow()
)

print(valid_tx.model_dump_json(by_alias=True))
# Returns: {"accountId": 101, "amount": 250.0, "transactionType": "deposit", ...}
```
