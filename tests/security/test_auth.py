"""
Testes de Segurança - Authentication & Authorization

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


def test_jwt_token_validation_success(admin_token):
    """
    Testa validação de token JWT válido

    Security: Authentication
    """
    from fastapi.security import HTTPAuthorizationCredentials

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=admin_token
    )

    # Deve validar sem exceções
    token_data = pytest.importasync(verify_jwt_token(credentials))

    assert token_data.role == "admin"
    assert "test-tenant" in token_data.tenant_id


def test_jwt_token_missing_claims():
    """
    Testa rejeição de token com claims faltantes

    Security: OWASP API2:2023
    """
    # Token sem claim 'role'
    incomplete_token = jwt.encode(
        {
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user@test.com"
            # 'role' ausente!
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=incomplete_token
    )

    # Deve lançar HTTPException 401
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        pytest.importasync(verify_jwt_token(credentials))

    assert exc_info.value.status_code == 401
    assert "claims ausentes" in str(exc_info.value.detail)


def test_rbac_privilege_escalation_prevention():
    """
    Testa prevenção de privilege escalation

    Security: OWASP API5:2023
    """
    # Usuário dev tenta acessar recurso admin-only
    dev_token_data = type('TokenData', (), {
        'tenant_id': 'test-tenant',
        'user_id': 'dev@test.com',
        'role': 'dev'
    })()

    # Decorator que exige role 'admin'
    admin_only = require_role(["admin"])

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        admin_only(dev_token_data)

    assert exc_info.value.status_code == 403
    assert "não autorizada" in str(exc_info.value.detail)


def test_expired_token_rejection():
    """
    Testa que tokens expirados são rejeitados

    Security: Token Expiration
    """
    # Token que expira imediatamente
    expired_token = create_access_token(
        data={
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "user@test.com",
            "role": "admin"
        },
        expires_delta=timedelta(seconds=-1)  # Já expirado
    )

    from fastapi.security import HTTPAuthorizationCredentials
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=expired_token
    )

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        pytest.importasync(verify_jwt_token(credentials))

    assert exc_info.value.status_code == 401
