"""
Refresh session management URL configurations.
Defines CRUD routes for refresh token sessions.
"""

PREFIX = '/sessions'                       # Base path for session management

# Session CRUD endpoints
GET_SESSIONS_URI   = '/'                   # List all active sessions
GET_SESSION_URI    = '/{session_id:int}'   # Get specific session details
POST_SESSION_URI   = '/'                   # Create new session (admin only)
PUT_SESSION_URI    = '/{session_id:int}'   # Update session
DELETE_SESSION_URI = '/{session_id:int}'   # Terminate session
