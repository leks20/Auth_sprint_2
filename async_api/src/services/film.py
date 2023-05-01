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
from models.film import Film, FilmSortBy


class FilmService:
    def __init__(self, redis: AbstractCacheStorage, elastic: AbstractSearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Film | None:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def search_in_elastic(
        self,
        query_: str,
        page_size_: int | None,
        page_number_: int | None,
        sort_by_: FilmSortBy | None = None,
        sort_order_: SortOrder | None = None,
    ) -> list[Film] | None:

        cache_key = f"{query_}:{page_size_}:{page_number_}:{sort_by_}:{sort_order_}"
        from_ = get_pagination(page_size_, page_number_)

        body = get_body(query_, from_, page_size_, sort_by_, sort_order_)

        films = await self._search_film_from_cache(cache_key)
        if not films:
            films = await self._search_film_from_elastic(body)
            if not films:
                return None
            await self._put_search_film_to_cache(cache_key, films)

        return films

    async def _search_film_from_elastic(self, body: dict) -> list[Film] | None:
        try:
            docs = await self.elastic.search(index="movies", body=body)
            docs = docs.get("hits").get("hits")

            return [Film(**data["_source"]) for data in docs]

        except NotFoundError:
            return None

    async def _get_film_from_elastic(self, film_id: str) -> Film | None:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Film | None:
        data = await self.redis.get(f"film_id_{film_id}")
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            f"film_id_{film.id}", film.json(), ex=settings.redis_expire_time
        )

    async def _search_film_from_cache(self, cache_key: str):
        data = await self.redis.get(cache_key)
        if not data:
            return None

    async def _put_search_film_to_cache(self, cache_key: str, films: list[Film]):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(films)),
            ex=settings.redis_expire_time,
        )


@lru_cache()
def get_film_service(
    redis: AbstractCacheStorage = Depends(get_redis),
    elastic: AbstractSearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
