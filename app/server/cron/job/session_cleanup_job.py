"""
Session cleanup background job.
Removes
"""

import asyncio
from typing import TYPE_CHECKING

from app.config.app_settings import alchemy
from app.infrastructure.di.providers import provide_session_service
from app.lib.logger import logger

if TYPE_CHECKING:
    from app.application.services import SessionService


async def cleanup_expired_sessions():
    """
    Main job function to delete expired sessions.
    """
    await logger.ainfo('Starting session cleanup job')
    async with alchemy.get_session() as db_session:
        try:
            session_service: SessionService = await anext(provide_session_service(db_session))
            await session_service.delete_expired_sessions()
            await db_session.commit()
        except Exception as exc:
            await logger.acritical(
                f'Session cleanup task failed with error: {exc!s}'
            )
    await logger.ainfo('Session cleanup job completed successfully')


if __name__ == '__main__':
    asyncio.run(cleanup_expired_sessions())
