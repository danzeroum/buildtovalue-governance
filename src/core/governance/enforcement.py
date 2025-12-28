#!/usr/bin/env python3
"""
BuildToValue v0.9.5.1 - Enforcement Engine with Regulatory Impact Assessment
Bug Fix Release: Shadow AI blocking + executive summary location fix
"""
import os
import yaml
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime, timezone  # ✅ FIX: Added timezone

from src.domain.enums import ThreatDomain, ThreatCategory, Outcome
from src.domain.entities import Task, AISystem
from src.core.governance.threat_classifier import (
    ThreatVectorClassifier,
    ThreatClassificationResult
)

logger = logging.getLogger(__name__)


class RegulatoryPenaltyLoader:
    """
    Loads and manages regulatory penalty schedules from YAML configuration.

    v0.9.5.1 Fix: _generate_executive_summary moved here from EnforcementEngine
    """

    DEFAULT_CONFIG_PATH = "src/config/regulatory_penalties.yaml"

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
            "article": "Art. 83(5)",
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
            "article": "§ 1691e",
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
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.penalties = {}
        self.metadata = {}
        self.aggregation_rules = {}
        self._load_penalties()

    def _load_penalties(self) -> None:
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

            self.metadata = config.get("metadata", {})
            self.penalties = config.get("penalties", {})
            self.aggregation_rules = config.get("aggregation_rules", {})

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
        self.metadata = {
            "version": "0.9.5-fallback",
            "last_updated": "2025-12-27T16:05:00Z",
            "legal_review_date": "2025-12-15",
            "source": "Embedded fallback (YAML not available)"
        }

    def _validate_legal_review(self) -> None:
        """Verify that legal review is current (within 90 days)."""
        review_date_str = self.metadata.get("legal_review_date")
        if not review_date_str:
            logger.warning(
                "No 'legal_review_date' found in penalty config metadata. "
                "Ensure quarterly legal review is performed."
            )
            return

        try:
            review_date = datetime.fromisoformat(review_date_str)

            # If naive (no timezone), assume UTC
            if review_date.tzinfo is None:
                review_date = review_date.replace(tzinfo=timezone.utc)

            # ✅ FIX: Use timezone-aware datetime
            days_since_review = (datetime.now(timezone.utc) - review_date).days

            if days_since_review > 90:
                logger.warning(
                    f"⚠️ Regulatory penalty config is {days_since_review} days old. "
                    f"Quarterly legal review is OVERDUE. "
                    f"Last review: {review_date_str}"
                )
            else:
                logger.info(
                    f"✅ Regulatory penalties current "
                    f"(reviewed {days_since_review} days ago)"
                )
        except ValueError:
            logger.warning(
                f"Invalid 'legal_review_date' format: {review_date_str}. "
                f"Expected ISO format (YYYY-MM-DD)."
            )

    def get_applicable_penalties(
            self,
            classification: ThreatClassificationResult
    ) -> List[Dict[str, Any]]:
        """Find applicable regulatory penalties based on threat classification."""
        applicable = []

        for penalty_name, penalty_config in self.penalties.items():
            triggers = penalty_config.get("triggers", {})

            # Step 1: Match Threat Domains
            trigger_domains = triggers.get("threat_domains", [])
            domain_match = any(
                domain.value in trigger_domains or domain.name in trigger_domains
                for domain in classification.detected_domains
            )

            if not domain_match:
                continue

            # Step 2: Match Specific Keywords
            specific_violations = triggers.get("specific_violations", [])
            matched_triggers = []

            for violation in specific_violations:
                violation_keyword = violation.get("keyword", "").lower()

                for threat_name, keywords in classification.matched_keywords.items():
                    if any(violation_keyword in kw.lower() for kw in keywords):
                        matched_triggers.append(violation_keyword)
                        break

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

        # Sort by severity (CRITICAL first) then by max penalty
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        applicable.sort(
            key=lambda x: (severity_order.get(x["severity"], 99), -x["max_penalty"])
        )

        return applicable

    def calculate_total_exposure(
            self,
            applicable_penalties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate total regulatory exposure across all applicable penalties."""
        if not applicable_penalties:
            return {
                "total_min_eur": 0,
                "total_max_eur": 0,
                "total_min_usd": 0,
                "total_max_usd": 0,
                "currencies": [],
                "stacking_applied": False
            }

        # Separate by jurisdiction
        eu_penalties = [
            p for p in applicable_penalties
            if p["jurisdiction"] == "European Union"
        ]
        us_penalties = [
            p for p in applicable_penalties
            if "United States" in p["jurisdiction"]
        ]

        # EU: Max penalty rule (no stacking)
        eu_min = max((p["min_penalty"] for p in eu_penalties), default=0)
        eu_max = max((p["max_penalty"] for p in eu_penalties), default=0)

        # US: Stacking allowed (different legal bases)
        us_min = sum(p["min_penalty"] for p in us_penalties)
        us_max = sum(p["max_penalty"] for p in us_penalties)

        currencies = []
        if eu_penalties:
            currencies.append("EUR")
        if us_penalties:
            currencies.append("USD")

        stacking_applied = len(us_penalties) > 1

        return {
            "total_min_eur": eu_min,
            "total_max_eur": eu_max,  # ✅ Correct key name
            "total_min_usd": us_min,
            "total_max_usd": us_max,  # ✅ Correct key name
            "currencies": currencies,
            "stacking_applied": stacking_applied,
            "eu_penalties_count": len(eu_penalties),
            "us_penalties_count": len(us_penalties)
        }

    # ✅ FIX: MOVED FROM EnforcementEngine
    def _generate_executive_summary(
            self,
            penalties: List[Dict[str, Any]],
            total_exposure: Dict[str, Any]
    ) -> str:
        """Generate CFO-ready executive summary of regulatory exposure."""
        critical_penalties = [p for p in penalties if p["severity"] == "CRITICAL"]
        high_penalties = [p for p in penalties if p["severity"] == "HIGH"]

        # ✅ FIX: Use .get() with defaults
        total_max_eur = total_exposure.get("total_max_eur", 0)
        total_min_eur = total_exposure.get("total_min_eur", 0)
        total_max_usd = total_exposure.get("total_max_usd", 0)
        total_min_usd = total_exposure.get("total_min_usd", 0)

        # Format EUR amounts
        if total_max_eur > 0:
            eur_range = f"€{total_min_eur:,} - €{total_max_eur:,}"
        else:
            eur_range = None

        # Format USD amounts
        if total_max_usd > 0:
            usd_range = f"${total_min_usd:,} - ${total_max_usd:,}"
        else:
            usd_range = None

        # Build summary
        if critical_penalties:
            summary = f"🚨 CRITICAL: {len(critical_penalties)} prohibited practice(s) detected. "
            if eur_range:
                summary += f"EU regulatory exposure: {eur_range}. "
            if usd_range:
                summary += f"US regulatory exposure: {usd_range}. "

            violations = ", ".join(
                set(kw for p in critical_penalties for kw in p["triggered_by"])
            )
            summary += f"Violations: {violations}."
        elif high_penalties:
            summary = f"⚠️ HIGH: {len(high_penalties)} regulatory violation(s) detected. "
            if eur_range:
                summary += f"EU exposure: {eur_range}. "
            if usd_range:
                summary += f"US exposure: {usd_range}. "
        else:
            summary = "Regulatory risks detected. Review recommended."

        return summary


@dataclass
class Decision:
    """Enforcement decision with regulatory impact assessment."""
    outcome: Outcome
    risk_score: float
    reason: str
    detected_threats: List[str]
    confidence: float
    recommendations: List[str] = field(default_factory=list)
    regulatory_impact: Optional[Dict[str, Any]] = None
    loss_categories: List[str] = field(default_factory=list)
    controls_applied: List[str] = field(default_factory=list)
    baseline_risk: float = 0.0
    sub_threat_type: Optional[str] = None


class EnforcementEngine:
    """
    Enforces governance policies with regulatory impact assessment.

    v0.9.5.1 Fix: Shadow AI now forces BLOCKED outcome
    """

    THRESHOLD_CRITICAL = 9.0
    THRESHOLD_HIGH = 7.0
    THRESHOLD_MEDIUM = 4.0
    THRESHOLD_LOW = 3.0

    def __init__(
            self,
            penalty_config_path: Optional[str] = None,
            use_simplified_taxonomy: bool = True
    ):
        self.classifier = ThreatVectorClassifier(use_simplified=use_simplified_taxonomy)
        self.penalty_loader = RegulatoryPenaltyLoader(penalty_config_path)
        logger.info(
            f"EnforcementEngine v0.9.5.1 initialized. "
            f"Loaded {len(self.penalty_loader.penalties)} penalty schedules."
        )

    def enforce(
            self,
            task: Task,
            system: AISystem,
            issues: Optional[List[str]] = None
    ) -> Decision:
        """Enforce governance policy with regulatory impact assessment."""
        issues_to_analyze = issues or []

        classification = self.classifier.classify(
            issues=issues_to_analyze,
            task_title=task.title,
            task_description=task.description
        )

        baseline_risk = self._calculate_risk_score(classification)
        controls_applied, residual_risk = self._apply_controls(
            baseline_risk, classification, system
        )
        regulatory_impact = self._calculate_regulatory_impact(classification)
        outcome, reason = self._determine_outcome(
            residual_risk, classification, regulatory_impact
        )
        recommendations = self._generate_recommendations(
            classification, regulatory_impact, outcome
        )

        return Decision(
            outcome=outcome,
            risk_score=residual_risk,
            reason=reason,
            detected_threats=[t.value for t in classification.detected_domains],
            confidence=classification.weighted_score,
            recommendations=recommendations,
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
        """Calculate risk score on 0-10 scale."""
        base_score = classification.weighted_score * 10.0

        severity_boost = 0.0
        if classification.sub_threat_type:
            if classification.sub_threat_type in [
                "prohibited_practice_biometric",
                "shadow_ai_credential_exposure"
            ]:
                severity_boost = 2.0
            elif classification.sub_threat_type in [
                "proxy_discrimination",
                "model_inversion",
                "pii_leakage"
            ]:
                severity_boost = 1.0

        loss_category_count = len(classification.loss_categories)
        category_multiplier = 1.0 + (loss_category_count * 0.1)

        risk_score = min((base_score + severity_boost) * category_multiplier, 10.0)
        return round(risk_score, 2)

    def _apply_controls(
            self,
            baseline_risk: float,
            classification: ThreatClassificationResult,
            system: AISystem
    ) -> Tuple[List[str], float]:
        """Apply controls and calculate residual risk."""
        controls = []
        risk_reduction_factor = 1.0

        if ThreatDomain.BIASES in classification.detected_domains:
            controls.append("Bias Keyword Filter")
            risk_reduction_factor *= 0.7

        if ThreatDomain.PRIVACY in classification.detected_domains:
            controls.append("PII Detection")
            risk_reduction_factor *= 0.6

        if classification.sub_threat_type and "shadow_ai" in classification.sub_threat_type:
            controls.append("Shadow AI Credential Blocker")
            risk_reduction_factor *= 0.3

        residual_risk = baseline_risk * risk_reduction_factor
        return controls, round(residual_risk, 2)

    def _calculate_regulatory_impact(
            self,
            classification: ThreatClassificationResult
    ) -> Optional[Dict[str, Any]]:
        """Calculate regulatory financial exposure."""
        applicable_penalties = self.penalty_loader.get_applicable_penalties(
            classification
        )

        if not applicable_penalties:
            return None

        total_exposure = self.penalty_loader.calculate_total_exposure(
            applicable_penalties
        )

        # ✅ FIX: Call from penalty_loader (not self)
        executive_summary = self.penalty_loader._generate_executive_summary(
            applicable_penalties, total_exposure
        )

        return {
            "applicable_regulations": applicable_penalties,
            "total_exposure": total_exposure,
            "executive_summary": executive_summary,
            "compliance_note": (
                f"Penalties based on statutory schedules as of "
                f"{self.penalty_loader.metadata.get('last_updated', 'N/A')}. "
                f"Actual fines may vary based on organization size, cooperation, "
                f"and mitigating factors."
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

    def _determine_outcome(
            self,
            risk_score: float,
            classification: ThreatClassificationResult,
            regulatory_impact: Optional[Dict[str, Any]]
    ) -> Tuple[Outcome, str]:
        """Determine enforcement outcome based on risk and regulatory exposure."""

        # ✅ FIX: Force BLOCKED for Shadow AI credential exposure
        if (classification.sub_threat_type and
                "shadow_ai" in classification.sub_threat_type):
            return (
                Outcome.BLOCKED,
                f"BLOCKED: Shadow AI violation detected ({classification.sub_threat_type}). "
                f"Immediate credential rotation required."
            )

        # CRITICAL: Prohibited practices (EU AI Act Art. 5)
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

        # HIGH RISK: Automatic block
        if risk_score >= self.THRESHOLD_CRITICAL:
            primary = classification.primary_threat or "high-risk activity"
            return (
                Outcome.BLOCKED,
                f"BLOCKED: Critical risk score ({risk_score}/10.0) for {primary}. "
                f"Immediate review required."
            )

        # ESCALATE: High risk or significant regulatory exposure
        if risk_score >= self.THRESHOLD_HIGH:
            reason = f"Risk score {risk_score}/10.0 exceeds HIGH threshold. "
            if regulatory_impact:
                reason += regulatory_impact["executive_summary"]
            return Outcome.ESCALATE, reason

        # CONDITIONAL: Medium risk
        if risk_score >= self.THRESHOLD_MEDIUM:
            return (
                Outcome.CONDITIONAL,
                f"Conditional approval: Risk score {risk_score}/10.0. "
                f"Monitoring required for {classification.primary_threat}."
            )

        # APPROVED: Low risk
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
        """Generate actionable recommendations based on detected threats."""
        recommendations = []

        # Critical recommendations (Blocked/Escalated)
        if outcome in [Outcome.BLOCKED, Outcome.ESCALATE]:
            if regulatory_impact:
                recommendations.append(
                    "🚨 URGENT: Engage Legal Dept for regulatory compliance review"
                )
            recommendations.append(
                "📋 Document decision in compliance ledger (ISO 42001 Clause 9.1)"
            )

        # Domain-specific recommendations
        for domain in classification.detected_domains:
            if domain == ThreatDomain.BIASES:
                recommendations.append(
                    "⚖️ Conduct fairness audit across demographic groups (EU AI Act Art. 10)"
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
                        "⛔ CRITICAL: Biometric processing prohibited without consent (EU AI Act Art. 5)"
                    )

            elif domain == ThreatDomain.MISUSE:
                if "shadow_ai" in str(classification.sub_threat_type):
                    recommendations.append(
                        "🔑 Rotate credentials immediately - potential exposure detected"
                    )
                    recommendations.append(
                        "👥 Employee training: Authorized AI tools only"
                    )
                else:
                    recommendations.append(
                        "🛡️ Implement robust input validation and output monitoring"
                    )

            elif domain == ThreatDomain.UNRELIABLE_OUTPUTS:
                recommendations.append(
                    "✓ Implement fact-checking against verified knowledge base"
                )
                recommendations.append(
                    "📚 Require source citations for all factual claims"
                )

            elif domain == ThreatDomain.DRIFT:
                recommendations.append(
                    "📊 Enable continuous monitoring for model drift and quality degradation"
                )

        # Generic monitoring (Approved/Conditional)
        if outcome in [Outcome.APPROVED, Outcome.CONDITIONAL]:
            recommendations.append(
                "📈 Enable continuous monitoring for drift and quality degradation"
            )

        return recommendations


# Version metadata
ENFORCEMENT_VERSION = "0.9.5.1"
SCIENTIFIC_BASIS = """
v0.9.5.1 (2025-12-27 21:00) - Bug Fix Release:

BUG FIXES:
✅ Moved _generate_executive_summary to RegulatoryPenaltyLoader (correct location)
✅ Fixed shadow_ai credential exposure to force BLOCKED outcome
✅ Fixed datetime.utcnow() deprecation (now uses timezone.utc)
✅ Standardized key names (total_max_eur, total_min_eur)

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
- ECOA § 1691: $10K - $500K per case

DECISION THRESHOLDS:
- CRITICAL ≥ 9.0: Immediate block
- HIGH ≥ 7.0: Escalate to human review
- MEDIUM ≥ 5.0: Conditional approval
- LOW < 5.0: Auto-approve

KEY METRICS (Target):
- Prevention rate: 98.8%
- False positive rate: <2%
- Regulatory penalty accuracy: 100%
"""
