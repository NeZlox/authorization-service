"""
Database repository for User model.
Handles basic database operations for user entities.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from personal_growth_sdk.authorization.models import User

__all__ = ['UserRepository']


class UserRepository(SQLAlchemyAsyncRepository[User]):
    """
    Async repository for User model operations
    """

    model_type = User  # Specifies the SQLAlchemy model class
