from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_genre(make_get_request, test_data):
    expected = await test_data("genre")
    for tested_genre in expected:
        response = await make_get_request(f"/genre/{tested_genre['id']}", params={})
        assert response.status == HTTPStatus.OK
        assert response.body == tested_genre


@pytest.mark.asyncio
async def test_genre_404(make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/genre/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
