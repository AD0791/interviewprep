from pydantic import BaseModel, Field, ValidationError

class Strict(BaseModel):
    amount: int = Field(strict=True)

try:
    Strict(amount="500")
except ValidationError as e:
    print(e.errors()[0]["type"], e.errors()[0]["msg"])

print(Strict(amount=500))
