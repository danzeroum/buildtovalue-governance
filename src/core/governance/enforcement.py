#!/usr/bin/env python3

"""
BuildToValue v0.9.1 - Enforcement Engine (CORRIGIDO)
ARQUIVO: src/core/governance/enforcement.py
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from src.domain.entities import AISystem, Task, Decision
from src.domain.enums import OperationalStatus, AIPhase

try:
    from .threat_classifier import ThreatVectorClassifier, ThreatClassificationResult
except ImportError:
    from src.core.governance.threat_classifier import (
        ThreatVectorClassifier,
        ThreatClassificationResult
    )

logger = logging.getLogger(__name__)


class RuntimeEnforcementEngine:
    """
    Core enforcement engine with multi-agent assessment.
    v0.9.1 Fixes:
    - ✅ Corrected ethical agent to check title + description
    - ✅ Integrated threat score into final risk calculation
    - ✅ Increased penalty weights for detected threats
    """

    def __init__(self):
        self.threat_classifier = ThreatVectorClassifier(use_simplified=True)
        self.logger = logging.getLogger(__name__)

    def enforce(
            self,
            task: Task,
            system: AISystem,
            policies: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """
        Evaluate task against system policies with enhanced threat analysis.
        """

        # ====================================================================
        # STEP 1: KILL SWITCH (CRITICAL - Check first)
        # ====================================================================
        if system.operational_status == OperationalStatus.EMERGENCY_STOP:
            self.logger.critical(
                f"EMERGENCY_STOP activated for system {system.id}. "
                f"All operations blocked."
            )

            return Decision(
                outcome="BLOCKED",
                reason="KILL_SWITCH_ACTIVE - System under emergency stop",
                risk_score=10.0,
                issues=["Emergency stop activated"],
                recommended_action="Contact system administrator for reactivation",
                threat_classification={
                    "status": "EMERGENCY",
                    "reason": "Manual kill switch activated"
                },
                system_context={
                    "operational_status": system.operational_status.value,
                    "phase": system.lifecycle_phase.value,
                    "system_id": system.id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        # ====================================================================
        # STEP 2: SUSPENDED STATUS CHECK
        # ====================================================================
        if system.operational_status == OperationalStatus.SUSPENDED:
            self.logger.warning(f"System {system.id} is SUSPENDED. Blocking task.")
            return Decision(
                outcome="BLOCKED",
                reason="SYSTEM_SUSPENDED - Awaiting human review",
                risk_score=8.0,
                issues=["System suspended pending review"],
                recommended_action="Wait for system reactivation or contact administrator"
            )

        # ====================================================================
        # STEP 3: LIFECYCLE PHASE VALIDATION
        # ====================================================================
        if system.lifecycle_phase in [AIPhase.DESIGN, AIPhase.DATA_PREP, AIPhase.TRAINING]:
            self.logger.warning(
                f"System {system.id} in pre-deployment phase: {system.lifecycle_phase.value}"
            )

        # ====================================================================
        # STEP 4: MULTI-AGENT RISK ASSESSMENT
        # ====================================================================
        issues = []
        risk_scores = {}

        # Technical Agent
        technical_risk = self._assess_technical_risk(task, system)
        risk_scores["technical"] = technical_risk["score"]
        issues.extend(technical_risk["issues"])

        # Regulatory Agent
        regulatory_risk = self._assess_regulatory_risk(task, system)
        risk_scores["regulatory"] = regulatory_risk["score"]
        issues.extend(regulatory_risk["issues"])

        # Ethical Agent (CORRIGIDO)
        ethical_risk = self._assess_ethical_risk(task, system)
        risk_scores["ethical"] = ethical_risk["score"]
        issues.extend(ethical_risk["issues"])

        # ====================================================================
        # STEP 5: THREAT CLASSIFICATION (Huwyler Taxonomy)
        # ====================================================================
        threat_result: ThreatClassificationResult = self.threat_classifier.classify(
            issues=issues,
            task_title=task.title,
            task_description=task.description
        )

        # ✅ CORREÇÃO 1: Adicionar ameaça detectada aos issues
        if threat_result.primary_threat != "other":
            issues.append(f"Threat detected: {threat_result.primary_threat}")

        # ====================================================================
        # STEP 6: AGGREGATE RISK SCORE (CORRIGIDO)
        # ====================================================================

        # ✅ CORREÇÃO 2: Calcular penalidade por ameaça
        threat_score_penalty = 0.0
        if threat_result.primary_threat != "other":
            # Pega a confiança (0.0 a 1.0) e multiplica por 10 para score de risco
            confidence = threat_result.confidence_scores.get(
                threat_result.primary_threat, 0.0
            )
            threat_score_penalty = confidence * 10.0

        # Weighted average dos agentes
        base_score = (
                risk_scores["technical"] * 0.20 +
                risk_scores["regulatory"] * 0.30 +
                risk_scores["ethical"] * 0.20
        )

        # ✅ CORREÇÃO 3: Incluir threat score no cálculo (peso 30%)
        final_score = base_score + (threat_score_penalty * 0.30)

        # Cap em 10.0
        final_score = min(final_score, 10.0)

        # Lifecycle phase adjustment
        if system.lifecycle_phase == AIPhase.MONITORING:
            final_score *= 0.9  # 10% reduction for mature systems

        # ====================================================================
        # STEP 7: DECISION LOGIC
        # ====================================================================
        if final_score >= 7.0:
            outcome = "BLOCKED"
            recommended_action = "Task violates governance policies. Review and modify."
        elif final_score >= 4.0:
            outcome = "ESCALATE"
            recommended_action = "Human review required before proceeding."
        else:
            outcome = "ALLOWED"
            recommended_action = None

        # ====================================================================
        # STEP 8: ENRICHED RESULT
        # ====================================================================
        decision = Decision(
            outcome=outcome,
            reason=self._generate_reason(risk_scores, issues),
            risk_score=final_score,
            issues=issues,
            recommended_action=recommended_action,
            threat_classification={
                "detected_vectors": [t.value for t in threat_result.detected_categories],
                "primary_threat": threat_result.primary_threat,
                "confidence_scores": threat_result.confidence_scores,
                "matched_keywords": threat_result.matched_keywords,
                "taxonomy_version": "Huwyler 2025 (arXiv:2511.21901v1)"
            },
            system_context={
                "system_id": system.id,
                "phase": system.lifecycle_phase.value,
                "status": system.operational_status.value,
                "risk_classification": system.risk_classification.value,
                "sector": system.sector.value,
                "human_ai_config": system.human_ai_configuration.value,
                "schema_version": "0.9.1",
                "compliance": {
                    "nist_alignment": "70%",
                    "aicm_coverage": system.calculate_aicm_coverage(),
                    "supply_chain_risk": system.calculate_supply_chain_risk()
                }
            }
        )

        self.logger.info(
            f"Decision for task {task.id}: {outcome} "
            f"(risk={final_score:.2f}, threat={threat_result.primary_threat})"
        )

        return decision

    def _assess_technical_risk(self, task: Task, system: AISystem) -> Dict:
        """Assess technical risks."""
        issues = []
        score = 0.0

        # Example checks (customize based on system)
        if system.training_compute_flops and system.training_compute_flops > 1e25:
            issues.append("High compute system - increased complexity risk")
            score += 2.0

        # Check external dependencies
        for dep in system.external_dependencies:
            if dep.risk_level == "HIGH":
                issues.append(f"High-risk dependency: {dep.name} ({dep.vendor})")
                score += 1.5

        return {"score": min(score, 10.0), "issues": issues}

    def _assess_regulatory_risk(self, task: Task, system: AISystem) -> Dict:
        """Assess regulatory compliance risks."""
        issues = []
        score = 0.0

        # EU AI Act compliance
        if system.risk_classification.value == "prohibited":
            issues.append("EU AI Act - PROHIBITED practice detected")
            score = 10.0  # Automatic block

        elif system.risk_classification.value == "high":
            # High-risk systems require additional checks
            if not system.requires_human_oversight():
                issues.append("EU AI Act Art. 14 - Human oversight required")
                score += 3.0

        # ✅ CORREÇÃO 4: Verificar prohibited_domains no title também
        for prohibited in system.prohibited_domains:
            if prohibited.lower() in task.title.lower():
                issues.append(f"Task violates prohibited domain: {prohibited}")
                score += 5.0

        return {"score": min(score, 10.0), "issues": issues}

    def _assess_ethical_risk(self, task: Task, system: AISystem) -> Dict:
        """
        Assess ethical risks.
        ✅ CORRIGIDO: Verifica title E description
        """
        issues = []
        score = 0.0

        # ✅ CORREÇÃO 5: Concatenar title + description
        content_to_check = (task.title + " " + task.description).lower()

        # ✅ CORREÇÃO 6: Keywords expandidas + peso aumentado
        bias_keywords = [
            "discriminate", "bias", "unfair", "prejudice",
            "deny loan", "zip code", "redline", "race", "gender"
        ]

        for keyword in bias_keywords:
            if keyword in content_to_check:
                issues.append(f"Potential ethical concern: {keyword}")
                score += 2.5  # ✅ Peso aumentado de 1.0 para 2.5

        # Check target demographic considerations
        if system.target_demographic and "vulnerable" in system.target_demographic.lower():
            issues.append("System targets vulnerable population - heightened scrutiny")
            score += 2.0

        return {"score": min(score, 10.0), "issues": issues}

    def _generate_reason(self, risk_scores: Dict, issues: List[str]) -> str:
        """Generate human-readable decision reason."""
        max_risk_category = max(risk_scores, key=risk_scores.get)
        max_score = risk_scores[max_risk_category]

        reason = f"Primary risk: {max_risk_category} ({max_score:.1f}/10.0)"

        if issues:
            reason += f" | Issues: {len(issues)} detected"

        return reason


# ============================================================================
# VERSION METADATA
# ============================================================================
ENFORCEMENT_VERSION = "0.9.1"
ENHANCEMENTS = """
v0.9.1 (2025-12-27):
- ✅ FIXED: Ethical agent now checks title + description (not just description)
- ✅ FIXED: Threat classification score integrated into final risk (30% weight)
- ✅ FIXED: Increased ethical keyword penalties (1.0 → 2.5)
- ✅ FIXED: Added threat detection to issues list
- ✅ FIXED: Regulatory agent checks prohibited domains in title

v0.9.0 (2025-12-26):
- Added Kill Switch (EMERGENCY_STOP check)
- Integrated Huwyler threat classification
- Enriched audit logs with threat_classification
- Added system_context metadata
"""
