from functools import wraps
from typing import Any, AsyncGenerator

import httpx
import jwt
from core.config import settings
from core.logger import logger
from fastapi import Depends, HTTPException, Request, status
from httpx import AsyncClient


async def get_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client


async def verify_token(
    access_token: str, required_roles: list[str], request: Request
) -> str | None:

    client = AsyncClient()
    request_id = request.state.request_id

    try:
        response = await client.get(
            url=settings.verify_token_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Request-Id": request_id,
            },
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        logger.error(e, exc_info=True)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e,
        )

    decoded_token = jwt.decode(
        access_token, settings.secret_key, algorithms=[settings.jwt_algorithm]
    )
    role = decoded_token["sub"]["role"]

    if role in required_roles:
        return None

    return None


def check_permission(required_roles: list[str]) -> Any:
    def outer_wrapper(function: Any) -> Any:
        @wraps(function)
        async def inner_wrapper(*args: Any, **kwargs: Any) -> Any:

            access_token = kwargs.get("HTTPBearer")
            request = kwargs.get("request")

            if not access_token:
                msg = "Missing authorization token"
                logger.error(msg, exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=msg,
                )

            result = await verify_token(access_token, required_roles, request)

            if isinstance(result, str):
                logger.error(result, exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result,
                )
            return await function(*args, **kwargs)

        return inner_wrapper

    return outer_wrapper
