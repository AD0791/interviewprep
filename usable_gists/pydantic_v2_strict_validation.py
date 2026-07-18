# Use Case: Production Pydantic v2 Schema Setup
# Purpose: Validates complex nested schemas, runs strict mode checks, and formats JSON outputs.
# Key features: Pydantic v2 strict configuration, field validators, model-level validation, and serialization formatting.

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

class UserAddress(BaseModel):
    street: str
    city: str
    postal_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")  # Enforces ZIP pattern

class UserRegistrationSchema(BaseModel):
    # Enforces strict mode globally (fails immediately if strings are passed as integers, etc.)
    model_config = {"strict": True, "populate_by_name": True}

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    access_key: str = Field(..., alias="accessKey")  # Maps camelCase incoming JSON to snake_case
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    address: Optional[UserAddress] = None
    created_at: Optional[datetime] = None

    # Before field validator: Strip whitespaces before standard type validations run
    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    # After field validator: Run validation on parsed types
    @field_validator("password", mode="after")
    @classmethod
    def verify_password_complexity(cls, v: str) -> str:
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(char in special_chars for char in v):
            raise ValueError("Password must contain at least one special character")
        return v

    # Model-level validator: Cross-compare fields after all fields resolve
    @model_validator(mode="after")
    def verify_password_match(self) -> "UserRegistrationSchema":
        if self.password != self.confirm_password:
            raise ValueError("password and confirm_password must match")
        return self
