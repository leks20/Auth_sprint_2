from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from models.commons.sort import SortOrder
from models.film import Film, FilmSortBy
from services.film import FilmService, get_film_service
from utils.permissions import check_permission

router = APIRouter()


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Get film by ID",
    description="Get information about film: ID, title, description, imdb_rating, genre, director, actors, writers",
    tags=["Films"],
)
@check_permission(["admin"])
async def film_details(
    film_id: str,
    request: Request,
    film_service: FilmService = Depends(get_film_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> Film:
    if film := await film_service.get_by_id(film_id):
        return Film.from_orm(film)
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")


@router.get(
    "",
    response_model=List[Film],
    summary="Get list of films",
    description="Get a list of information about films: ID, title, description, imdb_rating, genre, director, actors, writers",
    tags=["Films"],
)
@check_permission(["admin", "user"])
async def film_search(
    request: Request,
    query_: str,
    page_size_: int
    | None = Query(10, alias="page[size]", description="Items amount on page", ge=1),
    page_number_: int
    | None = Query(
        1, alias="page[number]", description="Page number for pagination", ge=1
    ),
    sort_by_: FilmSortBy | None = None,
    sort_order_: SortOrder | None = None,
    film_service: FilmService = Depends(get_film_service),
    HTTPBearer: str = Header(name="HTTPBearer"),
) -> List[Film]:
    if sort_by_ == "title":
        sort_by_ += ".keyword"
    if result := await film_service.search_in_elastic(
        query_, page_size_, page_number_, sort_by_, sort_order_
    ):
        return result
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
