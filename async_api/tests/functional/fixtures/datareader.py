import json

import aiofiles
import pytest

from async_api.tests.functional.settings import config


@pytest.fixture
def test_data():
    async def inner(name_index: str):
        file = config.data_dir.joinpath(f"{name_index}_data.json")
        async with aiofiles.open(file, encoding="utf-8") as file:
            data = await file.read()
            data_json = json.loads(data)
        return data_json

    return inner
