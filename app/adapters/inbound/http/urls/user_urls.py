"""
User management endpoint URL configurations.
Defines CRUD routes for user accounts.
"""

PREFIX = '/users'                    # Base path for user management

# User CRUD endpoints
GET_USERS_URI   = '/'                # List all users (admin only)
GET_USER_URI    = '/{user_id:int}'   # Get specific user details
POST_USER_URI   = '/'                # Register new user
PUT_USER_URI    = '/{user_id:int}'   # Update user information
DELETE_USER_URI = '/{user_id:int}'   # Deactivate/delete user account
