"""
Application-wide constants and configuration values.
"""

# API Configuration
API_BASE_PATH: str = '/api'  # Base path for all API endpoints

# Authentication Constants
AUTH_ACCESS_TOKEN_KEY: str = 'psg_access_token'  # Cookie name for access token      # noqa: S105
AUTH_REFRESH_TOKEN_KEY: str = 'psg_refresh_token'  # Cookie name for refresh token   # noqa: S105
REFRESH_TOKEN_LENGTH: int = 64  # Length of generated refresh tokens
MAX_ACTIVE_REFRESH_SESSIONS: int = 5  # Max concurrent sessions per user

# Application Settings
DEFAULT_PAGINATION_SIZE: int = 20  # Default page size for paginated endpoints
