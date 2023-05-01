from dataclasses import dataclass

import aiohttp
import pytest
from multidict import CIMultiDictProxy

from .settings import config

pytest_plugins = ["fixtures.datareader", "fixtures.elastic_up_down"]


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="module")
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def make_get_request(session):
    async def inner(target: str, params: dict = None):
        url = f"{config.service_schema}://{config.service_url}:{config.service_port}/api/v1{target}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
