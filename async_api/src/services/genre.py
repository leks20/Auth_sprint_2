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
from models.genre import Genre


class GenreService:
    def __init__(self, redis: AbstractCacheStorage, elastic: AbstractSearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Genre | None:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def search_in_elastic(
        self,
        query_: str,
        page_size_: int | None,
        page_number_: int | None,
        sort_by_: str | None = None,
        sort_order_: SortOrder | None = None,
    ) -> list[Genre] | None:
        cache_key = f"{query_}:{page_size_}:{page_number_}:{sort_by_}:{sort_order_}"
        from_ = get_pagination(page_size_, page_number_)

        body = get_body(query_, from_, page_size_, sort_by_, sort_order_)

        genres = await self._search_genres_from_cache(cache_key)
        if not genres:
            genres = await self._search_genres_from_elastic(body)
            if not genres:
                return None
            await self._put_search_genres_to_cache(cache_key, genres)

        return genres

    async def _search_genres_from_elastic(self, body: dict) -> list[Genre] | None:
        try:
            docs = await self.elastic.search(index="genre", body=body)
            docs = docs.get("hits").get("hits")

            return [Genre(**data["_source"]) for data in docs]

        except NotFoundError:
            return None

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        try:
            doc = await self.elastic.get(index="genre", id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Genre | None:
        data = await self.redis.get(f"genre_id_{genre_id}")
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            f"genre_id_{genre.id}", genre.json(), ex=settings.redis_expire_time
        )

    async def _search_genres_from_cache(self, cache_key: str):
        data = await self.redis.get(cache_key)
        if not data:
            return None

    async def _put_search_genres_to_cache(self, cache_key: str, genres: list[Genre]):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(genres)),
            ex=settings.redis_expire_time,
        )


@lru_cache()
def get_genre_service(
    redis: AbstractCacheStorage = Depends(get_redis),
    elastic: AbstractSearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
