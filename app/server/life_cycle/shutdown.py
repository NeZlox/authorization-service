"""
Manages application shutdown procedures.
Ensures proper cleanup of scheduled tasks.
"""

from app.server.cron import clear_cron

__all__ = ['shutdown_callables_list']

shutdown_callables_list = [
    clear_cron
]
