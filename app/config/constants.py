"""
Application-wide constants and configuration values.
"""

# API Configuration
API_BASE_PATH: str = '/api'  # Base path for all API endpoints

# Authentication Constants
REFRESH_TOKEN_LENGTH: int = 64  # Length of generated refresh tokens
MAX_ACTIVE_REFRESH_SESSIONS: int = 5  # Max concurrent sessions per user

# Application Settings
DEFAULT_PAGINATION_SIZE: int = 20  # Default page size for paginated endpoints
