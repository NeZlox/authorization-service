"""
Business logic service for user management.
Handles user registration and authentication.
"""

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from personal_growth_sdk.authorization.models import User
from personal_growth_sdk.authorization.schemas import UserCreateRequest

from app.adapters.outbound.repositories import UserRepository

__all__ = ['UserService']

from app.lib.errors.exceptions import UserAlreadyExistsByEmailException
from app.lib.security import PasswordManager


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    """
    Service layer for user operations
    """

    repository_type = UserRepository  # Associated repository

    async def register_user(self, user_data: UserCreateRequest) -> User:
        """
        Registers new user with email/password.

        Args:
            user_data: User registration data

        Returns:
            User: Created user entity

        Raises:
            UserAlreadyExistsByEmailException: If email already registered
        """

        existing_user_by_email = await self.get_one_or_none(User.email == user_data.email)

        if existing_user_by_email:
            raise UserAlreadyExistsByEmailException(message='User already exists.')

        hashed_password = PasswordManager.hash(user_data.password)
        user_data.password = hashed_password

        new_user = await self.create(user_data)

        return new_user
