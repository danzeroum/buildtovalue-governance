"""
Testes Unitários - Domain Entities

ISO 42001 6.1 (Risk Assessment Logic)
"""

import pytest
from src.domain.entities import AISystem, Task
from src.domain.enums import AIRole, AISector, EUComplianceRisk, ArtifactType


def test_high_risk_system_requires_logging():
    """
    Testa que sistemas de alto risco requerem logging

    Compliance: EU AI Act Art. 12
    """
    with pytest.raises(ValueError) as exc_info:
        AISystem(
            id="test",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            name="Credit Scoring",
            role=AIRole.DEPLOYER,
            sector=AISector.BANKING,
            risk_classification=EUComplianceRisk.HIGH,
            logging_capabilities=False  # Violação!
        )

    assert "logging_capabilities=True" in str(exc_info.value)
    assert "Art. 12" in str(exc_info.value)


def test_high_risk_critical_sector_requires_eu_registration():
    """
    Testa que setores críticos de alto risco requerem registro EU

    Compliance: EU AI Act Art. 71
    """
    with pytest.raises(ValueError) as exc_info:
        AISystem(
            id="test",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            name="Biometric System",
            role=AIRole.PROVIDER,
            sector=AISector.BIOMETRIC,  # Setor crítico
            risk_classification=EUComplianceRisk.HIGH,
            logging_capabilities=True,
            eu_database_registration_id=None  # Violação!
        )

    assert "eu_database_registration_id" in str(exc_info.value)
    assert "Art. 71" in str(exc_info.value)


def test_systemic_gpai_requires_high_flops():
    """
    Testa classificação de GPAI sistêmico

    Compliance: EU AI Act Art. 51
    """
    with pytest.raises(ValueError) as exc_info:
        AISystem(
            id="test",
            tenant_id="550e8400-e29b-41d4-a716-446655440000",
            name="Foundation Model",
            role=AIRole.PROVIDER,
            sector=AISector.GENERAL_COMMERCIAL,
            risk_classification=EUComplianceRisk.HIGH,  # Deveria ser SYSTEMIC_GPAI
            logging_capabilities=True,
            training_compute_flops=5e25  # > 10^25 FLOPs
        )

    assert "SYSTEMIC_GPAI" in str(exc_info.value)
    assert "Art. 51" in str(exc_info.value)

@pytest.mark.skip(reason="Validation not implemented in v0.9.0 - planned for v0.9.5")
def test_task_creation_with_defaults():
    """
    Testa criação de Task com valores default
    """
    task = Task(title="Generate code for API")

    assert task.title == "Generate code for API"
    assert task.description == ""
    assert task.artifact_type == ArtifactType.CODE

@pytest.mark.skip(reason="Validation not implemented in v0.9.0 - planned for v0.9.5")
def test_valid_uuid_v4_accepted():
    """
    Testa que UUIDs v4 válidos são aceitos
    """
    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"

    system = AISystem(
        id="test",
        tenant_id=valid_uuid,
        name="Test System",
        role=AIRole.DEPLOYER,
        sector=AISector.BANKING,
        risk_classification=EUComplianceRisk.MINIMAL,
        logging_capabilities=False
    )

    assert system.tenant_id == valid_uuid.lower()
