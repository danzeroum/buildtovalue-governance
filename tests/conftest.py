"""
Pytest fixtures e configurações globais
"""

import pytest
import os
from pathlib import Path
from datetime import timedelta

# Setup test environment
os.environ["JWT_SECRET"] = "test-secret-key-for-pytest"
os.environ["HMAC_KEY"] = "test-hmac-key-for-pytest"
os.environ["ENVIRONMENT"] = "test"

from src.interface.api.auth import create_access_token
from src.core.registry.system_registry import SystemRegistry
from src.domain.entities import AISystem
from src.domain.enums import AIRole, AISector, EUComplianceRisk


@pytest.fixture
def test_db():
    """Fixture para banco de dados de teste"""
    db_path = Path("./test_data/test_registry.db")
    db_path.parent.mkdir(exist_ok=True)

    registry = SystemRegistry(f"sqlite:///{db_path}")

    yield registry

    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def admin_token():
    """Fixture para token de admin"""
    return create_access_token(
        data={
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "admin@test.com",
            "role": "admin"
        },
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def dev_token():
    """Fixture para token de desenvolvedor"""
    return create_access_token(
        data={
            "tenant_id": "test-tenant-550e8400-e29b-41d4-a716-446655440000",
            "user_id": "dev@test.com",
            "role": "dev"
        },
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def malicious_token():
    """Fixture para token de outro tenant (para testar BOLA)"""
    return create_access_token(
        data={
            "tenant_id": "malicious-tenant-123e4567-e89b-12d3-a456-426614174000",
            "user_id": "attacker@evil.com",
            "role": "admin"
        },
        expires_delta=timedelta(hours=1)
    )


@pytest.fixture
def sample_system():
    """Fixture para sistema de IA de teste"""
    return AISystem(
        id="test-system-001",
        tenant_id="test-tenant-550e8400-e29b-41d4-a716-446655440000",
        name="Test AI System",
        version="1.0.0",
        role=AIRole.DEPLOYER,
        sector=AISector.BANKING,
        risk_classification=EUComplianceRisk.HIGH,
        logging_capabilities=True,
        eu_database_registration_id="EU-TEST-12345"
    )


@pytest.fixture
def sample_high_risk_system():
    """Fixture para sistema de alto risco"""
    return AISystem(
        id="high-risk-system",
        tenant_id="test-tenant-550e8400-e29b-41d4-a716-446655440000",
        name="High Risk Credit Scoring",
        version="2.0.0",
        role=AIRole.PROVIDER,
        sector=AISector.BANKING,
        risk_classification=EUComplianceRisk.HIGH,
        logging_capabilities=True,
        training_compute_flops=5e24,
        eu_database_registration_id="EU-HIGH-67890"
    )
