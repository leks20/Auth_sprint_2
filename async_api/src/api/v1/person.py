from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from models.commons.sort import SortOrder
from models.person import Person
from services.person import PersonService, get_person_service
from utils.permissions import check_permission

router = APIRouter()


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Get person by ID",
    description="Get information about person: ID and name",
    tags=["Persons"],
)
@check_permission(["admin"])
async def person_details(
    request: Request,
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> Person:
    if person := await person_service.get_by_id(person_id):
        return Person.from_orm(person)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")


@router.get(
    "",
    response_model=List[Person],
    summary="Get list of persons",
    description="Get a list of information about persons: id and name",
    tags=["Persons"],
)
@check_permission(["admin", "user"])
async def person_search(
    request: Request,
    query_: str,
    page_size_: int
    | None = Query(10, alias="page[size]", description="Items amount on page", ge=1),
    page_number_: int
    | None = Query(
        1, alias="page[number]", description="Page number for pagination", ge=1
    ),
    sort_order_: SortOrder = SortOrder.asc,
    person_service: PersonService = Depends(get_person_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> List[Person]:
    sort_by_: str = "full_name.keyword"
    if result := await person_service.search_in_elastic(
        query_, page_size_, page_number_, sort_by_, sort_order_
    ):
        return result
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
