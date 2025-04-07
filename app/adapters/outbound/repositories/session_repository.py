"""
Database repository for Session model.
Provides basic CRUD operations for user sessions.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from personal_growth_sdk.authorization.models import Session

__all__ = ['SessionRepository']


class SessionRepository(SQLAlchemyAsyncRepository[Session]):
    """
    Async repository for Session model operations
    """

    model_type = Session  # Specifies the SQLAlchemy model class
