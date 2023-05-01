from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    @classmethod
    def from_orm(cls, obj: Any):
        return super().from_orm(obj)

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        orm_mode = True
        allow_population_by_field_name = True
