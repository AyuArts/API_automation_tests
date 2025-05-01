from pydantic import BaseModel, Field


class TextErrors(BaseModel):
    none: str = "can't be blank"

    @property
    def too_long(self, count: int = 200):
        return f"is too long (maximum is {count} characters)"

    is_invalid: str = "is invalid"


class Errors(BaseModel):
    text: TextErrors = Field(default_factory=TextErrors)
