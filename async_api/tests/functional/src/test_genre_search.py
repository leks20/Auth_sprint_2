from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_genres_search(make_get_request, test_data):
    genres_test = await test_data("genre")
    expected_genres = [
        {"id": genre["id"], "name": genre["name"], "description": genre["description"]}
        for genre in genres_test
    ]

    for tested_genre in expected_genres:
        response = await make_get_request(
            "/genre",
            params={
                "query_": tested_genre["name"],
                "page[size]": 10,
                "page[number]": 1,
                "sort_order_": "desc",
            },
        )

        assert response.status == HTTPStatus.OK

        response_body = response.body
        assert len(response_body) <= 10
        assert response.body[0] == tested_genre


@pytest.mark.asyncio
async def test_genres_search_not_found(make_get_request):
    response = await make_get_request(
        "/genre/",
        params={
            "query_": "Blablabla",
            "page[size]": 10,
            "page[number]": 1,
            "sort_order_": "desc",
        },
    )

    assert response.status == HTTPStatus.NOT_FOUND
