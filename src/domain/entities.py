"""
Entidades de domínio do BuildToValue
ISO 42001 compliant entity models
"""

from typing import List, Optional, Dict, Any
import re
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from .enums import AIRole, EUComplianceRisk, AISector, ArtifactType


class Task(BaseModel):
    """
    Representação de uma tarefa/prompt submetida ao sistema de IA

    Attributes:
        title: Título ou conteúdo da tarefa
        description: Descrição detalhada (opcional)
        artifact_type: Tipo de artefato a ser gerado
    """
    title: str
    description: str = ""
    artifact_type: ArtifactType = Field(default=ArtifactType.CODE)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Gerar relatório financeiro trimestral",
                "description": "Análise de receitas Q3 2024",
                "artifact_type": "documentation"
            }
        }
    )


class AISystem(BaseModel):
    """
    Representação Segura do Sistema de IA (EU AI Act + ISO 42001)

    Implementa:
    - Art. 6 EU AI Act (Risk Classification)
    - Art. 11 EU AI Act (Technical Documentation)
    - Art. 51 EU AI Act (GPAI Systemic Risk)
    - ISO 42001 4.1 (Context of Organization)
    """

    id: str = Field(..., description="Identificador único do sistema")
    name: str = Field(..., description="Nome do sistema de IA")
    version: str = Field(default="1.0.0", description="Versão do sistema")
    role: AIRole = Field(..., description="Papel na cadeia de IA (Art. 28)")
    risk_classification: EUComplianceRisk = Field(
        ...,
        description="Classificação de risco (Art. 6)"
    )
    sector: AISector = Field(..., description="Setor de aplicação (Anexo III)")

    # Multi-tenancy Hardened (BOLA Protection)
    tenant_id: str = Field(
        ...,
        description="ID da organização (UUID v4 obrigatório)"
    )

    # Políticas de Governança
    governance_policy: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Política específica do sistema (Camada 3)"
    )

    # Compliance e Rastreabilidade
    jurisdiction: str = Field(
        default="EU",
        description="Jurisdição legal (EU, US, BR, etc.)"
    )
    high_risk_flags: List[str] = Field(
        default_factory=list,
        description="Flags de alto risco identificadas"
    )
    eu_database_registration_id: Optional[str] = Field(
        default=None,
        description="ID de registro na EU Database (Art. 71)"
    )

    # Capacidades Técnicas (ISO 42001 7.2 - Competence)
    logging_capabilities: bool = Field(
        default=False,
        description="Sistema possui capacidade de logging (Art. 12)"
    )
    training_compute_flops: Optional[float] = Field(
        default=None,
        description="FLOPs de treinamento (Art. 51 - GPAI)"
    )

    # Sandbox Mode (Art. 57 EU AI Act)
    is_sandbox_mode: bool = Field(
        default=False,
        description="Sistema em modo sandbox regulatório"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "credit-scoring-v2",
                "name": "Credit Risk Scoring AI",
                "version": "2.1.0",
                "role": "deployer",
                "risk_classification": "high",
                "sector": "banking",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "jurisdiction": "EU",
                "high_risk_flags": [],
                "eu_database_registration_id": "EU-DB-12345",
                "logging_capabilities": True,
                "training_compute_flops": 1e24,
                "is_sandbox_mode": False
            }
        }
    )

    @field_validator('tenant_id')
    @classmethod
    def validate_tenant_uuid(cls, v: str) -> str:
        """
        Valida que tenant_id é UUID v4 válido (Mass Assignment Protection)

        Previne: Tenant ID forgery attacks
        Compliance: ISO 42001 B.4.6 (Human Resources - Access Control)
        """
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError(
                f"tenant_id deve ser UUID v4 válido, recebido: {v}. "
                f"Use: import uuid; str(uuid.uuid4())"
            )
        return v.lower()

    @model_validator(mode='after')
    def check_systemic_risk(self) -> 'AISystem':
        """
        Valida classificação de GPAI sistêmico (Art. 51 EU AI Act)

        Sistemas com FLOPs > 10^25 devem ser classificados como SYSTEMIC_GPAI
        """
        threshold = 1e25
        if self.training_compute_flops and self.training_compute_flops > threshold:
            if self.risk_classification != EUComplianceRisk.SYSTEMIC_GPAI:
                raise ValueError(
                    f"Sistema com {self.training_compute_flops:.2e} FLOPs (> 10^25) "
                    f"requer classificação SYSTEMIC_GPAI (Art. 51 EU AI Act). "
                    f"Classificação atual: {self.risk_classification.value}"
                )
        return self

    @model_validator(mode='after')
    def validate_high_risk_requirements(self) -> 'AISystem':
        """
        Valida requisitos adicionais para sistemas de alto risco (Art. 6)
        """
        if self.risk_classification == EUComplianceRisk.HIGH:
            # Sistemas de alto risco DEVEM ter logging (Art. 12)
            if not self.logging_capabilities:
                raise ValueError(
                    f"Sistemas de ALTO RISCO devem ter logging_capabilities=True "
                    f"(Art. 12 EU AI Act - Logging)"
                )

            # Setores de alto risco devem ter registro EU
            high_risk_sectors = [
                AISector.BIOMETRIC,
                AISector.LAW_ENFORCEMENT,
                AISector.JUSTICE,
                AISector.CRITICAL_INFRASTRUCTURE
            ]
            if self.sector in high_risk_sectors and not self.eu_database_registration_id:
                raise ValueError(
                    f"Sistemas de alto risco no setor {self.sector.value} "
                    f"devem ter eu_database_registration_id (Art. 71)"
                )

        return self
