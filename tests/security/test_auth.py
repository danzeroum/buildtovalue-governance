# tests/security/test_auth.py (COMPLETE FIXED VERSION)

"""
Security Tests - Authentication & Authorization

OWASP API2:2023 - Broken Authentication
OWASP API5:2023 - Broken Function Level Authorization
"""

import pytest
from datetime import timedelta
from jose import jwt
from src.interface.api.auth import (
    create_access_token,
    verify_jwt_token,
    require_role,
    SECRET_KEY,
    ALGORITHM
)


@pytest.mark.asyncio
async def test_jwt_token_validation_success(admin_token):
    """
    Test valid JWT token validation

    Security: Authentication
    """
    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=admin_token
    )

    # ✅ FIX: verify_jwt_token is async
    token_data = await verify_jwt_token(credentials)
    assert token_data.role == "admin"
    assert "test-tenant" in token_data.tenant_id


@pytest.mark.asyncio
async def test_jwt_token_missing_claims():
    """
    Test rejection of token with missing claims

    Security: OWASP API2:2023
    """
    # Token without 'role' claim
    incomplete_token = jwt.encode(
        {
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user@test.com"
            # 'role' missing!
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=incomplete_token
    )

    # Should raise HTTPException 401
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt_token(credentials)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_rejection():
    """
    Test that expired tokens are rejected

    Security: Token Expiration
    """
    # Token that expires immediately
    expired_token = create_access_token(
        data={
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user@test.com",
            "role": "admin"
        },
        expires_delta=timedelta(seconds=-1)  # Already expired
    )

    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=expired_token
    )

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_jwt_token(credentials)

    assert exc_info.value.status_code == 401


def test_rbac_privilege_escalation_prevention():
    """
    Test prevention of privilege escalation

    Security: OWASP API5:2023
    """
    # Dev user attempts to access admin-only resource
    dev_token_data = type('TokenData', (), {
        'tenant_id': 'test-tenant',
        'user_id': 'dev@test.com',
        'role': 'dev'
    })()

    # Decorator that requires 'admin' role
    admin_only = require_role(["admin"])

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        admin_only(dev_token_data)

    assert exc_info.value.status_code == 403
