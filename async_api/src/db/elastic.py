from abc import ABC, abstractmethod
from typing import Any

from elasticsearch import AsyncElasticsearch


class AbstractSearch(ABC):
    @abstractmethod
    def get(self, index: str, id: str):
        pass

    @abstractmethod
    def search(self, index: str, body, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass


class Elasticsearch(AbstractSearch):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get(self, index: str, id: str) -> Any:
        return await self.elastic.get(index, id)

    async def search(self, index: str, body, **kwargs) -> Any:
        return await self.elastic.search(index, body)


es: Elasticsearch | None = None


async def get_elastic() -> Elasticsearch:
    return es
