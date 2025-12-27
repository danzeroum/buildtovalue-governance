#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - Domain Enums
Unified vocabulary: ISO 42001 + EU AI Act + NIST AI RMF
"""
from enum import Enum

class ArtifactType(str, Enum):
    """Tipo de artefato gerado/processado"""
    CODE = "code"
    DATA_MODEL = "data_model"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    DATASET = "dataset"
    MODEL = "model"
    PROMPT = "prompt"

class AIRole(str, Enum):
    """Papel do agente na cadeia de IA (Art. 28 EU AI Act)"""
    PROVIDER = "provider"
    DEPLOYER = "deployer"
    DISTRIBUTOR = "distributor"
    IMPORTER = "importer"
    MANUFACTURER = "manufacturer"
    USER = "user"

class AISector(str, Enum):
    """Setores de aplicação (Anexo III EU AI Act)"""
    BANKING = "banking"  # Essencial para Fintech
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    BIOMETRIC = "biometric"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION = "migration"
    JUSTICE = "justice"
    DEMOCRATIC_PROCESSES = "democratic_processes"
    GENERAL_COMMERCIAL = "general_commercial"
    MARKETING = "marketing"
    GENERAL = "general"

class EUComplianceRisk(str, Enum):
    """Níveis de risco (Art. 6-7 EU AI Act)"""
    PROHIBITED = "prohibited" # Art. 5 (Era UNACCEPTABLE, padronizado para PROHIBITED conforme v0.9)
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    SYSTEMIC_GPAI = "systemic_gpai"

class DecisionOutcome(str, Enum):
    """Resultado da decisão de enforcement"""
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    PENDING_REVIEW = "PENDING_REVIEW"
    ESCALATED = "ESCALATED"

# --- NOVOS v0.9.0 (NIST) ---

class AIPhase(str, Enum):
    DESIGN = "design"
    DATA_PREP = "data_preparation"
    TRAINING = "training"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    RETIREMENT = "retirement"

class OperationalStatus(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"
    EMERGENCY_STOP = "emergency_stop"

class HumanAIConfiguration(str, Enum):
    HUMAN_IN_THE_LOOP = "human_in_the_loop"
    HUMAN_OVER_THE_LOOP = "human_over_the_loop"
    FULLY_AUTONOMOUS = "fully_autonomous"

class ThreatCategory(str, Enum):
    MISUSE = "misuse"
    UNRELIABLE = "unreliable_outputs"
    SECURITY = "security"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    DRIFT = "drift"
    OTHER = "other"

class ThreatDomain(str, Enum):
    MISUSE = "misuse"
    POISONING = "poisoning"
    PRIVACY = "privacy"
    ADVERSARIAL = "adversarial"
    BIASES = "biases"
    UNRELIABLE_OUTPUTS = "unreliable_outputs"
    DRIFT = "drift"
    SUPPLY_CHAIN = "supply_chain"
    IP_THREAT = "ip_threat"