"""
Contains application middleware configurations.
Primary purpose is request processing time logging.
"""

from app.lib.logger import create_request_processing_time_logging_middleware

__all__ = ['middlewares_list']

middlewares_list = [
    create_request_processing_time_logging_middleware
]
