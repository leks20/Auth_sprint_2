from functools import lru_cache

import orjson
from aioredis import Redis
from api.common.elastic import get_body, get_pagination
from core.config import settings
from db.elastic import AbstractSearch, get_elastic
from db.redis import AbstractCacheStorage, get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.commons.sort import SortOrder
from models.person import Person


class PersonService:
    def __init__(self, redis: AbstractCacheStorage, elastic: AbstractSearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Person | None:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def search_in_elastic(
        self,
        query_: str,
        page_size_: int | None,
        page_number_: int | None,
        sort_by_: str | None = None,
        sort_order_: SortOrder | None = None,
    ) -> list[Person] | None:
        cache_key = f"{query_}:{page_size_}:{page_number_}:{sort_by_}:{sort_order_}"
        from_ = get_pagination(page_size_, page_number_)

        body = get_body(query_, from_, page_size_, sort_by_, sort_order_)

        persons = await self._search_persons_from_cache(cache_key)
        if not persons:
            persons = await self._search_persons_from_elastic(body)
            if not persons:
                return None
            await self._put_search_persons_to_cache(cache_key, persons)

        return persons

    async def _search_persons_from_elastic(self, body: dict) -> list[Person] | None:
        try:
            docs = await self.elastic.search(index="person", body=body)
            docs = docs.get("hits").get("hits")

            return [Person(**data["_source"]) for data in docs]

        except NotFoundError:
            return None

    async def _get_person_from_elastic(self, person_id: str) -> Person | None:
        try:
            doc = await self.elastic.get(index="person", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Person | None:
        data = await self.redis.get(f"person_id_{person_id}")
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            f"person_id_{person.id}", person.json(), ex=settings.redis_expire_time
        )

    async def _search_persons_from_cache(self, cache_key: str):
        data = await self.redis.get(cache_key)
        if not data:
            return None

    async def _put_search_persons_to_cache(self, cache_key: str, persons: list[Person]):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(persons)),
            ex=settings.redis_expire_time,
        )


@lru_cache()
def get_person_service(
    redis: AbstractCacheStorage = Depends(get_redis),
    elastic: AbstractSearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
