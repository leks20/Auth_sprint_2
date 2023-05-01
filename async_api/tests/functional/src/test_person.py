from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_person(make_get_request, test_data):
    expected = await test_data("person")
    for tested_person in expected:
        response = await make_get_request(f"/person/{tested_person['id']}", params={})

        assert response.status == HTTPStatus.OK
        assert response.body == tested_person


@pytest.mark.asyncio
async def test_person_404(make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/person/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
