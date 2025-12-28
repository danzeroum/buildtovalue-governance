#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - Domain Entities
Merged Schema: Clean Core (No Hacks)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from .enums import (
    AIPhase, OperationalStatus, HumanAIConfiguration,
    EUComplianceRisk, AISector, AIRole, ArtifactType
)


# --- Sub-entities (Helpers) ---
@dataclass
class ThirdPartyComponent:
    name: str
    version: str
    vendor: str
    license_type: str
    risk_level: str
    vulnerabilities: List[str] = field(default_factory=list)


@dataclass
class AISystemCostBenefit:
    deployment_cost_usd: float
    maintenance_cost_monthly: float
    expected_benefit_monthly: float
    error_cost_per_incident: float


@dataclass
class ResidualRiskDisclosure:
    risk: str
    likelihood: str
    impact: str
    user_guidance: str
    mitigation_applied: List[str] = field(default_factory=list)


@dataclass
class SocialImpactAssessment:
    affected_population_size: int
    demographic_groups_affected: List[str]
    potential_harms: List[Dict[str, str]]
    potential_benefits: List[Dict[str, str]]
    equity_analysis: Optional[Dict[str, float]] = None


@dataclass
class AISystemTeamComposition:
    system_id: str
    design_team_size: int
    disciplines_represented: List[str]
    stakeholder_groups_consulted: List[str]
    diversity_statement: str
    accessibility_expert_involved: bool


# --- Main Entities ---

@dataclass
class Task:
    id: str = field(default_factory=lambda: "unknown")
    tenant_id: str = field(default_factory=lambda: "unknown")
    system_id: str = field(default_factory=lambda: "unknown")
    title: str = ""
    description: str = ""
    artifact_type: ArtifactType = ArtifactType.CODE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AISystem:
    """
    Unified AI System Entity.

    Contains Legacy (Registry) and New (NIST/Gateway) fields.
    """

    # Identification & Core
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    role: AIRole = AIRole.DEPLOYER
    sector: AISector = AISector.GENERAL
    risk_classification: EUComplianceRisk = EUComplianceRisk.MINIMAL

    # Governance & Configuration
    is_sandbox_mode: bool = False
    logging_capabilities: bool = True
    jurisdiction: str = "EU"
    eu_database_registration_id: Optional[str] = None
    training_compute_flops: Optional[float] = None
    high_risk_flags: List[str] = field(default_factory=list)
    governance_policy: Dict[str, Any] = field(default_factory=dict)

    # NIST / v0.9.0 Lifecycle & Operations
    lifecycle_phase: AIPhase = AIPhase.DEPLOYMENT
    operational_status: OperationalStatus = OperationalStatus.ACTIVE
    human_ai_configuration: HumanAIConfiguration = HumanAIConfiguration.HUMAN_OVER_THE_LOOP
    intended_purpose: Optional[str] = None
    prohibited_domains: List[str] = field(default_factory=list)
    target_demographic: Optional[str] = None
    expected_benefits: Optional[str] = None
    external_dependencies: List[ThirdPartyComponent] = field(default_factory=list)
    estimated_carbon_kg_co2: Optional[float] = None
    energy_consumption_kwh: Optional[float] = None
    aicm_controls_applicable: List[str] = field(default_factory=list)
    aicm_controls_implemented: List[str] = field(default_factory=list)

    # Complex Optional Fields
    cost_benefit_analysis: Optional[AISystemCostBenefit] = None
    residual_risks: List[ResidualRiskDisclosure] = field(default_factory=list)
    social_impact: Optional[SocialImpactAssessment] = None
    team_composition: Optional[AISystemTeamComposition] = None
    policy_card_uri: Optional[str] = None

    # Audit
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

    def requires_human_oversight(self) -> bool:
        return (self.human_ai_configuration != HumanAIConfiguration.FULLY_AUTONOMOUS
                or self.risk_classification == EUComplianceRisk.HIGH)

    def calculate_aicm_coverage(self) -> float:
        if not self.aicm_controls_applicable: return 1.0
        return len(self.aicm_controls_implemented) / len(self.aicm_controls_applicable)

    def calculate_supply_chain_risk(self) -> str:
        if not self.external_dependencies: return "LOW"
        risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        max_risk = max(risk_levels.get(d.risk_level, 0) for d in self.external_dependencies)
        return {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}[max_risk]

    def to_dict(self) -> Dict[str, Any]:
        def serialize(obj):
            if isinstance(obj, Enum): return obj.value
            if isinstance(obj, datetime): return obj.isoformat()
            if isinstance(obj, list): return [serialize(i) for i in obj]
            if hasattr(obj, '__dataclass_fields__'): return {k: serialize(v) for k, v in obj.__dict__.items()}
            return obj

        return {k: serialize(v) for k, v in self.__dict__.items()}


@dataclass
class Decision:
    """Decision entity (Pure Dataclass - No Hacks)"""
    outcome: str
    reason: str
    risk_score: float
    issues: List[str]
    recommended_action: Optional[str] = None
    threat_classification: Optional[Dict[str, Any]] = None
    system_context: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)