"""
Authentication API controller.
Handles user login, token refresh, and logout operations.
"""

from __future__ import annotations

from typing import Annotated

from litestar import Controller, delete, post, put
from litestar.datastructures import Cookie
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT
from personal_growth_sdk.authorization.constants.authentication import AUTH_ACCESS_TOKEN_KEY, AUTH_REFRESH_TOKEN_KEY
from personal_growth_sdk.authorization.schemas import UserLoginRequest, UserResponse

from app.adapters.inbound.http.urls.auth_urls import (
    DELETE_SESSIONS,
    DELETE_SESSIONS_ALL,
    POST_SESSIONS,
    PREFIX,
    PUT_SESSIONS,
)
from app.application.services import SessionService, UserService
from app.infrastructure.di.providers import provide_auth_service, provide_session_service, provide_user_service
from app.infrastructure.di.providers.cookie_dependencies import (
    create_role_based_dependency,
    extract_client_info,
    provide_set_auth_cookies,
)
from app.lib.schemas.client_info_schema import ClientInfoSchema
from app.lib.security import RoleGroup

__all__ = ['AuthController']


class AuthController(Controller):
    """
    Controller for authentication endpoints.

    Attributes:
        path: Base API path (/auth)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'session_service': Provide(provide_session_service),
        'user_service': Provide(provide_user_service),
        'client_info': Provide(extract_client_info, sync_to_thread=False)
    }
    tags = ['Authentication']  # noqa: RUF012

    @post(
        path=POST_SESSIONS,
        operation_id='CreateAuthToken',
        summary='User login',
        description='Authenticate user and get access/refresh token pair',
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=UserResponse,
                description='Successfully authenticated'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token for authorization',
                documentation_only=True,
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token for renewing access',
                documentation_only=True,
            ),
        ]
    )
    async def login(
            self,
            client_info: ClientInfoSchema,
            session_service: SessionService,
            user_service: UserService,
            data: UserLoginRequest,

    ) -> Response[UserResponse]:
        """
        Handle user login request.

        Args:
            client_info: Client context (IP, user agent)
            session_service: Session management service
            user_service: User account service
            data: Login credentials

        Returns:
            Response with user data and auth cookies
        """

        auth_service = provide_auth_service(
            user_service=user_service, session_service=session_service, client_info=client_info
        )
        user_schema, token_schema = await auth_service.login(data)
        cookies = provide_set_auth_cookies(
            access_token=token_schema.access_token,
            refresh_token=token_schema.refresh_token
        )

        return Response(
            content=user_schema,
            cookies=cookies
        )

    @put(
        path=PUT_SESSIONS,
        operation_id='RefreshAuthToken',
        summary='Refresh access token',
        description='Get new access token using refresh token',
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Token refreshed'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='New Access token (if successfully refreshed)',
                documentation_only=True,
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Possibly new Refresh token (if server reissues it)',
                documentation_only=True,
            ),
        ]
    )
    async def refresh_token(
            self,
            client_info: ClientInfoSchema,
            session_service: SessionService,
            user_service: UserService,
            user_id: Annotated[
                int,
                Body(
                    title='User ID',
                    description='The ID of the user to retrieve.'
                )

            ]
    ) -> Response[None]:
        """
        Handle token refresh request.

        Args:
            client_info: Client context
            session_service: Session service
            user_service: User service
            user_id: Authenticated user ID

        Returns:
            Response with new auth cookies
        """

        auth_service = provide_auth_service(
            user_service=user_service, session_service=session_service, client_info=client_info
        )
        response_tokens = await auth_service.refresh_session(user_id=user_id)
        cookies = provide_set_auth_cookies(
            access_token=response_tokens.access_token,
            refresh_token=response_tokens.refresh_token
        )
        return Response(
            content=None,
            cookies=cookies
        )

    @delete(
        path=DELETE_SESSIONS,
        operation_id='RevokeAuthToken',
        summary='User logout',
        description='Invalidate current session and revoke tokens',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.COMMON))},
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Successfully logged out'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token removed',
                documentation_only=True
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token removed',
                documentation_only=True
            ),
        ]
    )
    async def logout(
            self,
            client_info: ClientInfoSchema,
            current_user: UserResponse,
            session_service: SessionService,
            user_service: UserService
    ) -> Response[None]:
        """
        Handle user logout request.

        Args:
            client_info: Client context
            current_user: Authenticated user
            session_service: Session service
            user_service: User service

        Returns:
            Response with expired auth cookies
        """

        auth_service = provide_auth_service(
            user_service=user_service, session_service=session_service, client_info=client_info
        )
        await auth_service.revoke_session(user_id=current_user.id)
        cookies = provide_set_auth_cookies(
            access_token='',
            refresh_token='',
            is_delete=True
        )
        return Response(
            content=None,
            cookies=cookies
        )

    @delete(
        path=DELETE_SESSIONS_ALL,
        operation_id='RevokeAllSessions',
        summary='Terminate all sessions',
        description='Invalidate all active sessions for current user',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.COMMON))},
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='All sessions terminated'
            )
        },
        response_cookies=[
            Cookie(
                key=AUTH_ACCESS_TOKEN_KEY,
                description='Access token removed',
                documentation_only=True
            ),
            Cookie(
                key=AUTH_REFRESH_TOKEN_KEY,
                description='Refresh token removed',
                documentation_only=True
            ),
        ]
    )
    async def terminate_all_sessions(
            self,
            client_info: ClientInfoSchema,
            current_user: UserResponse,
            session_service: SessionService,
            user_service: UserService
    ) -> Response[None]:
        """
        Handle global logout request.

        Args:
            client_info: Client context
            current_user: Authenticated user
            session_service: Session service
            user_service: User service

        Returns:
            Response with expired auth cookies
        """

        auth_service = provide_auth_service(
            user_service=user_service, session_service=session_service, client_info=client_info
        )
        await auth_service.revoke_all_sessions(id_user=current_user.id)
        cookies = provide_set_auth_cookies(
            access_token='',
            refresh_token='',
            is_delete=True
        )
        return Response(
            content=None,
            cookies=cookies
        )
