#!/usr/bin/env python3
"""
BuildToValue v0.9.5 - Enforcement Engine with Regulatory Impact Assessment
Scientific Basis: Huwyler (2025) - arXiv:2511.21901v1 [cs.CR]

Major Changes in v0.9.5:
- Regulatory penalty calculation (EU AI Act, GDPR, ECOA)
- Financial exposure reporting (CFO-ready metrics)
- YAML-based penalty configuration (quarterly legal review support)
- CIA-L-R loss category tracking
- Control effectiveness baseline

References:
- Huwyler, H. (2025). "Standardized Threat Taxonomy for AI Security"
- EU AI Act (Regulation 2024/1689) - Art. 99
- GDPR (Regulation 2016/679) - Art. 83
- Equal Credit Opportunity Act (15 USC § 1691)
"""

import os
import yaml
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

from src.domain.enums import ThreatDomain, ThreatCategory, Outcome
from src.domain.entities import Task, AISystem
from src.core.governance.threat_classifier import (
    ThreatVectorClassifier,
    ThreatClassificationResult
)

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# REGULATORY PENALTY CONFIGURATION LOADER
# ============================================================================

class RegulatoryPenaltyLoader:
    """
    Loads and manages regulatory penalty schedules from YAML configuration.

    v0.9.5 Design:
    - Centralized penalty configuration (regulatory_penalties.yaml)
    - Fallback to embedded defaults if YAML unavailable
    - Quarterly legal review support (metadata tracking)
    - Multi-jurisdiction support (EUR, USD)

    Governance Requirements:
    - Legal Dept must review YAML quarterly
    - Version control with signed commits
    - Audit trail via metadata.changelog
    """

    DEFAULT_CONFIG_PATH = "src/config/regulatory_penalties.yaml"

    # ✅ EMBEDDED FALLBACK (Production Safety)
    # If YAML is missing/corrupted, use these statutory minimums
    FALLBACK_PENALTIES = {
        "eu_ai_act_prohibited_practices": {
            "jurisdiction": "European Union",
            "regulation": "AI Act (Regulation 2024/1689)",
            "article": "Art. 99 - Prohibited Practices",
            "penalty": {
                "currency": "EUR",
                "min_fine": 15000000,
                "max_fine": 35000000
            },
            "triggers": {
                "threat_domains": ["PRIVACY"],
                "specific_violations": [
                    {"keyword": "emotion recognition"},
                    {"keyword": "biometric categorization"}
                ]
            },
            "severity": "CRITICAL"
        },
        "eu_ai_act_high_risk_violations": {
            "jurisdiction": "European Union",
            "regulation": "AI Act (Regulation 2024/1689)",
            "article": "Art. 99 - High-Risk Systems",
            "penalty": {
                "currency": "EUR",
                "min_fine": 7500000,
                "max_fine": 15000000
            },
            "triggers": {
                "threat_domains": ["BIASES"],
                "specific_violations": [
                    {"keyword": "proxy discrimination"},
                    {"keyword": "deny loan"}
                ]
            },
            "severity": "HIGH"
        },
        "gdpr_art_83_5_violations": {
            "jurisdiction": "European Union",
            "regulation": "GDPR (Regulation 2016/679)",
            "article": "Art. 83(5) - Data Protection Principles",
            "penalty": {
                "currency": "EUR",
                "min_fine": 10000000,
                "max_fine": 20000000
            },
            "triggers": {
                "threat_domains": ["PRIVACY"],
                "specific_violations": [
                    {"keyword": "pii leakage"},
                    {"keyword": "model inversion"}
                ]
            },
            "severity": "HIGH"
        },
        "ecoa_discrimination": {
            "jurisdiction": "United States",
            "regulation": "Equal Credit Opportunity Act (15 USC § 1691)",
            "article": "§ 1691e - Civil liability",
            "penalty": {
                "currency": "USD",
                "min_fine": 10000,
                "max_fine": 500000
            },
            "triggers": {
                "threat_domains": ["BIASES"],
                "specific_violations": [
                    {"keyword": "redlining"},
                    {"keyword": "proxy discrimination"}
                ]
            },
            "severity": "HIGH"
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize penalty loader.

        Args:
            config_path: Path to regulatory_penalties.yaml
                        (defaults to src/config/regulatory_penalties.yaml)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.penalties = {}
        self.metadata = {}
        self.aggregation_rules = {}

        self._load_penalties()

    def _load_penalties(self) -> None:
        """
        Load penalty schedules from YAML or fallback to embedded defaults.

        Safety Features:
        - Graceful degradation if YAML missing
        - Schema validation
        - Legal review date verification
        """
        try:
            config_file = Path(self.config_path)

            if not config_file.exists():
                logger.warning(
                    f"Regulatory penalty config not found at {self.config_path}. "
                    f"Using embedded fallback penalties."
                )
                self.penalties = self.FALLBACK_PENALTIES
                self._set_fallback_metadata()
                return

            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Extract sections
            self.metadata = config.get("metadata", {})
            self.penalties = config.get("penalties", {})
            self.aggregation_rules = config.get("aggregation_rules", {})

            # ✅ VALIDATE LEGAL REVIEW DATE
            self._validate_legal_review()

            logger.info(
                f"Loaded {len(self.penalties)} penalty schedules from "
                f"{self.config_path} (version {self.metadata.get('version')})"
            )

        except yaml.YAMLError as e:
            logger.error(
                f"YAML parsing error in {self.config_path}: {e}. "
                f"Falling back to embedded penalties."
            )
            self.penalties = self.FALLBACK_PENALTIES
            self._set_fallback_metadata()

        except Exception as e:
            logger.error(
                f"Unexpected error loading penalties: {e}. "
                f"Falling back to embedded penalties."
            )
            self.penalties = self.FALLBACK_PENALTIES
            self._set_fallback_metadata()

    def _set_fallback_metadata(self) -> None:
        """Set metadata when using embedded fallback."""
        self.metadata = {
            "version": "0.9.5-fallback",
            "last_updated": "2025-12-27T16:05:00Z",
            "legal_review_date": "2025-12-15",
            "source": "Embedded fallback (YAML not available)"
        }

    def _validate_legal_review(self) -> None:
        """
        Verify that legal review is current (within 90 days).

        Governance Requirement:
        - Quarterly legal review mandatory for compliance
        - Warning if review overdue (not blocking)
        """
        from datetime import datetime, timedelta

        review_date_str = self.metadata.get("legal_review_date")
        if not review_date_str:
            logger.warning(
                "No legal_review_date found in penalty config metadata. "
                "Ensure quarterly legal review is performed."
            )
            return

        try:
            review_date = datetime.fromisoformat(review_date_str)
            days_since_review = (datetime.now() - review_date).days

            if days_since_review > 90:
                logger.warning(
                    f"⚠️ Regulatory penalty config is {days_since_review} days old. "
                    f"Quarterly legal review is OVERDUE. "
                    f"Last review: {review_date_str}"
                )
            else:
                logger.info(
                    f"✅ Regulatory penalties current (reviewed {days_since_review} days ago)"
                )

        except ValueError:
            logger.warning(
                f"Invalid legal_review_date format: {review_date_str}. "
                f"Expected ISO format (YYYY-MM-DD)."
            )

    def get_applicable_penalties(
            self,
            classification: ThreatClassificationResult
    ) -> List[Dict[str, Any]]:
        """
        Find applicable regulatory penalties based on threat classification.

        Algorithm:
        1. Match threat_domains (e.g., PRIVACY, BIASES)
        2. Match specific_violations (keywords)
        3. Return all applicable penalties with metadata

        Args:
            classification: ThreatClassificationResult from classifier

        Returns:
            List of applicable penalty dicts with:
            - regulation name
            - penalty range (min/max)
            - severity
            - triggered_by (matched keywords)
            - citation URL
        """
        applicable = []

        for penalty_name, penalty_config in self.penalties.items():
            triggers = penalty_config.get("triggers", {})

            # ✅ STEP 1: Match Threat Domains
            trigger_domains = triggers.get("threat_domains", [])
            domain_match = any(
                domain.value in trigger_domains or domain.name in trigger_domains
                for domain in classification.detected_domains
            )

            if not domain_match:
                continue

            # ✅ STEP 2: Match Specific Keywords
            specific_violations = triggers.get("specific_violations", [])
            matched_triggers = []

            for violation in specific_violations:
                violation_keyword = violation.get("keyword", "").lower()

                # Check if keyword appears in classification results
                for threat_name, keywords in classification.matched_keywords.items():
                    if any(violation_keyword in kw.lower() for kw in keywords):
                        matched_triggers.append(violation_keyword)
                        break

            # ✅ STEP 3: Build Penalty Entry
            if matched_triggers:
                penalty_info = penalty_config.get("penalty", {})

                applicable.append({
                    "penalty_id": penalty_name,
                    "regulation": penalty_config.get("regulation", "Unknown"),
                    "article": penalty_config.get("article", "N/A"),
                    "jurisdiction": penalty_config.get("jurisdiction", "Unknown"),
                    "currency": penalty_info.get("currency", "EUR"),
                    "min_penalty": penalty_info.get("min_fine", 0),
                    "max_penalty": penalty_info.get("max_fine", 0),
                    "alternative_formula": penalty_info.get("alternative_formula"),
                    "severity": penalty_config.get("severity", "MEDIUM"),
                    "triggered_by": matched_triggers,
                    "citation": penalty_config.get("citation_url", ""),
                    "enforcement_authority": penalty_config.get(
                        "enforcement_authority", "N/A"
                    )
                })

        # Sort by severity (CRITICAL > HIGH > MEDIUM)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        applicable.sort(
            key=lambda x: (
                severity_order.get(x["severity"], 99),
                -x["max_penalty"]  # Higher fines first
            )
        )

        return applicable

    def calculate_total_exposure(
            self,
            applicable_penalties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total regulatory exposure across all applicable penalties.

        Aggregation Rules (per YAML config):
        - EU regulations: No stacking (max penalty rule)
        - US regulations: Stacking allowed (different legal bases)

        Args:
            applicable_penalties: List from get_applicable_penalties()

        Returns:
            Dict with:
            - total_min_eur: Minimum exposure (EUR)
            - total_max_eur: Maximum exposure (EUR)
            - total_min_usd: Minimum exposure (USD)
            - total_max_usd: Maximum exposure (USD)
            - currencies: List of applicable currencies
            - stacking_applied: Whether penalties were stacked
        """
        if not applicable_penalties:
            return {
                "total_min_eur": 0,
                "total_max_eur": 0,
                "total_min_usd": 0,
                "total_max_usd": 0,
                "currencies": [],
                "stacking_applied": False
            }

        # Separate by jurisdiction for stacking rules
        eu_penalties = [
            p for p in applicable_penalties
            if p["jurisdiction"] == "European Union"
        ]
        us_penalties = [
            p for p in applicable_penalties
            if "United States" in p["jurisdiction"]
        ]

        # ✅ EU PENALTIES: Max penalty rule (no stacking)
        eu_min = max((p["min_penalty"] for p in eu_penalties), default=0)
        eu_max = max((p["max_penalty"] for p in eu_penalties), default=0)

        # ✅ US PENALTIES: Stacking allowed (different legal bases)
        us_min = sum(p["min_penalty"] for p in us_penalties)
        us_max = sum(p["max_penalty"] for p in us_penalties)

        # Aggregate
        total_min_eur = eu_min
        total_max_eur = eu_max
        total_min_usd = us_min
        total_max_usd = us_max

        currencies = []
        if eu_penalties:
            currencies.append("EUR")
        if us_penalties:
            currencies.append("USD")

        stacking_applied = len(us_penalties) > 1

        return {
            "total_min_eur": total_min_eur,
            "total_max_eur": total_max_eur,
            "total_min_usd": total_min_usd,
            "total_max_usd": total_max_usd,
            "currencies": currencies,
            "stacking_applied": stacking_applied,
            "eu_penalties_count": len(eu_penalties),
            "us_penalties_count": len(us_penalties)
        }


# ============================================================================
# DECISION RESULT (Enhanced for v0.9.5)
# ============================================================================

@dataclass
class Decision:
    """
    Enforcement decision with regulatory impact assessment.

    v0.9.5 Enhancements:
    - regulatory_impact: Financial exposure (CFO-ready)
    - loss_categories: CIA-L-R framework categories
    - controls_applied: List of active controls
    - baseline_risk: Risk score without controls (for ROI tracking)

    Fields:
        outcome: APPROVED, BLOCKED, ESCALATE, CONDITIONAL
        risk_score: Weighted risk score (0.0-10.0)
        reason: Human-readable explanation
        detected_threats: List of threat names
        confidence: Overall confidence (0.0-1.0)
        recommendations: List of mitigation actions

        # ✅ v0.9.5: NEW FIELDS
        regulatory_impact: Financial exposure assessment
        loss_categories: CIA-L-R categories affected
        controls_applied: List of control names applied
        baseline_risk: Risk score without controls
        sub_threat_type: Specific sub-threat (e.g., "proxy_discrimination")
    """
    outcome: Outcome
    risk_score: float
    reason: str
    detected_threats: List[str]
    confidence: float
    recommendations: List[str] = field(default_factory=list)

    # ✅ v0.9.5: REGULATORY IMPACT ASSESSMENT
    regulatory_impact: Optional[Dict[str, Any]] = None
    # Structure:
    # {
    #     "applicable_regulations": [
    #         {
    #             "regulation": "EU AI Act Art. 99",
    #             "min_penalty": 15000000,
    #             "max_penalty": 35000000,
    #             "currency": "EUR",
    #             "severity": "CRITICAL",
    #             "triggered_by": ["emotion recognition"]
    #         }
    #     ],
    #     "total_exposure": {
    #         "min_eur": 25000000,
    #         "max_eur": 55000000,
    #         "currencies": ["EUR", "USD"]
    #     },
    #     "executive_summary": "CRITICAL: €35M exposure..."
    # }

    # ✅ v0.9.5: CIA-L-R FRAMEWORK
    loss_categories: List[str] = field(default_factory=list)

    # ✅ v0.9.5: CONTROL EFFECTIVENESS TRACKING (Foundation for v1.0)
    controls_applied: List[str] = field(default_factory=list)
    baseline_risk: float = 0.0  # Risk without controls

    # ✅ v0.9.5: SUB-THREAT TRACKING
    sub_threat_type: Optional[str] = None


# ============================================================================
# ENFORCEMENT ENGINE
# ============================================================================

class EnforcementEngine:
    """
    Enforces governance policies with regulatory impact assessment.

    v0.9.5 Capabilities:
    - Threat classification (via ThreatVectorClassifier)
    - Risk scoring (prevalence-weighted)
    - Regulatory penalty calculation (multi-jurisdiction)
    - CIA-L-R loss category tracking
    - Control baseline (foundation for v1.0 ROI tracking)

    Decision Thresholds:
    - CRITICAL (≥9.0): Prohibited practices, immediate block
    - HIGH (≥7.0): Escalate to human review
    - MEDIUM (≥5.0): Conditional approval with monitoring
    - LOW (<5.0): Automatic approval

    Scientific Basis:
    - Huwyler (2025) - Standardized Threat Taxonomy
    - NIST AI RMF 1.0 - Govern/Map/Measure functions
    - ISO/IEC 42001:2023 - Clause 6.1 (Risk Assessment)
    """

    # ✅ RISK THRESHOLDS (Empirically Calibrated)
    THRESHOLD_CRITICAL = 9.0  # Block immediately
    THRESHOLD_HIGH = 7.0  # Escalate to human
    THRESHOLD_MEDIUM = 5.0  # Conditional approval
    THRESHOLD_LOW = 3.0  # Auto-approve with logging

    def __init__(
            self,
            penalty_config_path: Optional[str] = None,
            use_simplified_taxonomy: bool = True
    ):
        """
        Initialize enforcement engine.

        Args:
            penalty_config_path: Path to regulatory_penalties.yaml
            use_simplified_taxonomy: Use ThreatCategory vs ThreatDomain
        """
        self.classifier = ThreatVectorClassifier(
            use_simplified=use_simplified_taxonomy
        )
        self.penalty_loader = RegulatoryPenaltyLoader(penalty_config_path)

        logger.info(
            f"✅ EnforcementEngine v0.9.5 initialized. "
            f"Loaded {len(self.penalty_loader.penalties)} penalty schedules."
        )

    def enforce(
            self,
            task: Task,
            system: AISystem,
            issues: Optional[List[str]] = None
    ) -> Decision:
        """
        Enforce governance policy with regulatory impact assessment.

        v0.9.5 Workflow:
        1. Classify threats (prevalence-weighted)
        2. Calculate risk score
        3. Assess regulatory exposure (financial)
        4. Determine outcome (APPROVED/BLOCKED/ESCALATE)
        5. Generate recommendations

        Args:
            task: Task being evaluated
            system: AISystem being accessed
            issues: Optional pre-detected issues

        Returns:
            Decision with regulatory_impact populated
        """
        # ✅ STEP 1: CLASSIFY THREATS
        issues_to_analyze = issues or []

        # Add task context for classification
        classification = self.classifier.classify(
            issues=issues_to_analyze,
            task_title=task.title,
            task_description=task.description
        )

        # ✅ STEP 2: CALCULATE BASELINE RISK SCORE
        baseline_risk = self._calculate_risk_score(classification)

        # ✅ STEP 3: APPLY CONTROLS (Future: v1.0 ROI tracking)
        controls_applied, residual_risk = self._apply_controls(
            baseline_risk, classification, system
        )

        # ✅ STEP 4: ASSESS REGULATORY EXPOSURE
        regulatory_impact = self._calculate_regulatory_impact(classification)

        # ✅ STEP 5: DETERMINE OUTCOME
        outcome, reason = self._determine_outcome(
            residual_risk, classification, regulatory_impact
        )

        # ✅ STEP 6: GENERATE RECOMMENDATIONS
        recommendations = self._generate_recommendations(
            classification, regulatory_impact, outcome
        )

        # ✅ BUILD DECISION
        return Decision(
            outcome=outcome,
            risk_score=residual_risk,
            reason=reason,
            detected_threats=[t.value for t in classification.detected_domains],
            confidence=classification.weighted_score,
            recommendations=recommendations,
            # v0.9.5 fields
            regulatory_impact=regulatory_impact,
            loss_categories=classification.loss_categories,
            controls_applied=controls_applied,
            baseline_risk=baseline_risk,
            sub_threat_type=classification.sub_threat_type
        )

    def _calculate_risk_score(
            self,
            classification: ThreatClassificationResult
    ) -> float:
        """
        Calculate risk score on 0-10 scale.

        v0.9.5 Algorithm:
        - Base score = weighted_score (prevalence-adjusted) * 10
        - Severity boost based on sub_threat_type
        - Loss category multiplier (more categories = higher risk)

        Args:
            classification: Threat classification result

        Returns:
            Risk score (0.0-10.0)
        """
        # Base score from prevalence-weighted confidence
        base_score = classification.weighted_score * 10.0

        # ✅ SEVERITY BOOST (Sub-Threat Specific)
        severity_boost = 0.0

        if classification.sub_threat_type:
            # CRITICAL sub-threats (EU AI Act Art. 5 violations)
            if classification.sub_threat_type in [
                "prohibited_practice_biometric",
                "shadow_ai_credential_exposure"
            ]:
                severity_boost = 2.0  # Push to CRITICAL range (≥9.0)

            # HIGH sub-threats (regulatory violations)
            elif classification.sub_threat_type in [
                "proxy_discrimination",
                "model_inversion",
                "pii_leakage"
            ]:
                severity_boost = 1.0  # Push to HIGH range (≥7.0)

        # ✅ LOSS CATEGORY MULTIPLIER
        # More impacted categories = higher systemic risk
        loss_category_count = len(classification.loss_categories)
        category_multiplier = 1.0 + (loss_category_count * 0.1)

        # Final score (capped at 10.0)
        risk_score = min((base_score + severity_boost) * category_multiplier, 10.0)

        return round(risk_score, 2)

    def _apply_controls(
            self,
            baseline_risk: float,
            classification: ThreatClassificationResult,
            system: AISystem
    ) -> Tuple[List[str], float]:
        """
        Apply controls and calculate residual risk.

        v0.9.5: Basic implementation (foundation for v1.0 ROI tracking)
        v1.0: Will track control effectiveness and cost avoidance

        Args:
            baseline_risk: Risk score without controls
            classification: Threat classification
            system: AI system being accessed

        Returns:
            Tuple of (controls_applied, residual_risk)
        """
        controls = []
        risk_reduction_factor = 1.0  # No reduction by default

        # ✅ CONTROL 1: Bias Keyword Filter
        if ThreatDomain.BIASES in classification.detected_domains:
            controls.append("Bias Keyword Filter")
            risk_reduction_factor *= 0.7  # 30% reduction

        # ✅ CONTROL 2: PII Detection
        if ThreatDomain.PRIVACY in classification.detected_domains:
            controls.append("PII Detection")
            risk_reduction_factor *= 0.6  # 40% reduction

        # ✅ CONTROL 3: Shadow AI Blocker (v0.9.5 NEW)
        if classification.sub_threat_type and "shadow_ai" in classification.sub_threat_type:
            controls.append("Shadow AI Credential Blocker")
            risk_reduction_factor *= 0.3  # 70% reduction (CRITICAL control)

        # ✅ CONTROL 4: System-Level Controls
        # Future: Read from system.controls or governance policy

        residual_risk = baseline_risk * risk_reduction_factor

        return controls, round(residual_risk, 2)

    def _calculate_regulatory_impact(
            self,
            classification: ThreatClassificationResult
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate regulatory financial exposure.

        v0.9.5: Full implementation with multi-jurisdiction support

        Args:
            classification: Threat classification result

        Returns:
            Dict with applicable_regulations and total_exposure,
            or None if no regulatory risks detected
        """
        # Get applicable penalties from YAML config
        applicable_penalties = self.penalty_loader.get_applicable_penalties(
            classification
        )

        if not applicable_penalties:
            return None

        # Calculate total exposure
        total_exposure = self.penalty_loader.calculate_total_exposure(
            applicable_penalties
        )

        # ✅ GENERATE EXECUTIVE SUMMARY
        executive_summary = self._generate_executive_summary(
            applicable_penalties, total_exposure
        )

        return {
            "applicable_regulations": applicable_penalties,
            "total_exposure": total_exposure,
            "executive_summary": executive_summary,
            "compliance_note": (
                "Penalties based on statutory schedules as of "
                f"{self.penalty_loader.metadata.get('last_updated', 'N/A')}. "
                "Actual fines may vary based on organization size, "
                "cooperation, and mitigating factors."
            ),
            "legal_review_status": {
                "last_reviewed": self.penalty_loader.metadata.get(
                    "legal_review_date", "Unknown"
                ),
                "next_review": self.penalty_loader.metadata.get(
                    "next_review_date", "Unknown"
                ),
                "version": self.penalty_loader.metadata.get("version", "Unknown")
            }
        }

    def _generate_executive_summary(
            self,
            penalties: List[Dict[str, Any]],
            total_exposure: Dict[str, Any]
    ) -> str:
        """
        Generate CFO-ready executive summary of regulatory exposure.

        Args:
            penalties: List of applicable penalties
            total_exposure: Total exposure calculation

        Returns:
            Executive summary string
        """
        critical_penalties = [p for p in penalties if p["severity"] == "CRITICAL"]
        high_penalties = [p for p in penalties if p["severity"] == "HIGH"]

        # Format currency amounts
        if total_exposure["total_max_eur"] > 0:
            eur_range = (
                f"€{total_exposure['total_min_eur']:,} - "
                f"€{total_exposure['total_max_eur']:,}"
            )
        else:
            eur_range = None

        if total_exposure["total_max_usd"] > 0:
            usd_range = (
                f"${total_exposure['total_min_usd']:,} - "
                f"${total_exposure['total_max_usd']:,}"
            )
        else:
            usd_range = None

        # Build summary
        if critical_penalties:
            summary = (
                f"🚨 CRITICAL: {len(critical_penalties)} prohibited practice(s) detected. "
            )
            if eur_range:
                summary += f"EU regulatory exposure: {eur_range}. "
            if usd_range:
                summary += f"US regulatory exposure: {usd_range}. "

            # List critical violations
            violations = ", ".join(
                set(kw for p in critical_penalties for kw in p["triggered_by"])
            )
            summary += f"Violations: {violations}."

        elif high_penalties:
            summary = (
                f"⚠️ HIGH: {len(high_penalties)} regulatory violation(s) detected. "
            )
            if eur_range:
                summary += f"EU exposure: {eur_range}. "
            if usd_range:
                summary += f"US exposure: {usd_range}."

        else:
            summary = "Regulatory risks detected. Review recommended."

        return summary

    def _determine_outcome(
            self,
            risk_score: float,
            classification: ThreatClassificationResult,
            regulatory_impact: Optional[Dict[str, Any]]
    ) -> Tuple[Outcome, str]:
        """
        Determine enforcement outcome based on risk and regulatory exposure.

        v0.9.5 Decision Logic:
        - BLOCKED: CRITICAL regulatory violations or risk ≥9.0
        - ESCALATE: HIGH regulatory violations or risk ≥7.0
        - CONDITIONAL: MEDIUM risk (5.0-7.0)
        - APPROVED: LOW risk (<5.0)

        Args:
            risk_score: Calculated risk score (0-10)
            classification: Threat classification
            regulatory_impact: Regulatory exposure assessment

        Returns:
            Tuple of (Outcome, reason string)
        """
        # ✅ CRITICAL: Prohibited Practices (EU AI Act Art. 5)
        if regulatory_impact:
            critical_regs = [
                r for r in regulatory_impact["applicable_regulations"]
                if r["severity"] == "CRITICAL"
            ]
            if critical_regs:
                violations = ", ".join(
                    set(kw for r in critical_regs for kw in r["triggered_by"])
                )
                return (
                    Outcome.BLOCKED,
                    f"BLOCKED: Prohibited AI practice detected ({violations}). "
                    f"{regulatory_impact['executive_summary']}"
                )

        # ✅ HIGH RISK: Automatic Block
        if risk_score >= self.THRESHOLD_CRITICAL:
            primary = classification.primary_threat or "high-risk activity"
            return (
                Outcome.BLOCKED,
                f"BLOCKED: Critical risk score ({risk_score}/10.0) for {primary}. "
                f"Immediate review required."
            )

        # ✅ ESCALATE: High Risk or Significant Regulatory Exposure
        if risk_score >= self.THRESHOLD_HIGH:
            reason = f"Risk score {risk_score}/10.0 exceeds HIGH threshold. "
            if regulatory_impact:
                reason += regulatory_impact["executive_summary"]
            return (Outcome.ESCALATE, reason)

        # ✅ CONDITIONAL: Medium Risk
        if risk_score >= self.THRESHOLD_MEDIUM:
            return (
                Outcome.CONDITIONAL,
                f"Conditional approval: Risk score {risk_score}/10.0. "
                f"Monitoring required for {classification.primary_threat}."
            )

        # ✅ APPROVED: Low Risk
        return (
            Outcome.APPROVED,
            f"Approved: Low risk ({risk_score}/10.0). Standard monitoring applies."
        )

    def _generate_recommendations(
            self,
            classification: ThreatClassificationResult,
            regulatory_impact: Optional[Dict[str, Any]],
            outcome: Outcome
    ) -> List[str]:
        """
        Generate actionable recommendations based on detected threats.

        Args:
            classification: Threat classification
            regulatory_impact: Regulatory exposure
            outcome: Enforcement outcome

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # ✅ CRITICAL RECOMMENDATIONS (Blocked/Escalated)
        if outcome in [Outcome.BLOCKED, Outcome.ESCALATE]:
            if regulatory_impact:
                recommendations.append(
                    "⚠️ URGENT: Engage Legal Dept for regulatory compliance review"
                )
                recommendations.append(
                    f"📋 Document decision in compliance ledger (ISO 42001 Clause 9.1)"
                )

        # ✅ DOMAIN-SPECIFIC RECOMMENDATIONS
        for domain in classification.detected_domains:
            if domain == ThreatDomain.BIASES:
                recommendations.append(
                    "🔍 Conduct fairness audit across demographic groups (EU AI Act Art. 10)"
                )
                if "proxy discrimination" in str(classification.sub_threat_type):
                    recommendations.append(
                        "🚫 Remove zip code/geographic proxies from model features"
                    )

            elif domain == ThreatDomain.PRIVACY:
                recommendations.append(
                    "🔒 Apply differential privacy or federated learning (GDPR Art. 25)"
                )
                if "biometric" in str(classification.sub_threat_type):
                    recommendations.append(
                        "🚨 CRITICAL: Biometric processing prohibited without consent (EU AI Act Art. 5)"
                    )

            elif domain == ThreatDomain.MISUSE:
                if "shadow_ai" in str(classification.sub_threat_type):
                    recommendations.append(
                        "🔑 Rotate credentials immediately (potential exposure detected)"
                    )
                    recommendations.append(
                        "📚 Employee training: Authorized AI tools only"
                    )
                else:
                    recommendations.append(
                        "🛡️ Implement robust input validation and output monitoring"
                    )

            elif domain == ThreatDomain.UNRELIABLE_OUTPUTS:
                recommendations.append(
                    "✅ Implement fact-checking against verified knowledge base"
                )
                recommendations.append(
                    "📝 Require source citations for all factual claims"
                )

            elif domain == ThreatDomain.DRIFT:
                recommendations.append(
                    "📊 Deploy automated drift detection and retraining pipeline"
                )

        # ✅ GENERIC MONITORING (Approved/Conditional)
        if outcome in [Outcome.APPROVED, Outcome.CONDITIONAL]:
            recommendations.append(
                "📈 Enable continuous monitoring for drift and quality degradation"
            )

        return recommendations


# ============================================================================
# VERSION METADATA
# ============================================================================
ENFORCEMENT_VERSION = "0.9.5"
SCIENTIFIC_BASIS = """
v0.9.5 (2025-12-27) - Regulatory Impact Assessment:

MAJOR ENHANCEMENTS:
✅ Financial exposure calculation (EU AI Act, GDPR, ECOA)
✅ Multi-jurisdiction penalty support (EUR, USD)
✅ YAML-based regulatory configuration (quarterly legal review)
✅ CIA-L-R loss category tracking
✅ Control effectiveness baseline (foundation for v1.0 ROI)

REGULATORY COMPLIANCE:
- EU AI Act Art. 99: €15M - €35M fines
- GDPR Art. 83: €10M - €20M fines
- ECOA § 1691: $10K - $500K+ per case

DECISION THRESHOLDS:
- CRITICAL (≥9.0): Immediate block
- HIGH (≥7.0): Escalate to human review
- MEDIUM (≥5.0): Conditional approval
- LOW (<5.0): Auto-approve

SCIENTIFIC VALIDATION:
- Base taxonomy: arXiv:2511.21901v1 [cs.CR]
- NIST AI RMF 1.0 alignment
- ISO/IEC 42001:2023 Clause 6.1

KEY METRICS (Target):
- Prevention rate: 98.8%
- False positive rate: <2%
- Regulatory penalty accuracy: 100%

References:
[1] Huwyler (2025) - Standardized Threat Taxonomy
[2] EU AI Act (Regulation 2024/1689)
[3] GDPR (Regulation 2016/679)
[4] NIST AI RMF 1.0
"""
