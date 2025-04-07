"""
Dependency provider for AuthService.
Constructs and provides authentication service with all required dependencies.
"""

from app.application.services import AuthService, SessionService, UserService
from app.lib.schemas.client_info_schema import ClientInfoSchema
from app.lib.security import JWTManager, PasswordManager

__all__ = ['provide_auth_service']


def provide_auth_service(
        user_service: UserService,
        session_service: SessionService,
        client_info: ClientInfoSchema
):
    """
    Factory function that creates configured AuthService instance.

    Args:
        user_service: User management service
        session_service: Session handling service
        client_info: Client context information

    Returns:
        AuthService: Configured authentication service
    """

    return AuthService(
        client_info=client_info,
        user_service=user_service,
        session_service=session_service,
        jwt_manager=JWTManager(),
        password_service=PasswordManager(),
    )
