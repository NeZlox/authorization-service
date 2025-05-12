"""
Cron job management utilities.
Handles scheduling and cleanup of periodic tasks.
"""

import subprocess

from crontab import CronTab

from app.config.app_settings import get_settings
from app.lib.logger import logger

__all__ = ['clear_cron', 'write_cron']

settings = get_settings()


def write_cron():
    """
    Adds cron job for session cleanup (runs every 6 hours).
    """

    if not settings.app.CRON_JOBS_ENABLE:
        return

    # Get system paths
    python_path = subprocess.run(  # noqa: S603
        ['which', 'python'],  # noqa: S607
        capture_output=True,
        text=True,
        check=False
    ).stdout.strip()
    project_path = subprocess.run(  # noqa: S603
        ['pwd'],  # noqa: S607
        capture_output=True,
        text=True,
        check=False
    ).stdout.strip()

    logger.info(f'Python path: {python_path}')
    logger.info(f'PWD: {project_path}')

    cron = CronTab(user='root')

    # Debug logging configuration
    debug_command = f' >> {project_path}/logs/cron.log 2>&1' if settings.app.DEBUG else ''

    # Remove existing jobs
    cron.remove_all(comment=settings.app.CRON_JOB_IDENTIFIER)

    # Create new cleanup job
    job = cron.new(
        command=f'cd {project_path} && export PYTHONPATH={project_path} && export POSTGRES_DSN={settings.postgres.DSN} '
                f'&& export POSTGRES_SCHEMA={settings.postgres.SCHEMA} '
        # relative to the project root ↓
                f'&& {python_path} -m app.server.cron.job.session_cleanup_job{debug_command}',
        comment=settings.app.CRON_JOB_IDENTIFIER
    )

    # Schedule every 6 hours
    job.hours.every(6)

    cron.write()
    logger.info('Cron job for running parsers 4 times a day has been added')


def clear_cron():
    """Удаляет все `cron`-задачи для текущего пользователя."""
    if not settings.app.CRON_JOBS_ENABLE:
        return
    cron = CronTab(user='root')
    cron.remove_all(comment=settings.app.CRON_JOB_IDENTIFIER)
    cron.write()
    logger.info('All cron jobs cleared')


if __name__ == '__main__':
    import time

    # Test cron job management
    write_cron()
    time.sleep(5)
    clear_cron()
