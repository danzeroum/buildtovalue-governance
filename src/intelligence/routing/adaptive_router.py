"""
Adaptive Risk Router with 3 Specialized Agents

Implements:
- ISO 42001 6.1.2 (AI Risk Assessment)
- EU AI Act Art. 9 (Risk Management System)
- Multi-dimensional risk scoring (technical, regulatory, ethical)
"""

import logging
from typing import Dict, List

from src.domain.entities import Task, AISystem
from src.domain.enums import EUComplianceRisk, AISector

logger = logging.getLogger("btv.router")


class AdaptiveRiskRouter:
    """
    Adaptive Risk Router with Specialized Agents

    Multi-Agent Architecture:
    1. Technical Agent - Assesses technical complexity (FLOPs, logging)
    2. Regulatory Agent - Verifies compliance (EU AI Act, ISO 42001)
    3. Ethical Agent - Analyzes societal impact (transparency, fairness)

    Risk Score: 0-10 (weighted average)
    """

    def __init__(self):
        """Initialize router with agent weights"""
        self.risk_weights = {
            "technical": 0.3,
            "regulatory": 0.4,  # Higher weight (critical compliance)
            "ethical": 0.3
        }

        # Suspicious keywords for ethical analysis
        self.suspicious_keywords = [
            "discriminar", "manipular", "enganar", "social scoring",
            "subliminar", "vulnerabilidade", "criança", "emoção",
            "manipulação", "exploração", "preconceito", "viés",
            # English
            "discriminate", "manipulate", "deceive", "exploit",
            "bias", "prejudice", "vulnerability", "children"
        ]

    def assess_risk(self, task: Task, system: AISystem) -> Dict:
        """
        Assess aggregated task risk using 3 agents

        Args:
            task: Task being executed
            system: Executing AI system

        Returns:
            Dict with risk_score (0-10) and detected issues

        Compliance:
            ISO 42001 6.1.2 (AI Risk Assessment)
        """
        issues = []
        scores = {}

        # Agent 1: Technical Analysis
        scores["technical"] = self._assess_technical_risk(task, system, issues)

        # Agent 2: Regulatory Analysis (EU AI Act + ISO 42001)
        scores["regulatory"] = self._assess_regulatory_risk(task, system, issues)

        # Agent 3: Ethical Analysis (Art. 69 EU AI Act)
        scores["ethical"] = self._assess_ethical_risk(task, system, issues)

        # Aggregated score (weighted)
        risk_score = sum(
            scores[agent] * self.risk_weights[agent]
            for agent in scores
        )

        # Penalty for history (if flags exist)
        if system.high_risk_flags:
            penalty = min(2.0, len(system.high_risk_flags) * 0.5)
            risk_score += penalty
            issues.append(
                f"⚠️ System has {len(system.high_risk_flags)} high-risk flags"
            )

        logger.info(
            f"Risk assessed: {risk_score:.2f} | "
            f"Technical: {scores['technical']:.2f} | "
            f"Regulatory: {scores['regulatory']:.2f} | "
            f"Ethical: {scores['ethical']:.2f}"
        )

        return {
            "risk_score": min(10.0, risk_score),
            "breakdown": scores,
            "issues": issues
        }

    def _assess_technical_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agent 1: Assess technical risk

        Factors:
        - Training FLOPs (Art. 51 EU AI Act)
        - Logging capabilities (Art. 12 EU AI Act)
        - Task complexity

        Returns:
            Risk score (0-10)
        """
        risk = 2.0  # Base risk

        # Very high FLOPs = higher risk (Systemic GPAI)
        if system.training_compute_flops:
            if system.training_compute_flops > 1e25:
                risk += 3.0
                issues.append(
                    "🔴 Systemic GPAI system (FLOPs > 10^25) - Art. 51 EU AI Act"
                )
            elif system.training_compute_flops > 1e24:
                risk += 2.0
                issues.append(
                    "🟡 High-compute GPAI system (FLOPs > 10^24)"
                )

        # No logging = higher risk (Art. 12 ISO 42001)
        if not system.logging_capabilities:
            risk += 1.5
            issues.append(
                "⚠️ System without logging capability - Art. 12 ISO 42001 violation"
            )

        # Task size (complexity proxy)
        task_length = len(task.title) + len(task.description)
        if task_length > 1000:
            risk += 0.5
            issues.append("📝 Complex task detected (> 1000 chars)")

        return min(10.0, risk)

    def _assess_regulatory_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agent 2: Assess regulatory compliance

        Checks:
        - Application sector (Annex III EU AI Act)
        - Risk classification (Art. 6)
        - Jurisdiction (GDPR Art. 44-50)
        - EU Database registration (Art. 71)

        Returns:
            Risk score (0-10)
        """
        risk = 1.0  # Base risk

        # Sector -> base risk mapping
        high_risk_sectors = [
            AISector.BIOMETRIC,
            AISector.LAW_ENFORCEMENT,
            AISector.JUSTICE,
            AISector.CRITICAL_INFRASTRUCTURE,
            AISector.EMPLOYMENT,
            AISector.EDUCATION
        ]

        if system.sector in high_risk_sectors:
            risk += 4.0
            issues.append(
                f"🔴 HIGH-RISK sector: {system.sector.value} (Annex III EU AI Act)"
            )

        # System risk classification
        if system.risk_classification == EUComplianceRisk.PROHIBITED:
            risk = 10.0
            issues.append(
                "🚨 PROHIBITED PRACTICE detected - Art. 5 EU AI Act - IMMEDIATE BLOCK"
            )
        elif system.risk_classification == EUComplianceRisk.HIGH:
            risk += 3.0
            issues.append(
                "🔴 System classified as HIGH RISK (Art. 6 EU AI Act)"
            )
        elif system.risk_classification == EUComplianceRisk.SYSTEMIC_GPAI:
            risk += 3.5
            issues.append(
                "🔴 GPAI system with systemic risk (Art. 51 EU AI Act)"
            )

        # Non-EU jurisdiction = higher risk (GDPR Art. 44-50)
        if system.jurisdiction != "EU":
            risk += 1.0
            issues.append(
                f"⚠️ System in non-EU jurisdiction: {system.jurisdiction} "
                f"(GDPR Art. 44 - International Transfers)"
            )

        # High risk without EU registration = violation
        if (system.risk_classification == EUComplianceRisk.HIGH and
                not system.eu_database_registration_id):
            risk += 2.0
            issues.append(
                "🔴 High-risk system WITHOUT EU Database registration (Art. 71)"
            )

        return min(10.0, risk)

    def _assess_ethical_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agent 3: Assess ethical and societal risk

        Checks:
        - Suspicious keywords in prompt
        - Transparency (EU registration)
        - Explainability

        Returns:
            Risk score (0-10)
        """
        risk = 1.0  # Base risk

        # Suspicious keywords analysis
        task_lower = (task.title + " " + task.description).lower()
        detected_keywords = []

        for keyword in self.suspicious_keywords:
            if keyword in task_lower:
                detected_keywords.append(keyword)

        if detected_keywords:
            risk += min(3.0, len(detected_keywords) * 1.5)
            issues.append(
                f"⚠️ Suspicious terms detected in prompt: {', '.join(detected_keywords[:3])} "
                f"(Possible Art. 5 EU AI Act violation)"
            )

        # System without EU Database ID = less transparency
        if not system.eu_database_registration_id and system.risk_classification != EUComplianceRisk.MINIMAL:
            risk += 1.0
            issues.append(
                "⚠️ System not registered in EU Database (Art. 71) - "
                "Reduces transparency"
            )

        # Sensitive sectors (children, vulnerable)
        if system.sector in [AISector.EDUCATION, AISector.HEALTHCARE]:
            risk += 0.5
            issues.append(
                f"ℹ️ Sensitive sector: {system.sector.value} - "
                f"Requires special attention to vulnerabilities"
            )

        return min(10.0, risk)
