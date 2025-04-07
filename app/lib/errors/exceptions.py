"""
Application-specific exception classes.
Organized by error categories with proper HTTP status codes.
"""

from typing import Any

from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class AppException(Exception):  # noqa: N818 - сохранено для обратной совместимости
    """
    Base exception class for application errors.
    """

    def __init__(self, message: str = "", details: Any = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)


# Authentication/Authorization Exceptions
class JWTException(AppException):
    """
    Base JWT-related exception.
    """

    status_code = HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', "")
        super().__init__(message=message, details=details)


class JWTAbsentException(JWTException):
    """
    Raised when JWT token is missing.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Authorization token is missing'


class JWTCannotEncodeException(JWTException):
    """
    Raised when JWT encoding fails.
    """

    message = 'Failed to encode JWT token'


class JWTCannotDecodeException(JWTException):
    """
    Raised when JWT decoding fails.
    """

    message = 'Failed to decode JWT token'


class JWTExpiredException(JWTException):
    """
    Raised when JWT token has expired.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Token has expired'


class JWTInvalidException(JWTException):
    """
    Raised when JWT token is invalid.
    """

    status_code = HTTP_401_UNAUTHORIZED
    message = 'Invalid token'


# User-related Exceptions
class UserException(AppException):
    """
    Base user-related exception.
    """

    status_code = HTTP_400_BAD_REQUEST
    message = 'Ошибка пользователя'

    def __init__(self, message: str | None = None, details: Any = None):
        message = message or getattr(self, 'message', "")
        super().__init__(message=message, details=details)


class UserAlreadyExistsByEmailException(UserException):
    """
    Raised when email already exists.
    """

    status_code = HTTP_409_CONFLICT
    message = 'User with this email already exists'


class UserAlreadyExistsByUsernameException(UserException):
    """
    Raised when username already exists.
    """

    status_code = HTTP_409_CONFLICT
    message = 'User with this username already exists'


class UserNotExistsException(UserException):
    """
    Raised when user is not found.
    """

    status_code = HTTP_404_NOT_FOUND
    message = 'User not found'


class UserInvalidCredentialsException(UserException):
    """
    Raised on invalid login credentials.
    """

    status_code = HTTP_404_NOT_FOUND
    message = 'Invalid credentials'


class UserAccessDeniedException(UserException):
    """
    Raised when user lacks permissions.
    """

    status_code = HTTP_403_FORBIDDEN
    message = 'Insufficient permissions'
