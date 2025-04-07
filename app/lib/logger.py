"""
Centralized logging configuration for the application.
Configures structured logging with performance monitoring middleware.
"""

import logging
import time

import structlog
from litestar.logging import LoggingConfig, StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig
from litestar.types import ASGIApp, Receive, Scope, Send
from structlog.dev import RichTracebackFormatter

from app.config.base_settings import get_settings

settings = get_settings()

__all__ = ['create_request_processing_time_logging_middleware', 'log', 'logger']


def custom_log_processor(logger_instance, method_name, event_dict):  # noqa: ARG001
    """
    Custom log processor to standardize log format.
    """

    # print(event_dict)
    # print(method_name)

    event_dict['level'] = event_dict['level'].upper()
    event_dict['message'] = event_dict.pop('event')

    return event_dict


# Main logging configuration
log = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions='always',
        standard_lib_logging_config=LoggingConfig(
            root={'level': logging.getLevelName(settings.log.LEVEL)},
        ),
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder([
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]),

            custom_log_processor,

            structlog.processors.JSONRenderer() if settings.log.JSON else structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=RichTracebackFormatter(max_frames=1, show_locals=False, width=80)
            )
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    ),
    middleware_logging_config=LoggingMiddlewareConfig(
        request_log_fields=settings.log.REQUEST_FIELDS,
        response_log_fields=settings.log.RESPONSE_FIELDS,
    ),
)

# Configured logger instance
logger = log.structlog_logging_config.configure()()


def create_request_processing_time_logging_middleware(app: ASGIApp):
    """
    Middleware to log request processing time.
    """

    async def request_processing_time_logging_middleware(scope: Scope, receive: Receive, send: Send):
        start_time = time.perf_counter()
        await app(scope, receive, send)
        end_time = time.perf_counter()

        processing_time = (end_time - start_time) * 1000
        processing_time = f'{processing_time:.2f}ms'

        logger.info(
            'Request processing time',
            processing_time=processing_time,
            request_path=scope['path'],
            method=scope['method'].upper(),
        )

    return request_processing_time_logging_middleware
