"""
Handles application startup routines.
Mainly schedules background tasks using cron.
"""

from app.server.cron import write_cron

__all__ = ['startup_callables_list']

startup_callables_list = [
    write_cron
]
