"""API module - REST API and authentication"""

from .gateway import app
from .auth import create_access_token, verify_jwt_token, require_role, TokenData

__all__ = [
    "app",
    "create_access_token",
    "verify_jwt_token",
    "require_role",
    "TokenData",
]
