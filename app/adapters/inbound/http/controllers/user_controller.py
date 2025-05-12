"""
User management API controller.
Handles user registration and account operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.service import OffsetPagination
from litestar import Controller, delete, get, post, put
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Dependency, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from personal_growth_sdk.authorization.models import User
from personal_growth_sdk.authorization.schemas import UserCreateRequest, UserResponse, UserUpdateRequest
from sqlalchemy.orm import selectinload

from app.adapters.inbound.http.urls.user_urls import (
    DELETE_USER_URI,
    GET_CURRENT_USER_URI,
    GET_USER_URI,
    GET_USERS_URI,
    POST_REGISTER_USER_URI,
    POST_USER_URI,
    PREFIX,
    PUT_USER_URI,
)
from app.application.services import UserService
from app.infrastructure.di.providers import create_role_based_dependency, provide_user_service
from app.lib.security import RoleGroup

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes

__all__ = ['UserController']


class UserController(Controller):
    """
    Controller for user management endpoints.

    Attributes:
        path: Base API path (/users)
        dependencies: Required service providers
        tags: OpenAPI grouping tag
    """

    path = PREFIX
    dependencies = {  # noqa: RUF012
        'user_service': Provide(provide_user_service)
    }
    tags = ['User']  # noqa: RUF012

    @post(
        path=POST_REGISTER_USER_URI,
        operation_id='RegisterUser',
        name='users:register',
        summary='Register new user',
        description='Public user registration endpoint with email verification',
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=UserResponse,
                description='Successfully registered new user'
            )
        }
    )
    async def register_user(
            self,
            user_service: UserService,
            data: Annotated[UserCreateRequest, Body(title='Register User')]
    ) -> UserResponse:
        """
        Handle new user registration.

        Args:
            user_service: User account service
            data: Registration data

        Returns:
            Created user profile
        """

        db_obj = await user_service.register_user(data)  # Предполагаем метод register в сервисе
        return user_service.to_schema(db_obj, schema_type=UserResponse)

    @get(
        path=GET_CURRENT_USER_URI,
        operation_id='GetCurrentUser',
        name='users:me',
        summary='Get current user profile',
        description='Retrieve authenticated user profile information',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.COMMON))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=UserResponse,
                description='Successfully retrieved user profile'
            )
        }
    )
    async def get_me(
            self,
            current_user: UserResponse
    ) -> UserResponse:
        """
        Get current user profile.

        Args:
            current_user: Authenticated user

        Returns:
            User profile data
        """

        return current_user

    @get(
        path=GET_USERS_URI,
        operation_id='GetUsers',
        name='users:get',
        summary='Get all users',
        description='Retrieve a list of all users (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=OffsetPagination[UserResponse],
                description='Successfully retrieved list of users'
            )
        }
    )
    async def get_users(
            self,
            current_user: UserResponse,  # noqa: ARG002
            user_service: UserService,
            filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]
    ) -> OffsetPagination[UserResponse]:
        """
        Get paginated user list.

        Args:
            current_user: Authenticated developer
            user_service: User service
            filters: Query filters

        Returns:
            Paginated user results
        """

        results, total = await user_service.list_and_count(*filters, load=selectinload(User.active_sessions))
        return user_service.to_schema(data=results, total=total, filters=filters, schema_type=UserResponse)

    @get(
        path=GET_USER_URI,
        operation_id='GetUser',
        name='users:get_one',
        summary='Get a single user',
        description='Retrieve a single user by their ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=UserResponse,
                description='Successfully retrieved the user'
            )
        }
    )
    async def get_user(
            self,
            current_user: UserResponse,  # noqa: ARG002
            user_service: UserService,
            user_id: Annotated[
                int,
                Parameter(
                    title='User ID',
                    description='The ID of the user to retrieve.'
                )
            ]
    ) -> UserResponse:
        """
        Get single user details.

        Args:
            current_user: Authenticated developer
            user_service: User service
            user_id: Target user ID

        Returns:
            Detailed user information
        """

        db_obj = await user_service.get(user_id, load=selectinload(User.active_sessions))
        return user_service.to_schema(db_obj, schema_type=UserResponse)

    @post(
        path=POST_USER_URI,
        operation_id='CreateUser',
        name='users:create',
        summary='Create a user',
        description='Create a new user with provided data (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_201_CREATED,
        responses={
            HTTP_201_CREATED: ResponseSpec(
                data_container=UserResponse,
                description='Successfully created a new user'
            )
        }
    )
    async def create_user(
            self,
            current_user: UserResponse,  # noqa: ARG002
            user_service: UserService,
            data: Annotated[UserCreateRequest, Body(title='Create User')]
    ) -> UserResponse:
        """
        Create new user record.

        Args:
            current_user: Authenticated developer
            user_service: User service
            data: User creation data

        Returns:
            Newly created user details
        """

        db_obj = await user_service.create(data)
        return user_service.to_schema(db_obj, schema_type=UserResponse)

    @put(
        path=PUT_USER_URI,
        operation_id='UpdateUser',
        name='users:update',
        summary='Update a user',
        description='Update an existing user by ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_200_OK,
        responses={
            HTTP_200_OK: ResponseSpec(
                data_container=UserResponse,
                description='Successfully updated the user'
            )
        }
    )
    async def update_user(
            self,
            current_user: UserResponse,  # noqa: ARG002
            user_service: UserService,
            user_id: Annotated[int, Parameter(title='User ID', description='The ID of the user to update')],
            data: Annotated[UserUpdateRequest, Body(title='Update Order')]
    ) -> UserResponse:
        """
        Update existing user.

        Args:
            current_user: Authenticated developer
            user_service: User service
            user_id: Target user ID
            data: User update data

        Returns:
            Updated user details
        """

        db_obj = await user_service.update(data, user_id)
        return user_service.to_schema(db_obj, schema_type=UserResponse)

    @delete(
        path=DELETE_USER_URI,
        operation_id='DeleteUser',
        name='users:delete',
        summary='Delete a user',
        description='Delete a user by ID (Private method for developers).',
        dependencies={'current_user': Provide(create_role_based_dependency(RoleGroup.PRIVATE))},
        status_code=HTTP_204_NO_CONTENT,
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                data_container=UserResponse,
                description='Successfully delete the user'
            )
        }
    )
    async def delete_user(
            self,
            current_user: UserResponse,  # noqa: ARG002
            user_service: UserService,
            user_id: Annotated[int, Parameter(title='User ID', description='The ID of the user to delete')]
    ) -> None:
        """
        Delete user record.

        Args:
            current_user: Authenticated developer
            user_service: User service
            user_id: Target user ID
        """

        await user_service.delete(user_id)
