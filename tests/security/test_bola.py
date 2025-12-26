"""
Testes de Segurança - BOLA/IDOR (Broken Object Level Authorization)

OWASP API1:2023 - Broken Object Level Authorization
"""

import pytest
from src.core.registry.system_registry import SystemRegistry


def test_bola_cross_tenant_system_access(test_db, sample_system):
    """
    Testa que tenant A não pode acessar sistemas do tenant B

    Security: BOLA Protection
    """
    # Tenant A registra sistema
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    system_id = test_db.register_system(sample_system, tenant_a)

    # Tenant B tenta acessar (cross-tenant attack)
    tenant_b = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"

    result = test_db.get_system(system_id, tenant_b)

    # Deve retornar None (sem expor se sistema existe)
    assert result is None, "SECURITY BREACH: Cross-tenant access allowed!"


def test_bola_cross_tenant_policy_access(test_db):
    """
    Testa que tenant não pode acessar políticas de outros tenants

    Security: BOLA Protection
    """
    # Tenant A registra política sensível
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    sensitive_policy = {
        "autonomy_matrix": {
            "production": {"max_risk_level": 1.0}
        },
        "internal_secret": "confidential-data-xyz"
    }
    test_db.register_tenant(tenant_a, "Tenant A Corp", sensitive_policy)

    # Tenant B tenta acessar política de A
    tenant_b = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"

    policy = test_db.get_tenant_policy(tenant_a, requesting_tenant=tenant_b)

    # Deve retornar vazio (não expõe dados)
    assert policy == {}, "SECURITY BREACH: Cross-tenant policy access allowed!"


def test_mass_assignment_attack_prevention(test_db, sample_system):
    """
    Testa prevenção de Mass Assignment (tenant_id forging)

    Security: OWASP API6:2023 - Mass Assignment
    """
    # Atacante tenta forjar tenant_id no payload
    legitimate_tenant = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # Sistema afirma pertencer ao tenant legítimo
    sample_system.tenant_id = legitimate_tenant

    # Mas JWT token é de outro tenant
    attacker_tenant = "malicious-tenant-123e4567-e89b-12d3-a456-426614174000"

    # Tentativa de registro deve falhar
    with pytest.raises(ValueError) as exc_info:
        test_db.register_system(sample_system, requesting_tenant=attacker_tenant)

    assert "Tenant ID mismatch" in str(exc_info.value)
    assert "security attack" in str(exc_info.value).lower()


def test_list_systems_isolation(test_db, sample_system):
    """
    Testa que list_systems retorna apenas sistemas do próprio tenant

    Security: BOLA Protection
    """
    tenant_a = "test-tenant-550e8400-e29b-41d4-a716-446655440000"
    tenant_b = "other-tenant-123e4567-e89b-12d3-a456-426614174000"

    # Tenant A registra sistema
    sample_system.tenant_id = tenant_a
    test_db.register_system(sample_system, tenant_a)

    # Tenant B lista seus sistemas
    systems_b = test_db.list_systems_by_tenant(tenant_b)

    # Não deve conter sistemas de A
    assert len(systems_b) == 0, "SECURITY BREACH: Cross-tenant data leak in list!"


def test_sql_injection_via_system_id(test_db):
    """
    Testa proteção contra SQL Injection via system_id

    Security: OWASP API8:2023 - Security Misconfiguration
    """
    tenant = "test-tenant-550e8400-e29b-41d4-a716-446655440000"

    # Tentativa de SQL Injection
    malicious_system_id = "test' OR '1'='1"

    # Query não deve retornar nenhum resultado (parametrized query protege)
    result = test_db.get_system(malicious_system_id, tenant)

    assert result is None, "SECURITY BREACH: SQL Injection successful!"
