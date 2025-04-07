"""
Refresh session API controller.
Manages active user sessions (developer tools).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.service import OffsetPagination
from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Dependency, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from personal_growth_sdk.authorization.models import Session
from personal_growth_sdk.authorization.schemas import (
    SessionCreateRequest,
    SessionResponse,
    SessionUpdateRequest,
    UserResponse,
)
from sqlalchemy.orm import selectinload

from app.adapters.inbound.http.urls.session_urls import (
    DELETE_SESSION_URI,
    GET_SESSION_URI,
    GET_SESSIONS_URI,
    POST_SESSION_URI,
    PREFIX,
    PUT_SESSION_URI,
)
from app.application.services import SessionService
from app.infrastructure.di.providers import create_role_based_dependency, provide_session_service, provide_user_service
from app.lib.security import RoleGroup

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes

__all__ = ['SessionController']


class SessionController(Controller):
    """
    Controller for session management endpoints.

    Attributes:
        path: Base API path (/refresh-sessions)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'user_service': Provide(provide_user_service),
        'session_service': Provide(provide_session_service)
    }
    tags = ['Refresh Sessions']  # noqa: RUF012

    @get(
        path=GET_SESSIONS_URI,
        operation_id='GetRefreshSessions',
        name='refresh_sessions:get',
        summary='Get all refresh sessions',
        description='Retrieve a list of all refresh sessions (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=OffsetPagination[SessionResponse],
                description='Successfully retrieved list of refresh sessions'
            )
        }
    )
    async def get_sessions(
            self,
            current_user: UserResponse,  # noqa: ARG002
            session_service: SessionService,
            filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]
    ) -> OffsetPagination[SessionResponse]:
        """
        Get paginated session list.

        Args:
            current_user: Authenticated developer
            session_service: Session service
            filters: Query filters

        Returns:
            Paginated session results
        """

        results, total = await session_service.list_and_count(*filters, load=selectinload(Session.user))
        return session_service.to_schema(
            data=results,
            total=total,
            filters=filters,
            schema_type=SessionResponse
        )

    @get(
        path=GET_SESSION_URI,
        operation_id='GetRefreshSession',
        name='refresh_sessions:get_one',
        summary='Get a single refresh session',
        description='Retrieve a single refresh session by its ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=SessionResponse,
                description='Successfully retrieved the refresh session'
            )
        }
    )
    async def get_session(
            self,
            current_user: UserResponse,  # noqa: ARG002
            session_service: SessionService,
            refresh_session_id: Annotated[
                int,
                Parameter(
                    title='Session ID',
                    description='The ID of the refresh session to retrieve.'
                )
            ]
    ) -> SessionResponse:
        """
        Get single session details.

        Args:
            current_user: Authenticated developer
            session_service: Session service
            refresh_session_id: Target session ID

        Returns:
            Detailed session information
        """

        db_obj = await session_service.get(refresh_session_id, load=selectinload(Session.user))
        return session_service.to_schema(db_obj, schema_type=SessionResponse)

    @post(
        path=POST_SESSION_URI,
        operation_id='CreateRefreshSession',
        name='refresh_sessions:create',
        summary='Create a refresh session',
        description='Create a new refresh session with provided data (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=SessionResponse,
                description='Successfully created a new refresh session'
            )
        }
    )
    async def create_session(
            self,
            current_user: UserResponse,  # noqa: ARG002
            session_service: SessionService,
            data: Annotated[SessionCreateRequest, Body(title='Create Refresh Session')]
    ) -> SessionResponse:
        """
        Create new session record.

        Args:
            current_user: Authenticated developer
            session_service: Session service
            data: Session creation data

        Returns:
            Newly created session details
        """

        db_obj = await session_service.create(data)
        return session_service.to_schema(db_obj, schema_type=SessionResponse)

    @put(
        path=PUT_SESSION_URI,
        operation_id='UpdateRefreshSession',
        name='refresh_sessions:update',
        summary='Update a refresh session',
        description='Update an existing refresh session by ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=SessionResponse,
                description='Successfully updated the refresh session'
            )
        }
    )
    async def update_session(
            self,
            current_user: UserResponse,  # noqa: ARG002
            session_service: SessionService,
            refresh_session_id: Annotated[
                int, Parameter(title='Session ID', description='The ID of the session to update')],
            data: Annotated[SessionUpdateRequest, Body(title='Update Refresh Session')]
    ) -> SessionResponse:
        """
        Update existing session.

        Args:
            current_user: Authenticated developer
            session_service: Session service
            refresh_session_id: Target session ID
            data: Session update data

        Returns:
            Updated session details
        """

        db_obj = await session_service.update(data, refresh_session_id)
        return session_service.to_schema(db_obj, schema_type=SessionResponse)

    @delete(
        path=DELETE_SESSION_URI,
        operation_id='DeleteRefreshSession',
        name='refresh_sessions:delete',
        summary='Delete a refresh session',
        description='Delete a refresh session by ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=None,
                description='Successfully delete the refresh session'
            )
        }
    )
    async def delete_session(
            self,
            current_user: UserResponse,  # noqa: ARG002
            session_service: SessionService,
            refresh_session_id: Annotated[
                int, Parameter(title='Session ID', description='The ID of the session to delete')]
    ) -> None:
        """
        Delete session record.

        Args:
            current_user: Authenticated developer
            session_service: Session service
            refresh_session_id: Target session ID
        """

        await session_service.delete(refresh_session_id)
