from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_movie_search(make_get_request, test_data):
    expected_movies = await test_data("movies")

    for tested_movie in expected_movies:
        response = await make_get_request(
            "/films",
            params={
                "query_": tested_movie["title"],
                "page[size]": 10,
                "page[number]": 1,
            },
        )
        assert response.status == HTTPStatus.OK

        response_body = response.body
        assert len(response_body) <= 10
        assert response_body[0]["title"] == tested_movie["title"]


@pytest.mark.asyncio
async def test_movies_search_not_found(make_get_request):
    response = await make_get_request(
        "/films/",
        params={"query_": "Blablyreyteyuabla", "page[size]": 10, "page[number]": 1},
    )
    assert response.status == HTTPStatus.NOT_FOUND
