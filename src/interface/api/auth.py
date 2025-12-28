"""
Authentication and Authorization (JWT + RBAC)

Implements:
- ISO 42001 B.4.6 (Human Resources - Access Control)
- JWT tokens with short expiration
- Role-Based Access Control (4 roles)

✅ UPDATED: Fixed datetime.utcnow() deprecation (Python 3.12+)
"""

import os
from datetime import datetime, timedelta, UTC  # ✅ ADDED UTC
from typing import List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import logging

logger = logging.getLogger("btv.auth")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-change-me-in-prod")
ALGORITHM = "HS256"
DEFAULT_EXPIRATION_MINUTES = 30

if SECRET_KEY == "super-secret-key-change-me-in-prod":
    logger.warning(
        "⚠️  USING DEFAULT JWT SECRET! Set JWT_SECRET environment variable in production!"
    )

security = HTTPBearer()


class TokenData(BaseModel):
    """
    Data extracted from JWT token

    Attributes:
        tenant_id: Tenant UUID (for multi-tenant isolation)
        user_id: User ID
        role: RBAC role (admin, dev, auditor, app)
        exp: Expiration timestamp
    """
    tenant_id: str
    user_id: str
    role: str
    exp: int


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=DEFAULT_EXPIRATION_MINUTES)
) -> str:
    """
    Create JWT access token

    Args:
        data: Token payload (tenant_id, user_id, role)
        expires_delta: Time until expiration

    Returns:
        JWT token string

    Example:
        >>> token = create_access_token({
        ...     "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        ...     "user_id": "admin@company.com",
        ...     "role": "admin"
        ... })
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta  # ✅ FIXED: was datetime.utcnow()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(
        f"Token created for user {data.get('user_id')} "
        f"(role: {data.get('role')}, tenant: {data.get('tenant_id')})"
    )

    return encoded_jwt


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> TokenData:
    """
    Verify and decode JWT token

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        TokenData with validated claims

    Raises:
        HTTPException 401: Invalid, expired token or missing claims

    Security:
        Prevents Authentication Bypass via claim validation
    """
    token = credentials.credentials

    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # CRITICAL: Required Claims Validation
        required_claims = ["tenant_id", "user_id", "role", "exp"]
        missing_claims = [c for c in required_claims if c not in payload]

        if missing_claims:
            logger.warning(
                f"Token with missing claims: {missing_claims}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: missing claims ({', '.join(missing_claims)})"
            )

        return TokenData(**payload)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def require_role(allowed_roles: List[str]):
    """
    Decorator for RBAC (Role-Based Access Control)

    Args:
        allowed_roles: List of allowed roles (admin, dev, auditor, app)

    Returns:
        Dependency that validates token role

    Example:
        @app.post("/admin-only")
        async def admin_endpoint(
            token: TokenData = Depends(require_role(["admin"]))
        ):
            return {"message": "Admin access granted"}

    Security:
        Prevents Privilege Escalation

    Compliance:
        ISO 42001 B.4.6 (Access Control)
    """
    def dependency(token: TokenData = Depends(verify_jwt_token)):
        if token.role not in allowed_roles:
            logger.warning(
                f"Access denied: user {token.user_id} (role={token.role}) "
                f"tried to access resource requiring roles: {allowed_roles}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: role '{token.role}' not authorized. "
                       f"Allowed roles: {', '.join(allowed_roles)}"
            )
        return token

    return dependency
