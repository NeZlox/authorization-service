"""
Authentication endpoint URL configurations.
Defines routes for session management and token operations.
"""

PREFIX = '/auth'                        # Base path for all authentication endpoints

# Session management endpoints
POST_SESSIONS       = '/sessions'       # Login - Create new session and get tokens
PUT_SESSIONS        = '/sessions'       # Refresh - Renew access token using refresh token
DELETE_SESSIONS     = '/sessions'       # Logout - Revoke current session tokens
DELETE_SESSIONS_ALL = '/sessions/all'   # Global logout - Revoke all active sessions
