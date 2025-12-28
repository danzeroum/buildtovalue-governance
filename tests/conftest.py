# tests/conftest.py (CLEANUP FIX)

"""
Pytest fixtures and global configurations
"""

import sys
from pathlib import Path

# ✅ Add project root to sys.path to resolve 'src' imports
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
import os
from datetime import timedelta
import gc

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
    """Fixture for test database"""
    db_path = Path("./test_data/test_registry.db")
    db_path.parent.mkdir(exist_ok=True)

    registry = SystemRegistry(f"sqlite:///{db_path}")
    yield registry

    # ✅ FIX: More robust cleanup for Windows
    try:
        # Explicitly close connections
        if hasattr(registry, 'engine'):
            registry.engine.dispose()

        # Force garbage collection to release handles
        del registry
        gc.collect()

        # Wait a moment for Windows to release the file
        import time
        time.sleep(0.1)

        # Try to remove (if it fails, not critical)
        if db_path.exists():
            db_path.unlink()

    except PermissionError:
        # Ignore permission error on Windows (not critical for tests)
        pass
    except Exception as e:
        # Log other errors but don't fail the test
        print(f"Warning: Cleanup error: {e}")


@pytest.fixture
def admin_token():
    """Fixture for admin token"""
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
    """Fixture for developer token"""
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
    """Fixture for another tenant's token (to test BOLA)"""
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
    """Fixture for test AI system"""
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
    """Fixture for high-risk system"""
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
