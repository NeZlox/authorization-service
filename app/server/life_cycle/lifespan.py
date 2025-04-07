"""
Manages core application lifecycle events.
Handles startup/shutdown logging and hooks.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar

from app.config.base_settings import get_settings
from app.lib.logger import logger

__all__ = ['provide_lifespan_service']

settings = get_settings()


@asynccontextmanager
async def provide_lifespan_service(app: Litestar) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """
    Main lifespan manager for application events.
    """

    await logger.ainfo('Server is starting')
    try:
        yield
    finally:
        await logger.ainfo('Server is shutting down')
