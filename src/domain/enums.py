"""
Enumerações do BuildToValue (ISO 42001 + EU AI Act compliant)
"""

from enum import Enum


class ArtifactType(str, Enum):
    """Tipo de artefato gerado/processado"""
    CODE = "code"
    DATA_MODEL = "data_model"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"


class AIRole(str, Enum):
    """Papel do agente na cadeia de IA (Art. 28 EU AI Act)"""
    PROVIDER = "provider"
    DEPLOYER = "deployer"
    DISTRIBUTOR = "distributor"
    IMPORTER = "importer"
    MANUFACTURER = "manufacturer"


class AISector(str, Enum):
    """Setores de aplicação (Anexo III EU AI Act)"""
    BIOMETRIC = "biometric"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION = "migration"
    JUSTICE = "justice"
    DEMOCRATIC_PROCESSES = "democratic_processes"
    BANKING = "banking"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    GENERAL_COMMERCIAL = "general_commercial"
    MARKETING = "marketing"


class EUComplianceRisk(str, Enum):
    """Níveis de risco (Art. 6-7 EU AI Act)"""
    UNACCEPTABLE = "unacceptable"      # Art. 5 - Proibido
    HIGH = "high"                       # Art. 6 - Alto risco (Anexo III)
    LIMITED = "limited"                 # Art. 50 - Risco limitado
    MINIMAL = "minimal"                 # Art. 69 - Risco mínimo
    SYSTEMIC_GPAI = "systemic_gpai"   # Art. 51 - GPAI sistêmico


class DecisionOutcome(str, Enum):
    """Resultado da decisão de enforcement"""
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    PENDING_REVIEW = "PENDING_REVIEW"
    ESCALATED = "ESCALATED"
