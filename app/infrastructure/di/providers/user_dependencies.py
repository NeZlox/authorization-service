"""
Dependency provider for UserService.
Manages user service lifecycle with database connection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services import UserService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_user_service']


async def provide_user_service(
        db_session: AsyncSession | None = None,
) -> AsyncGenerator[UserService, None]:
    """
    Async generator that provides UserService instance.

    Args:
        db_session: Optional database session

    Yields:
        UserService: Configured user service
    """

    async with UserService.new(
            session=db_session
    ) as service:
        yield service
