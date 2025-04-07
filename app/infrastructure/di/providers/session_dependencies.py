"""
Dependency provider for SessionService.
Manages session service lifecycle with database connection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services import SessionService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_session_service']


async def provide_session_service(
        db_session: AsyncSession | None = None,
) -> AsyncGenerator[SessionService, None]:
    """
    Async generator that provides SessionService instance.

    Args:
        db_session: Optional database session

    Yields:
        SessionService: Configured session service
    """

    async with SessionService.new(
            session=db_session
    ) as service:
        yield service
