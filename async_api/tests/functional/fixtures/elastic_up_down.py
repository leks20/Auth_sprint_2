import json

import aiofiles
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from async_api.tests.functional.settings import config


@pytest.fixture(scope="session", autouse=True)
async def create_indexes():
    client = AsyncElasticsearch(
        hosts=f"{config.elastic_schema}://{config.elastic_host}:{config.elastic_port}"
    )

    for name in ["movies", "genre", "person"]:
        scheme_name = f"scheme_{name}.json"
        async with aiofiles.open(
            config.schemes_dir.joinpath(scheme_name), encoding="utf-8"
        ) as scheme_file:
            scheme = await scheme_file.read()
            scheme_json = json.loads(scheme)
        await client.indices.create(index=name, body=scheme_json, ignore=400)

    for name in ["genre", "person", "movies"]:
        data_name = f"{name}_data.json"
        async with aiofiles.open(
            config.data_dir.joinpath(data_name), encoding="utf-8"
        ) as data_file:
            data = await data_file.read()
            data_json = json.loads(data)
            await async_bulk(
                client=client,
                actions=[
                    {"_index": name, "_id": record["id"], **record}
                    for record in data_json
                ],
            )

    for name in ["genre", "person", "movies"]:
        items = {}
        while not items.get("count"):
            items = await client.count(index=name)

    yield client

    for name in ["movies", "genre", "person"]:
        await client.options(ignore_status=[400, 404]).indices.delete(index=name)

    await client.close()
