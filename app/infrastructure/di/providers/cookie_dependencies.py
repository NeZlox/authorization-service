"""
Authentication cookie management utilities.
Handles cookie operations and user authentication dependencies.
"""

from typing import Literal

import msgspec
from litestar import Request
from litestar.datastructures import Cookie
from litestar.params import Dependency
from personal_growth_sdk.authorization.constants.authentication import AUTH_ACCESS_TOKEN_KEY, AUTH_REFRESH_TOKEN_KEY
from personal_growth_sdk.authorization.constants.http_headers import (
    HEADER_DEVICE_FINGERPRINT,
    HEADER_USER_AGENT,
    HEADER_X_FORWARDED_FOR,
)
from personal_growth_sdk.authorization.models.enums import RoleType
from personal_growth_sdk.authorization.schemas import UserResponse

from app.application.services import UserService
from app.config.base_settings import get_settings
from app.lib.errors.exceptions import JWTAbsentException, JWTInvalidException, UserAccessDeniedException
from app.lib.schemas.client_info_schema import ClientInfoSchema
from app.lib.schemas.token_payload import TokenPayloadSchema
from app.lib.security import JWTManager

__all__ = [
    'create_role_based_dependency',
    'extract_client_info',
    'get_authenticated_user',
    'provide_set_auth_cookies',
]

settings = get_settings()


def provide_set_auth_cookies(
        access_token: str,
        refresh_token: str,
        is_delete: bool = False
) -> list[Cookie]:
    """
    Creates authentication cookies with proper security settings.

    Args:
        access_token: JWT access token
        refresh_token: JWT refresh token
        is_delete: Whether to create deletion cookies

    Returns:
        list[Cookie]: List of configured auth cookies
    """

    is_secure = settings.app.MODE in ['PROD', 'STAGE']
    same_site: Literal['lax', 'none'] = 'none' if settings.app.MODE in ['PROD', 'STAGE'] else 'lax'

    max_age_access = settings.app.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60 if not is_delete else 0
    max_age_refresh = settings.app.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400 if not is_delete else 0

    return [
        # ACCESS_TOKEN_
        Cookie(
            key=AUTH_ACCESS_TOKEN_KEY,
            value=access_token,
            max_age=max_age_access,
            secure=is_secure,
            httponly=True,
            samesite=same_site,
        ),
        # REFRESH_TOKEN
        Cookie(
            key=AUTH_REFRESH_TOKEN_KEY,
            value=refresh_token,
            max_age=max_age_refresh,
            secure=is_secure,
            httponly=True,
            samesite=same_site,
        )
    ]


def extract_client_info(request: Request) -> ClientInfoSchema:
    """
    Extracts client context information from request.

    Args:
        request: Incoming HTTP request

    Returns:
        ClientInfoSchema: Extracted client information
    """

    client_info = ClientInfoSchema(
        ip=request.headers.get(HEADER_X_FORWARDED_FOR) or '',
        user_agent=request.headers.get(HEADER_USER_AGENT),
        fingerprint=request.headers.get(HEADER_DEVICE_FINGERPRINT) or '',
        access_token=request.cookies.get(AUTH_ACCESS_TOKEN_KEY),
        refresh_token=request.cookies.get(AUTH_REFRESH_TOKEN_KEY)
    )
    return client_info


async def get_authenticated_user(
        request: Request,
        user_service: UserService
) -> UserResponse:
    """
    Validates JWT and retrieves authenticated user.

    Args:
        request: Incoming HTTP request
        user_service: User service instance

    Returns:
        UserResponse: Authenticated user data

    Raises:
        JWTAbsentException: If no access token provided
        JWTInvalidException: If token validation fails
    """

    client_info = extract_client_info(request)
    if client_info.access_token is None:
        raise JWTAbsentException
    try:
        payload_schema = msgspec.convert(
            JWTManager.decode_access_token(client_info.access_token),
            type=TokenPayloadSchema
        )
        user = await user_service.get(item_id=int(payload_schema.sub))
        return user_service.to_schema(data=user, schema_type=UserResponse)
    except Exception as exc:
        raise JWTInvalidException(details=str(exc)) from exc


def create_role_based_dependency(allowed_roles: tuple[RoleType, ...]):
    """
    Creates dependency that enforces role-based access control.

    Args:
        allowed_roles: Tuple of permitted roles

    Returns:
        Dependency that validates user roles
    """

    async def wrapper(
            request: Request, user_service: UserService = Dependency(skip_validation=True)  # noqa: B008
    ) -> UserResponse:
        user = await get_authenticated_user(request=request, user_service=user_service)

        if user.role not in allowed_roles:
            raise UserAccessDeniedException
        return user

    return wrapper
