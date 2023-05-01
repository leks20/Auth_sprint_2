from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_person_search(make_get_request, test_data):
    persons_test = await test_data("person")
    expected_persons = [
        {
            "id": person["id"],
            "full_name": person["full_name"],
        }
        for person in persons_test
    ]
    for tested_person in expected_persons:
        response = await make_get_request(
            "/person",
            params={
                "query_": tested_person["full_name"],
                "page[size]": 10,
                "page[number]": 1,
                "sort_order_": "desc",
            },
        )
        assert response.status == HTTPStatus.OK
        response_body = response.body
        assert len(response_body) <= 10
        assert response.body[0] == tested_person


@pytest.mark.asyncio
async def test_person_search_not_found(make_get_request):
    response = await make_get_request(
        "/person/",
        params={
            "query_": "Blablyreyteyuabla",
            "page[size]": 10,
            "page[number]": 1,
            "sort_order_": "desc",
        },
    )
    assert response.status == HTTPStatus.NOT_FOUND
