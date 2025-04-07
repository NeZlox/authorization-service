"""
JWT token management utilities.
Handles generation, validation and cryptographic operations for access/refresh tokens.
"""

import datetime
import secrets

from jose import jwt
from passlib.context import CryptContext

from app.config.base_settings import get_settings
from app.config.constants import REFRESH_TOKEN_LENGTH
from app.lib.errors.exceptions import (
    AppException,
    JWTCannotDecodeException,
    JWTCannotEncodeException,
    JWTExpiredException,
    JWTInvalidException,
)
from app.lib.logger import logger

__all__ = ['JWTManager']
settings = get_settings()


class JWTManager:
    """
    JWT token processor with cryptographic operations.

    Uses Argon2 for refresh token hashing and configurable JWT algorithms.
    """

    _pwd_context = CryptContext(
        schemes=['argon2'],
        deprecated='auto',
        argon2__memory_cost=32768,  # 32MB memory usage
        argon2__hash_len=64,  # 64-byte hash length
        argon2__time_cost=3,  # Lower time cost
        argon2__type='id'  # ID hash type
    )

    @staticmethod
    def generate_access_token(payload: dict) -> str:
        """
        Generates a signed JWT access token with expiration.
        """

        try:
            to_encode = payload.copy()
            expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=settings.app.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({'exp': expire})

            encoded_jwt = jwt.encode(
                to_encode,
                settings.app.JWT_PRIVATE_KEY,
                algorithm=settings.app.JWT_ALGORITHM
            )
            return str(encoded_jwt)
        except Exception as exc:
            msg = 'JwtToken: create_access_token: Unknown error'
            extra = {'query_params': payload, 'error': exc}
            logger.critical(msg, extra=extra, exc_info=True)
            raise JWTCannotEncodeException from exc

    @staticmethod
    def decode_access_token(token: str) -> dict:
        """
        Validates and decodes a JWT access token payload.
        """

        try:
            decoded_token = jwt.decode(
                token,
                settings.app.JWT_PUBLIC_KEY,
                algorithms=[settings.app.JWT_ALGORITHM]
            )
            return decoded_token
        except jwt.ExpiredSignatureError as exc:
            msg = 'JwtToken: decode_access_token: ExpiredSignatureError'
            extra = {'token': token, 'error': str(exc)}
            logger.info(msg, extra=extra, exc_info=True)
            raise JWTExpiredException from exc
        except jwt.JWTError as exc:
            msg = 'JwtToken: decode_access_token: JWTError'
            extra = {'token': token, 'error': str(exc)}
            logger.info(msg, extra=extra, exc_info=True)
            raise JWTInvalidException from exc
        except Exception as exc:
            msg = 'JwtToken: decode_access_token: Unknown error'
            extra = {'token': token, 'error': str(exc)}
            logger.critical(msg, extra=extra)
            raise JWTCannotDecodeException from exc

    @classmethod
    def generate_refresh_token(cls) -> tuple[str, str]:
        """
        Generates a cryptographically secure refresh token pair.
        """

        try:
            raw_token = secrets.token_urlsafe(REFRESH_TOKEN_LENGTH)
            hashed_token = cls._pwd_context.hash(raw_token)
            return raw_token, hashed_token
        except Exception as exc:
            logger.critical('Refresh token generation failed')
            raise AppException('Refresh token generation failed', details=str(exc)) from exc

    @classmethod
    def verify_refresh_token(cls, raw_token: str, hashed_token: str) -> bool:
        """
        Validates a refresh token against its hash.
        """

        try:
            return cls._pwd_context.verify(raw_token, hashed_token)
        except Exception as exc:
            logger.warning(
                'Refresh token verification failed',
                extra={'error': str(exc)}
            )
            return False
