#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - Domain Enums
Unified vocabulary: ISO 42001 + EU AI Act + NIST AI RMF
"""
from enum import Enum

class ArtifactType(str, Enum):
    """Generated/processed artifact type"""
    CODE = "code"
    DATA_MODEL = "data_model"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    DATASET = "dataset"
    MODEL = "model"
    PROMPT = "prompt"

class AIRole(str, Enum):
    """AI agent role in the AI chain (Art. 28 EU AI Act)"""
    PROVIDER = "provider"
    DEPLOYER = "deployer"
    DISTRIBUTOR = "distributor"
    IMPORTER = "importer"
    MANUFACTURER = "manufacturer"
    USER = "user"

class AISector(str, Enum):
    """Application sectors (Annex III EU AI Act)"""
    BANKING = "banking"
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
    """Risk levels (Art. 6-7 EU AI Act)"""
    PROHIBITED = "prohibited"  # Art. 5 (Was UNACCEPTABLE, standardized to PROHIBITED as per v0.9
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    SYSTEMIC_GPAI = "systemic_gpai"

class DecisionOutcome(str, Enum):
    """Enforcement decision outcome"""
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    PENDING_REVIEW = "PENDING_REVIEW"
    ESCALATED = "ESCALATED"

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

class ThreatCategory(Enum):
    """
    Simplified threat categories (7 categories)
    """
    MISUSE = "MISUSE"
    UNRELIABLE = "UNRELIABLE"
    PRIVACY = "PRIVACY"
    FAIRNESS = "FAIRNESS"
    SECURITY = "SECURITY"
    DRIFT = "DRIFT"
    OTHER = "OTHER"

class ThreatDomain(Enum):
    """
    Full threat taxonomy
    """
    MISUSE = "MISUSE"
    POISONING = "POISONING"
    PRIVACY = "PRIVACY"
    ADVERSARIAL = "ADVERSARIAL"
    BIASES = "BIASES"
    UNRELIABLE_OUTPUTS = "UNRELIABLE_OUTPUTS"
    DRIFT = "DRIFT"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    IP_THREAT = "IP_THREAT"

class Outcome(Enum):
    """
    Enforcement decision outcomes
    """
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    ESCALATE = "ESCALATE"
    CONDITIONAL = "CONDITIONAL"