"""
Security Tests - BOLA/IDOR (Broken Object Level Authorization)

OWASP API1:2023 - Broken Object Level Authorization
"""

import pytest
from src.core.registry.system_registry import SystemRegistry


def test_bola_cross_tenant_system_access(test_db, sample_system):
    """
    Test that tenant A cannot access tenant B's systems

    Security: BOLA Protection
    """
    # Tenant A registers system
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    system_id = test_db.register_system(sample_system, tenant_a)

    # Tenant B attempts access (cross-tenant attack)
    tenant_b = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"
    result = test_db.get_system(system_id, tenant_b)

    # Should return None (without exposing if system exists)
    assert result is None, "SECURITY BREACH: Cross-tenant access allowed!"


def test_bola_cross_tenant_policy_access(test_db):
    """
    Test that tenant cannot access other tenants' policies

    Security: BOLA Protection
    """
    # Tenant A registers sensitive policy
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    sensitive_policy = {
        "autonomy_matrix": {
            "production": {"max_risk_level": 1.0}
        },
        "internal_secret": "confidential-data-xyz"
    }

    test_db.register_tenant(tenant_a, "Tenant A Corp", sensitive_policy)

    # Tenant B attempts to access A's policy
    tenant_b = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"
    policy = test_db.get_tenant_policy(tenant_a, requesting_tenant=tenant_b)

    # Should return empty (does not expose data)
    assert policy == {}, "SECURITY BREACH: Cross-tenant policy access allowed!"


def test_mass_assignment_attack_prevention(test_db, sample_system):
    """
    Test prevention of Mass Assignment (tenant_id forging)

    Security: OWASP API6:2023 - Mass Assignment
    """
    # Attacker attempts to forge tenant_id in payload
    legitimate_tenant = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # System claims to belong to legitimate tenant
    sample_system.tenant_id = legitimate_tenant

    # But JWT token is from another tenant
    attacker_tenant = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"

    # Registration attempt should fail
    with pytest.raises(ValueError) as exc_info:
        test_db.register_system(sample_system, requesting_tenant=attacker_tenant)

    assert "Tenant ID mismatch" in str(exc_info.value)
    assert "security attack" in str(exc_info.value).lower()


def test_list_systems_isolation(test_db, sample_system):
    """
    Test that list_systems returns only the tenant's own systems

    Security: BOLA Protection
    """
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    tenant_b = "other-tenant-123e4567-e89b-12d3-a456-426614174000"

    # Tenant A registers system
    sample_system.tenant_id = tenant_a
    test_db.register_system(sample_system, tenant_a)

    # Tenant B lists their systems
    systems_b = test_db.list_systems_by_tenant(tenant_b)

    # Should not contain A's systems
    assert len(systems_b) == 0, "SECURITY BREACH: Cross-tenant data leak in list!"


def test_sql_injection_via_system_id(test_db):
    """
    Test protection against SQL Injection via system_id

    Security: OWASP API8:2023 - Security Misconfiguration
    """
    tenant = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # SQL Injection attempt
    malicious_system_id = "test' OR '1'='1"

    # Query should not return any results (parameterized query protects)
    result = test_db.get_system(malicious_system_id, tenant)

    assert result is None, "SECURITY BREACH: SQL Injection successful!"
