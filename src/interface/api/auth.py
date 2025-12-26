"""
Authentication and Authorization (JWT + RBAC)

Implementa:
- ISO 42001 B.4.6 (Human Resources - Access Control)
- JWT tokens with short expiration
- Role-Based Access Control (4 roles)
"""

import os
from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import logging

logger = logging.getLogger("btv.auth")

# Configuração JWT
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
    Dados extraídos do JWT token

    Attributes:
        tenant_id: UUID do tenant (para isolamento multi-tenant)
        user_id: ID do usuário
        role: Role RBAC (admin, dev, auditor, app)
        exp: Timestamp de expiração
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
    Cria JWT access token

    Args:
        data: Payload do token (tenant_id, user_id, role)
        expires_delta: Tempo até expiração

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
    expire = datetime.utcnow() + expires_delta
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
    Verifica e decodifica JWT token

    Args:
        credentials: Bearer token do header Authorization

    Returns:
        TokenData com claims validados

    Raises:
        HTTPException 401: Token inválido, expirado ou claims ausentes

    Security:
        Previne Authentication Bypass via claim validation
    """
    token = credentials.credentials

    try:
        # Decodifica token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # CRITICAL: Validação de Claims Obrigatórios
        required_claims = ["tenant_id", "user_id", "role", "exp"]
        missing_claims = [c for c in required_claims if c not in payload]

        if missing_claims:
            logger.warning(
                f"Token with missing claims: {missing_claims}"
            )
            raise HTTPException(
                status_code=401,
                detail=f"Token inválido: claims ausentes ({', '.join(missing_claims)})"
            )

        return TokenData(**payload)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )


def require_role(allowed_roles: List[str]):
    """
    Decorator para RBAC (Role-Based Access Control)

    Args:
        allowed_roles: Lista de roles permitidas (admin, dev, auditor, app)

    Returns:
        Dependency que valida role do token

    Example:
        @app.post("/admin-only")
        async def admin_endpoint(
        ... ):
        ...     token: TokenData = Depends(require_role(["admin"]))
        ...     return {"message": "Admin access granted"}

    Security:
        Previne Privilege Escalation
        Compliance: ISO 42001 B.4.6 (Access Control)
    """

    def dependency(token: TokenData = Depends(verify_jwt_token)):
        if token.role not in allowed_roles:
            logger.warning(
                f"Access denied: user {token.user_id} (role={token.role}) "
                f"tried to access resource requiring roles: {allowed_roles}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado: role '{token.role}' não autorizada. "
                       f"Roles permitidas: {', '.join(allowed_roles)}"
            )
        return token

    return dependency
