"""
Service for health check monitoring.
Provides system status and dependency health information.
"""

from personal_growth_sdk.lib.schemas.health_check_schema import (
    DependencyHealth,
    DependencyType,
    HealthSchema,
    HealthStatus,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.app_settings import get_settings
from app.lib.logger import logger

settings = get_settings()


class HealthService:
    """
    Service that performs system health checks and monitoring.

    Attributes:
        db_session: Async database session for health checks
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_health(self) -> HealthSchema:
        """
        Performs comprehensive health checks of system dependencies.

        Returns:
            HealthSchema: Complete health status with dependency details
        """

        db_dependency = DependencyHealth(
            name=f'PostgresSQL: schema `{settings.postgres.SCHEMA}`',
            status=HealthStatus.OK,
            type=DependencyType.POSTGRES,
            details=None
        )

        try:
            # Basic database connectivity test
            result = await self.db_session.execute(
                text("""
                        SELECT schema_name
                        FROM information_schema.schemata
                        WHERE schema_name = :schema
                    """),
                {"schema": settings.postgres.SCHEMA}
            )
            if result.scalar() != settings.postgres.SCHEMA:
                db_dependency.status = HealthStatus.ERROR
                db_dependency.details = {'error': f'Schema `{settings.postgres.SCHEMA}` not found'}
        except Exception as e:
            await logger.aerror(f'[HealthCheck] Ошибка при проверке Базы данных: {e}')
            db_dependency.status = HealthStatus.ERROR
            db_dependency.details = {'error': str(e)}

        deps = [db_dependency]

        status = HealthStatus.OK if all(dep.status == HealthStatus.OK for dep in deps) else HealthStatus.ERROR

        return HealthSchema(
            status=status,
            deps=deps
        )
