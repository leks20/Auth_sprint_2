from models.commons.orjson import BaseOrjsonModel
from pydantic import UUID4, Field


class Person(BaseOrjsonModel):
    id: str = Field(default_factory=UUID4)
    name: str = Field(..., alias="full_name")
