from typing import Annotated

from fastapi import Depends, Path, Request

from schemas.config import config
from schemas.db.schemas.user import UserSchema
from schemas.db.session import session_manager
from schemas.services.auth import AuthService
from schemas.utils.enums import TokenType
from schemas.utils.exceptions import UnauthorizedError


async def get_session():
    async with session_manager.session() as session:
        yield session


async def check_auth(request: Request, session=Depends(get_session)) -> UserSchema:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise UnauthorizedError("token not provided")
    return await AuthService(session).validate_token(access_token, TokenType.access)


async def res_check_auth(
    request: Request, session=Depends(get_session)
) -> UserSchema | None:
    try:
        return await check_auth(request, session)
    except:
        return None


OAuth = Annotated[UserSchema, Depends(check_auth)]
UnstrictedOAuth = Annotated[UserSchema | None, Depends(res_check_auth)]
