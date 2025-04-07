"""
Session cleanup background job.
Removes
"""

import asyncio
import os
import sys
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
    logger.info('Starting session cleanup job')
    async with alchemy.get_session() as db_session:
        try:
            session_service: SessionService = await anext(provide_session_service(db_session))
            await session_service.delete_expired_sessions()
        except Exception as e:
            await logger.acritical(
                f'Session cleanup task failed with error: {e}',
                exc_info=True
            )
    logger.info('Session cleanup job completed successfully')


if __name__ == '__main__':
    # Set up project root path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Run the cleanup job
    asyncio.run(cleanup_expired_sessions())
