from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from models.commons.sort import SortOrder
from models.genre import Genre
from services.genre import GenreService, get_genre_service
from utils.permissions import check_permission

router = APIRouter()


@router.get(
    "/{genre_id}",
    response_model=Genre,
    summary="Get genre by ID",
    description="Get information about genre: ID, name, description",
    tags=["Genres"],
)
@check_permission(["admin"])
async def genre_details(
    request: Request,
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> Genre:
    if genre := await genre_service.get_by_id(genre_id):
        return Genre.from_orm(genre)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")


@router.get(
    "",
    response_model=List[Genre],
    summary="Get list of genres",
    description="Get a list of information about genres: id, name, description",
    tags=["Genres"],
)
@check_permission(["admin", "user"])
async def genre_search(
    request: Request,
    query_: str,
    page_size_: int
    | None = Query(10, alias="page[size]", description="Items amount on page", ge=1),
    page_number_: int
    | None = Query(
        1, alias="page[number]", description="Page number for pagination", ge=1
    ),
    sort_order_: SortOrder = SortOrder.asc,
    genre_service: GenreService = Depends(get_genre_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> List[Genre]:
    sort_by_: str = "name.keyword"
    if result := await genre_service.search_in_elastic(
        query_, page_size_, page_number_, sort_by_, sort_order_
    ):
        return result
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
