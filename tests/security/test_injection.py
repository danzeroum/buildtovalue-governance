"""
Security Tests - SQL Injection and Input Validation

OWASP API8:2023 - Security Misconfiguration
"""

import pytest
from src.core.registry.system_registry import SystemRegistry
from src.domain.entities import AISystem
from src.domain.enums import AIRole, AISector, EUComplianceRisk


def test_sql_injection_in_tenant_name(test_db):
    """
    Test SQL Injection via tenant name

    Security: SQL Injection Prevention
    """
    tenant_id = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # Name with malicious SQL payload
    malicious_name = "Legit Corp'; DROP TABLE tenants; --"

    # Register (SQLAlchemy ORM should sanitize)
    test_db.register_tenant(tenant_id, malicious_name, {})

    # Verify that table still exists
    policy = test_db.get_tenant_policy(tenant_id, tenant_id)
    assert policy == {}, "SQL Injection: Table might be dropped!"


def test_json_injection_in_policy(test_db):
    """
    Test JSON Injection via policy field

    Security: OWASP API8:2023
    """
    tenant_id = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # Policy with JSON injection attempt
    malicious_policy = {
        "autonomy_matrix": {
            "production": {"max_risk_level": "'; DROP TABLE ai_systems; --"}
        }
    }

    # Should fail validation or be sanitized
    try:
        test_db.register_tenant(tenant_id, "Test Corp", malicious_policy)

        # If it passed, verify data is correct
        retrieved = test_db.get_tenant_policy(tenant_id, tenant_id)
        assert isinstance(retrieved, dict)

    except (ValueError, TypeError):
        # Expected validation failure
        pass


@pytest.mark.skip(reason="UUID validation not enforced in v0.9.0 - planned for v0.9.5")
def test_uuid_validation_rejects_invalid_format():
    """
    Test that invalid UUIDs are rejected

    Security: Input Validation
    """
    invalid_uuids = [
        "not-a-uuid",
        "123",
        "550e8400-XXXX-41d4-a716-446655440000",  # Invalid UUID v4
        "'; DROP TABLE ai_systems; --",
        "../../../etc/passwd",
        "550e8400-e29b-51d4-a716-446655440000"  # UUID v5 (not v4)
    ]

    for invalid_uuid in invalid_uuids:
        with pytest.raises(ValueError) as exc_info:
            AISystem(
                id="test",
                tenant_id=invalid_uuid,  # Invalid UUID
                name="Test",
                role=AIRole.DEPLOYER,
                sector=AISector.BANKING,
                risk_classification=EUComplianceRisk.MINIMAL,
                logging_capabilities=True
            )

        assert "UUID v4" in str(exc_info.value)


def test_path_traversal_in_system_id(test_db):
    """
    Test protection against Path Traversal

    Security: Path Traversal Prevention
    """
    tenant = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # Path traversal attempts
    malicious_ids = [
        "../../../etc/passwd",
        "..\\..\\windows\\system32",
        "/etc/shadow",
        "C:\\Windows\\System32\\config\\SAM"
    ]

    for malicious_id in malicious_ids:
        result = test_db.get_system(malicious_id, tenant)
        assert result is None, f"Path traversal vulnerability with: {malicious_id}"
