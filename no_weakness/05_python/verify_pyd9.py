from pydantic import BaseModel, Field, model_validator, ValidationError

class Transfer(BaseModel):
    amount: int = Field(gt=0, le=1_000_000)
    source: str
    destination: str

    @model_validator(mode="after")
    def source_and_destination_must_differ(self):
        if self.source == self.destination:
            raise ValueError("source and destination must differ")
        return self

try:
    Transfer(amount=-5, source="A", destination="A")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], err["type"], err["msg"])
print("---")
try:
    Transfer(amount=100, source="A", destination="A")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], err["type"], err["msg"])
