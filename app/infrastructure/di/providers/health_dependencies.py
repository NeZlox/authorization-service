"""
Dependency provider for HealthService.
Provides health monitoring service with database session.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services import HealthService
from app.config.base_settings import get_settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ['provide_health_service']

settings = get_settings()


async def provide_health_service(
        db_session: AsyncSession | None = None,
) -> HealthService:
    """
    Factory function that creates HealthService instance.

    Args:
        db_session: Optional database session

    Returns:
        HealthService: Configured health monitoring service
    """

    return HealthService(
        db_session=db_session

    )
