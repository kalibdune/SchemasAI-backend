import logging
from typing import Annotated

from fastapi import Depends, Path, Request, WebSocket, WebSocketException, status

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


async def websocket_auth(
    websocket: WebSocket, session=Depends(get_session)
) -> UserSchema:
    cookies_header = websocket.headers.get("cookie", "")
    cookies = {}

    for cookie in cookies_header.split("; "):
        if "=" in cookie:
            name, value = cookie.split("=", 1)
            cookies[name] = value

    access_token = cookies.get("access_token")
    if not access_token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        auth_service = AuthService(session)
        user = await auth_service.validate_token(access_token, TokenType.access)
        return user
    except Exception as e:
        logging.error(f"WebSocket authentication failed: %s", str(e))
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


WebSocketOAuth = Annotated[UserSchema, Depends(websocket_auth)]
OAuth = Annotated[UserSchema, Depends(check_auth)]
UnstrictedOAuth = Annotated[UserSchema | None, Depends(res_check_auth)]
