"""
Business logic service for session management.
Handles session lifecycle and enforcement rules.
"""

import datetime

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from personal_growth_sdk.authorization.models import Session

from app.adapters.outbound.repositories import SessionRepository
from app.config.constants import MAX_ACTIVE_REFRESH_SESSIONS

__all__ = ['SessionService']


class SessionService(SQLAlchemyAsyncRepositoryService[Session]):
    """
    Service layer for session operations
    """

    repository_type = SessionRepository  # Associated repository

    async def enforce_session_limit(self, user_id: int):
        """
        Enforces maximum active sessions per user.
        Removes oldest sessions when limit is exceeded.

        Args:
            user_id: User identifier to check sessions for
        """

        active_sessions, total = await self.list_and_count(
            Session.user_id == user_id,
            Session.expires_at > datetime.datetime.now(datetime.UTC)
        )

        if total >= MAX_ACTIVE_REFRESH_SESSIONS:
            # Определяем количество сессий для удаления
            sessions_to_delete_count = total - MAX_ACTIVE_REFRESH_SESSIONS
            # Получаем ID сессий, которые необходимо удалить
            if sessions_to_delete_count > 0:
                sessions_to_delete_ids = [
                    session.id for session in
                    sorted(active_sessions, key=lambda x: x.created_at)[:sessions_to_delete_count]
                ]
                await self.delete_many(item_ids=sessions_to_delete_ids)

    async def delete_expired_sessions(self):
        """
        Cleans up expired sessions from database
        """

        await self.delete_where(Session.expires_at < datetime.datetime.now(datetime.UTC))
