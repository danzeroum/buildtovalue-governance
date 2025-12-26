"""
Testes Unitários - Runtime Enforcement Engine

ISO 42001 8.2 (AI Risk Assessment - Operation)
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.core.governance.enforcement import RuntimeEnforcementEngine
from src.domain.entities import Task, AISystem
from src.domain.enums import AIRole, AISector, EUComplianceRisk, ArtifactType


@pytest.fixture
def temp_config():
    """Cria configuração temporária para testes"""
    config_data = {
        "version": "7.3.0-test",
        "prohibited_practices": ["social_scoring"],
        "autonomy_matrix": {
            "development": {"max_risk_level": 8.0},
            "production": {"max_risk_level": 3.0}
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)

    yield config_path

    config_path.unlink()


@pytest.fixture
def enforcement_engine(temp_config):
    """Cria engine de enforcement para testes"""
    memory_path = Path(tempfile.mkdtemp())
    engine = RuntimeEnforcementEngine(temp_config, memory_path)

    yield engine

    # Cleanup
    import shutil
    shutil.rmtree(memory_path)


def test_low_risk_task_allowed_in_production(enforcement_engine, sample_system):
    """
    Testa que tarefas de baixo risco são permitidas em produção
    """
    task = Task(
        title="Generate documentation",
        artifact_type=ArtifactType.DOCUMENTATION
    )

    decision = enforcement_engine.enforce(task, sample_system, env="production")

    assert decision["decision"] == "ALLOWED"
    assert decision["risk_score"] < 3.0


def test_high_risk_task_blocked_in_production(enforcement_engine, sample_high_risk_system):
    """
    Testa que tarefas de alto risco são bloqueadas em produção
    """
    task = Task(
        title="Deploy biometric recognition with social scoring manipulation subliminal",
        artifact_type=ArtifactType.CODE
    )

    decision = enforcement_engine.enforce(task, sample_high_risk_system, env="production")

    assert decision["decision"] == "BLOCKED"
    assert decision["risk_score"] > 3.0
    assert decision["escalation_required"] is True


def test_sandbox_mode_increases_risk_tolerance(enforcement_engine, sample_system):
    """
    Testa que sandbox mode aumenta tolerância a risco

    Compliance: EU AI Act Art. 57 (Regulatory Sandbox)
    """
    sample_system.is_sandbox_mode = True

    task = Task(
        title="Experimental high-risk feature test",
        artifact_type=ArtifactType.CODE
    )

    decision = enforcement_engine.enforce(task, sample_system, env="production")

    # Sandbox deve ter limite aumentado (3.0 + 2.0 = 5.0)
    assert decision["limit"] == 5.0
