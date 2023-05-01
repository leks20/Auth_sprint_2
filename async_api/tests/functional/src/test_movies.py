from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_movies(make_get_request, test_data):
    expected = await test_data("movies")
    for tested_movie in expected:
        response = await make_get_request(f"/films/{tested_movie['id']}", params={})
        assert response.status == HTTPStatus.OK

        response_body = response.body
        assert response_body["id"] == tested_movie["id"]
        assert response_body["title"] == tested_movie["title"]


@pytest.mark.asyncio
async def test_movies_404(make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/films/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
