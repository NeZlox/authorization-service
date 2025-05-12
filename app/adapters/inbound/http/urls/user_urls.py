"""
User management endpoint URL configurations.
Defines CRUD routes for user accounts.
"""

PREFIX = '/users'  # Base path for user management

GET_CURRENT_USER_URI = '/me'  # Current user profile
POST_REGISTER_USER_URI = '/register'  # Public user registration

# User CRUD endpoints
GET_USERS_URI = '/'  # List all users (admin only)
GET_USER_URI = '/{user_id:int}'  # Get specific user details
POST_USER_URI = '/'  # Register new user
PUT_USER_URI = '/{user_id:int}'  # Update user information
DELETE_USER_URI = '/{user_id:int}'  # Deactivate/delete user account
