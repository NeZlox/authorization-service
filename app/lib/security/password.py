"""
Password hashing and verification utilities.
Implements secure password handling using Argon2.
"""

from litestar.exceptions import NotAuthorizedException
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.lib.errors import AppException
from app.lib.logger import logger

__all__ = ['PasswordManager']


class PasswordManager:
    """
    Secure password handler using Argon2 hashing.

    Provides verification and hashing with secure defaults.
    """

    _pwd_context = CryptContext(
        schemes=['argon2'],
        deprecated='auto',
        argon2__memory_cost=131072,  # 128MB memory usage
        argon2__hash_len=32,  # 32-byte hash length
        argon2__time_cost=6,  # Higher time cost
        argon2__type='id'  # ID hash type
    )

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password against its hash.
        """

        try:
            return cls._pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError as exc:
            logger.error('Invalid hash format', exc_info=exc)
            raise NotAuthorizedException('Invalid authentication data') from exc
        except Exception as exc:
            logger.critical('Password verification error', exc_info=exc)
            raise NotAuthorizedException('Authentication failed', detail=str(exc)) from exc

    @classmethod
    def hash(cls, password: str) -> str:
        """
        Generates secure password hash.
        """

        try:
            return cls._pwd_context.hash(password)
        except Exception as exc:
            logger.critical('Password hashing failed', exc_info=exc)
            raise AppException('Password processing error') from exc
