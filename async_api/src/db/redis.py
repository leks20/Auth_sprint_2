from abc import ABC, abstractmethod

from aioredis import Redis


class AbstractCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str | bytes, ex: int, **kwargs):
        pass


class RedisStorage(AbstractCacheStorage):
    def __init__(self, storage: Redis):
        self.redis = storage

    async def get(self, key: str, **kwargs):
        return await self.redis.get(key)

    async def set(self, key: str, value: str | bytes, ex: int, **kwargs):
        await self.redis.set(key, "", ex=ex)


redis: RedisStorage | None = None


async def get_redis() -> RedisStorage:
    return redis
