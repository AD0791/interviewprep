from pydantic import BaseModel, ValidationError

class Flag(BaseModel):
    active: bool

for v in ["true", "yes", "1", "on", "0", "false", 1, 0]:
    try:
        print(repr(v), "->", Flag(active=v).active)
    except ValidationError as e:
        print(repr(v), "-> ValidationError")
