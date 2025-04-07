"""
Core authentication and authorization service.
Handles user login, session management and token operations.
"""

import datetime

import msgspec
from personal_growth_sdk.authorization.models import Session, User
from personal_growth_sdk.authorization.schemas import (
    SessionCreateRequest,
    SessionResponse,
    SessionUpdateRequest,
    UserResponse,
)
from personal_growth_sdk.authorization.schemas.user_schema import UserLoginRequest
from sqlalchemy.orm import selectinload

from app.application.services.session_service import SessionService
from app.application.services.user_service import UserService
from app.config.base_settings import get_settings
from app.lib.errors.exceptions import JWTExpiredException, UserInvalidCredentialsException, UserNotExistsException
from app.lib.schemas.client_info_schema import ClientInfoSchema
from app.lib.schemas.token_payload import TokenPayloadSchema
from app.lib.security import JWTManager, PasswordManager

__all__ = ['AuthService']

settings = get_settings()


class TokenSchema(msgspec.Struct):
    """
    Container for authentication tokens
    """

    access_token: str
    refresh_token: str


class AuthService:
    """
    Main service for authentication operations.

    Dependencies:
        client_info: Client context information
        user_service: User management service
        session_service: Session handling service
        jwt_manager: JWT token utilities
        password_service: Password hashing/verification
    """

    def __init__(
            self,
            client_info: ClientInfoSchema,
            user_service: UserService,
            session_service: SessionService,
            jwt_manager: JWTManager,
            password_service: PasswordManager,
    ):
        self.client_info = client_info
        self.user_service = user_service
        self.session_service = session_service
        self.jwt_manager = jwt_manager
        self.password_service = password_service

    async def login(self, data: UserLoginRequest) -> tuple[UserResponse, TokenSchema]:
        """
        Authenticates user and generates new tokens.

        Args:
            data: User credentials (email/password)

        Returns:
            tuple: User details and authentication tokens

        Raises:
            UserNotExistsException: If user not found
            UserInvalidCredentialsException: If password invalid
        """

        # User lookup and validation
        user_model = await self.user_service.get_one_or_none(
            User.email == data.email
        )
        if user_model is None:
            raise UserNotExistsException
        user_schema = self.user_service.to_schema(data=user_model, schema_type=UserResponse)

        if not self.password_service.verify(data.password, user_model.password):
            raise UserInvalidCredentialsException

        # Token generation
        payload = TokenPayloadSchema(
            sub=str(user_schema.id),
            exp=(datetime.datetime.now(datetime.UTC)
                 + datetime.timedelta(minutes=settings.app.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)),
            role=user_schema.role
        )
        access_token = self.jwt_manager.generate_access_token(msgspec.to_builtins(payload))
        raw_token, hash_refresh_token = self.jwt_manager.generate_refresh_token()

        refresh_token_expires_at = (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=settings.app.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )

        flag_updated = False
        if self.client_info.refresh_token:
            sessions = await self.session_service.list(
                Session.user_id == user_schema.id
            )
            for session in sessions:
                if self.jwt_manager.verify_refresh_token(
                        raw_token=self.client_info.refresh_token, hashed_token=session.refresh_token
                ):
                    await self.session_service.update(
                        item_id=session.id,
                        data=SessionUpdateRequest(
                            refresh_token=hash_refresh_token,
                            expires_at=refresh_token_expires_at,
                            user_agent=self.client_info.user_agent,
                            fingerprint=self.client_info.fingerprint,
                            ip=self.client_info.ip,
                        )
                    )
                    flag_updated = True
                    break

        if not flag_updated:
            await self.session_service.create(
                SessionCreateRequest(
                    refresh_token=hash_refresh_token,
                    expires_at=refresh_token_expires_at,
                    user_agent=self.client_info.user_agent,
                    fingerprint=self.client_info.fingerprint,
                    ip=self.client_info.ip,
                    user_id=user_schema.id
                )
            )
            await self.session_service.enforce_session_limit(user_id=user_schema.id)

        return user_schema, TokenSchema(access_token=access_token, refresh_token=raw_token)

    async def refresh_session(self, user_id: int) -> TokenSchema:
        """
        Refreshes expired access token using valid refresh token.

        Args:
            user_id: ID of user requesting refresh

        Returns:
            TokenSchema: New set of tokens

        Raises:
            UserInvalidCredentialsException: If invalid refresh token
            JWTExpiredException: If refresh token expired
        """

        if self.client_info.refresh_token is None:
            raise UserInvalidCredentialsException
        sessions = await self.session_service.list(
            Session.user_id == user_id,
            load=selectinload(Session.user)
        )
        session_schema = None
        for session in sessions:
            if self.jwt_manager.verify_refresh_token(
                    raw_token=self.client_info.refresh_token, hashed_token=session.refresh_token
            ):
                session_schema = self.session_service.to_schema(data=session, schema_type=SessionResponse)
                break

        if session_schema is None:
            raise UserInvalidCredentialsException

        if datetime.datetime.now(datetime.UTC) >= session_schema.expires_at:
            await self.session_service.delete(item_id=session_schema.id)
            raise JWTExpiredException

        # Generate new tokens
        payload = TokenPayloadSchema(
            sub=str(session_schema.user_id),
            exp=(datetime.datetime.now(datetime.UTC)
                 + datetime.timedelta(minutes=settings.app.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)),
            role=session_schema.user.role
        )
        access_token = self.jwt_manager.generate_access_token(msgspec.to_builtins(payload))
        raw_token, hash_refresh_token = self.jwt_manager.generate_refresh_token()

        refresh_token_expires_at = (
                datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(days=settings.app.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )

        await self.session_service.update(
            item_id=session_schema.id,
            data=SessionUpdateRequest(
                refresh_token=hash_refresh_token,
                expires_at=refresh_token_expires_at,
                user_agent=self.client_info.user_agent,
                fingerprint=self.client_info.fingerprint,
                ip=self.client_info.ip,
            )
        )
        return TokenSchema(access_token=access_token, refresh_token=raw_token)

    async def revoke_session(self, user_id: int) -> None:
        """
        Terminates specific user session.

        Args:
            user_id: User whose session to revoke

        Raises:
            UserInvalidCredentialsException: If session not found
        """

        sessions = await self.session_service.list(
            Session.user_id == user_id
        )
        for session in sessions:
            if self.jwt_manager.verify_refresh_token(
                    raw_token=self.client_info.refresh_token, hashed_token=session.refresh_token
            ):
                await self.session_service.delete(item_id=session.id)
                return
        raise UserInvalidCredentialsException

    async def revoke_all_sessions(self, id_user: int) -> None:
        """
        Terminates all active sessions for user.
        """

        await self.session_service.delete_where(Session.user_id == id_user)
