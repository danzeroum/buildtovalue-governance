#!/usr/bin/env python3
"""
BuildToValue v0.9.5 - Enforcement Engine Unit Tests
Validates regulatory impact calculation, decision logic, and YAML fallback

Test Coverage:
- Regulatory penalty calculation (EU AI Act, GDPR, ECOA)
- Total exposure aggregation (stacking rules)
- Decision outcome determination (thresholds)
- YAML loading and fallback mechanism
- Control application and risk reduction
- Executive summary generation
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.governance.enforcement import (
    EnforcementEngine,
    RegulatoryPenaltyLoader,
    Decision
)
from src.core.governance.threat_classifier import (
    ThreatClassificationResult,
    ThreatVectorClassifier
)
from src.domain.enums import ThreatDomain, Outcome
from src.domain.models import Task, AISystem


class TestRegulatoryPenaltyLoader(unittest.TestCase):
    """Test YAML loading and fallback mechanism (v0.9.5 resilience)."""

    def test_fallback_when_yaml_missing(self):
        """Should use embedded fallback when YAML not found."""
        loader = RegulatoryPenaltyLoader(
            config_path="/nonexistent/path/regulatory_penalties.yaml"
        )

        # Should load fallback penalties
        self.assertGreater(len(loader.penalties), 0)

        # Should have EU AI Act prohibited practices
        self.assertIn("eu_ai_act_prohibited_practices", loader.penalties)

        # Metadata should indicate fallback
        self.assertIn("fallback", loader.metadata.get("version", ""))

    def test_yaml_loading_success(self):
        """Should load penalties from valid YAML."""
        # Create temporary YAML file
        yaml_content = """
metadata:
  version: "0.9.5-test"
  last_updated: "2025-12-27T16:13:00Z"
  legal_review_date: "2025-12-15"

penalties:
  test_penalty:
    jurisdiction: "Test"
    regulation: "Test Regulation"
    penalty:
      currency: "EUR"
      min_fine: 1000000
      max_fine: 5000000
    triggers:
      threat_domains: ["PRIVACY"]
    severity: "HIGH"
"""

        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            loader = RegulatoryPenaltyLoader(config_path=temp_path)

            # Should load custom penalty
            self.assertIn("test_penalty", loader.penalties)
            self.assertEqual(
                loader.penalties["test_penalty"]["penalty"]["max_fine"],
                5000000
            )

            # Metadata should match
            self.assertEqual(loader.metadata["version"], "0.9.5-test")

        finally:
            os.unlink(temp_path)

    def test_yaml_parsing_error_triggers_fallback(self):
        """Should fallback on YAML parsing errors."""
        # Create invalid YAML
        yaml_content = """
invalid: yaml: content:
  - malformed
    broken syntax
"""

        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            loader = RegulatoryPenaltyLoader(config_path=temp_path)

            # Should use fallback
            self.assertIn("fallback", loader.metadata.get("version", ""))
            self.assertGreater(len(loader.penalties), 0)

        finally:
            os.unlink(temp_path)


class TestApplicablePenalties(unittest.TestCase):
    """Test penalty matching logic (v0.9.5 core feature)."""

    def setUp(self):
        self.loader = RegulatoryPenaltyLoader()
        self.classifier = ThreatVectorClassifier(use_simplified=False)

    def test_emotion_recognition_triggers_eu_ai_act_prohibited(self):
        """Emotion recognition should trigger €35M penalty (Art. 5)."""
        issues = [
            "System uses emotion recognition via micro-expressions"
        ]

        classification = self.classifier.classify(issues)
        applicable = self.loader.get_applicable_penalties(classification)

        # Should match EU AI Act Prohibited Practices
        prohibited = [
            p for p in applicable
            if "prohibited" in p["penalty_id"].lower()
        ]

        self.assertGreater(len(prohibited), 0)

        penalty = prohibited[0]
        self.assertEqual(penalty["severity"], "CRITICAL")
        self.assertEqual(penalty["max_penalty"], 35000000)
        self.assertIn("emotion recognition", penalty["triggered_by"])

    def test_proxy_discrimination_triggers_eu_ai_act_high_risk(self):
        """Proxy discrimination should trigger €15M penalty (Art. 9-15)."""
        issues = [
            "Model uses zip code as proxy for race in loan decisions"
        ]

        classification = self.classifier.classify(issues)
        applicable = self.loader.get_applicable_penalties(classification)

        # Should match EU AI Act High-Risk Systems
        high_risk = [
            p for p in applicable
            if "high_risk" in p["penalty_id"].lower()
        ]

        self.assertGreater(len(high_risk), 0)

        penalty = high_risk[0]
        self.assertEqual(penalty["severity"], "HIGH")
        self.assertEqual(penalty["max_penalty"], 15000000)

    def test_pii_leakage_triggers_gdpr(self):
        """PII leakage should trigger GDPR Art. 83 (€20M)."""
        issues = [
            "Model outputs leaked personal data via inversion attack"
        ]

        classification = self.classifier.classify(issues)
        applicable = self.loader.get_applicable_penalties(classification)

        # Should match GDPR
        gdpr = [
            p for p in applicable
            if "gdpr" in p["penalty_id"].lower()
        ]

        self.assertGreater(len(gdpr), 0)

        penalty = gdpr[0]
        self.assertEqual(penalty["max_penalty"], 20000000)
        self.assertIn("pii leakage", penalty["triggered_by"])

    def test_redlining_triggers_ecoa(self):
        """Redlining should trigger ECOA penalties (US)."""
        issues = [
            "Algorithm engages in redlining by denying loans in certain zip codes"
        ]

        classification = self.classifier.classify(issues)
        applicable = self.loader.get_applicable_penalties(classification)

        # Should match ECOA
        ecoa = [
            p for p in applicable
            if "ecoa" in p["penalty_id"].lower()
        ]

        self.assertGreater(len(ecoa), 0)

        penalty = ecoa[0]
        self.assertEqual(penalty["currency"], "USD")
        self.assertIn("redlining", penalty["triggered_by"])


class TestTotalExposureCalculation(unittest.TestCase):
    """Test exposure aggregation and stacking rules (v0.9.5)."""

    def setUp(self):
        self.loader = RegulatoryPenaltyLoader()

    def test_eu_penalties_no_stacking(self):
        """EU penalties should use max penalty rule (no stacking)."""
        # Simulate two EU penalties
        penalties = [
            {
                "jurisdiction": "European Union",
                "currency": "EUR",
                "min_penalty": 10000000,
                "max_penalty": 20000000  # GDPR
            },
            {
                "jurisdiction": "European Union",
                "currency": "EUR",
                "min_penalty": 15000000,
                "max_penalty": 35000000  # EU AI Act
            }
        ]

        total = self.loader.calculate_total_exposure(penalties)

        # Should use maximum (€35M), not sum (€55M)
        self.assertEqual(total["total_max_eur"], 35000000)
        self.assertEqual(total["total_min_eur"], 15000000)
        self.assertFalse(total["stacking_applied"])

    def test_us_penalties_stacking_allowed(self):
        """US penalties should stack (different legal bases)."""
        # Simulate two US penalties
        penalties = [
            {
                "jurisdiction": "United States",
                "currency": "USD",
                "min_penalty": 10000,
                "max_penalty": 500000  # ECOA
            },
            {
                "jurisdiction": "California, United States",
                "currency": "USD",
                "min_penalty": 2500,
                "max_penalty": 7500  # CCPA
            }
        ]

        total = self.loader.calculate_total_exposure(penalties)

        # Should stack (sum)
        self.assertEqual(total["total_max_usd"], 507500)
        self.assertEqual(total["total_min_usd"], 12500)
        self.assertTrue(total["stacking_applied"])

    def test_mixed_jurisdiction_exposure(self):
        """Handle mixed EU and US penalties correctly."""
        penalties = [
            {
                "jurisdiction": "European Union",
                "currency": "EUR",
                "min_penalty": 15000000,
                "max_penalty": 35000000
            },
            {
                "jurisdiction": "United States",
                "currency": "USD",
                "min_penalty": 10000,
                "max_penalty": 500000
            }
        ]

        total = self.loader.calculate_total_exposure(penalties)

        # Should have both currencies
        self.assertIn("EUR", total["currencies"])
        self.assertIn("USD", total["currencies"])

        # Should calculate both separately
        self.assertEqual(total["total_max_eur"], 35000000)
        self.assertEqual(total["total_max_usd"], 500000)


class TestEnforcementDecisions(unittest.TestCase):
    """Test decision logic and outcome determination (v0.9.5)."""

    def setUp(self):
        self.engine = EnforcementEngine(use_simplified_taxonomy=False)

        # Mock AISystem
        self.system = MagicMock(spec=AISystem)
        self.system.name = "TestAISystem"
        self.system.type = "generative"
        self.system.exposure = "public"

    def test_prohibited_practice_blocks_immediately(self):
        """Prohibited practices (emotion recognition) should block."""
        task = Task(
            title="Analyze customer emotions",
            description="Use emotion recognition to assess customer sentiment via facial analysis"
        )

        decision = self.engine.enforce(task, self.system)

        # Should BLOCK
        self.assertEqual(decision.outcome, Outcome.BLOCKED)

        # Should have CRITICAL regulatory impact
        self.assertIsNotNone(decision.regulatory_impact)
        self.assertIn(
            "CRITICAL",
            decision.regulatory_impact["executive_summary"]
        )

        # Should have €35M exposure
        self.assertEqual(
            decision.regulatory_impact["total_exposure"]["max_eur"],
            35000000
        )

    def test_high_risk_escalates(self):
        """High-risk violations should escalate to human review."""
        task = Task(
            title="Loan approval model",
            description="Use zip code as feature to predict loan default risk"
        )

        decision = self.engine.enforce(task, self.system)

        # Should ESCALATE or BLOCK
        self.assertIn(decision.outcome, [Outcome.ESCALATE, Outcome.BLOCKED])

        # Should have regulatory impact
        self.assertIsNotNone(decision.regulatory_impact)

        # Should identify proxy discrimination
        self.assertEqual(decision.sub_threat_type, "proxy_discrimination")

    def test_medium_risk_conditional_approval(self):
        """Medium risk should result in conditional approval."""
        task = Task(
            title="Content moderation",
            description="Filter potentially harmful content in user posts"
        )

        # This should have some risk but not critical
        decision = self.engine.enforce(task, self.system, issues=[
            "Some bias detected in content filtering"
        ])

        # Should approve or conditionally approve (depends on exact score)
        self.assertIn(
            decision.outcome,
            [Outcome.APPROVED, Outcome.CONDITIONAL]
        )

    def test_low_risk_approves(self):
        """Low-risk tasks should auto-approve."""
        task = Task(
            title="Data visualization",
            description="Generate charts from sales data"
        )

        decision = self.engine.enforce(task, self.system)

        # Should APPROVE
        self.assertEqual(decision.outcome, Outcome.APPROVED)

        # Should have low risk score
        self.assertLess(decision.risk_score, 5.0)

    def test_shadow_ai_credential_exposure_blocks(self):
        """Shadow AI credential exposure should block immediately."""
        task = Task(
            title="Debug API integration",
            description="Test API with key: sk-proj-abc123xyz456def789ghi012jkl345"
        )

        decision = self.engine.enforce(task, self.system)

        # Should BLOCK
        self.assertEqual(decision.outcome, Outcome.BLOCKED)

        # Should identify credential exposure
        self.assertEqual(decision.sub_threat_type, "shadow_ai_credential_exposure")

        # Should recommend credential rotation
        self.assertTrue(
            any("rotate credential" in rec.lower() for rec in decision.recommendations)
        )


class TestRiskScoreCalculation(unittest.TestCase):
    """Test risk score calculation logic (v0.9.5)."""

    def setUp(self):
        self.engine = EnforcementEngine(use_simplified_taxonomy=False)
        self.classifier = ThreatVectorClassifier(use_simplified=False)

    def test_severity_boost_for_prohibited_practices(self):
        """Prohibited practices should receive +2.0 severity boost."""
        issues = ["Emotion recognition system deployed"]
        classification = self.classifier.classify(issues)

        risk_score = self.engine._calculate_risk_score(classification)

        # Should be in CRITICAL range (≥9.0)
        self.assertGreaterEqual(risk_score, 9.0)

    def test_severity_boost_for_proxy_discrimination(self):
        """Proxy discrimination should receive +1.0 severity boost."""
        issues = ["Model uses zip code to deny loans"]
        classification = self.classifier.classify(issues)

        risk_score = self.engine._calculate_risk_score(classification)

        # Should be in HIGH range (≥7.0)
        self.assertGreaterEqual(risk_score, 7.0)

    def test_loss_category_multiplier(self):
        """Multiple loss categories should increase risk score."""
        issues = [
            "PII leakage via model inversion",  # C+L+R
            "Discriminatory outcomes detected"  # I+L+R
        ]
        classification = self.classifier.classify(issues)

        risk_score = self.engine._calculate_risk_score(classification)

        # Should have multiple loss categories
        self.assertGreater(len(classification.loss_categories), 3)

        # Score should reflect category multiplier
        self.assertGreater(risk_score, 7.0)


class TestControlApplication(unittest.TestCase):
    """Test control application and risk reduction (v0.9.5 foundation for v1.0)."""

    def setUp(self):
        self.engine = EnforcementEngine(use_simplified_taxonomy=False)
        self.classifier = ThreatVectorClassifier(use_simplified=False)
        self.system = MagicMock(spec=AISystem)

    def test_bias_control_reduces_risk(self):
        """Bias Keyword Filter should reduce risk by 30%."""
        issues = ["Discriminatory outcomes in hiring model"]
        classification = self.classifier.classify(issues)

        baseline_risk = self.engine._calculate_risk_score(classification)
        controls, residual_risk = self.engine._apply_controls(
            baseline_risk, classification, self.system
        )

        # Should apply Bias Keyword Filter
        self.assertIn("Bias Keyword Filter", controls)

        # Should reduce risk (≈30% reduction)
        self.assertLess(residual_risk, baseline_risk * 0.8)

    def test_shadow_ai_blocker_reduces_risk(self):
        """Shadow AI Blocker should reduce risk by 70%."""
        issues = ["API key exposed in task description"]
        classification = self.classifier.classify(issues)

        baseline_risk = self.engine._calculate_risk_score(classification)
        controls, residual_risk = self.engine._apply_controls(
            baseline_risk, classification, self.system
        )

        # Should apply Shadow AI Blocker
        self.assertIn("Shadow AI Credential Blocker", controls)

        # Should significantly reduce risk (≈70% reduction)
        self.assertLess(residual_risk, baseline_risk * 0.4)

    def test_multiple_controls_stack(self):
        """Multiple controls should compound risk reduction."""
        issues = [
            "PII leakage detected",  # PII Detection control
            "Discriminatory outcomes found"  # Bias Filter control
        ]
        classification = self.classifier.classify(issues)

        baseline_risk = self.engine._calculate_risk_score(classification)
        controls, residual_risk = self.engine._apply_controls(
            baseline_risk, classification, self.system
        )

        # Should apply multiple controls
        self.assertGreater(len(controls), 1)

        # Compounded reduction should be significant
        self.assertLess(residual_risk, baseline_risk * 0.5)


class TestExecutiveSummaryGeneration(unittest.TestCase):
    """Test executive summary generation (v0.9.5 CFO-ready output)."""

    def setUp(self):
        self.loader = RegulatoryPenaltyLoader()

    def test_critical_summary_includes_amount(self):
        """CRITICAL summary should include financial exposure."""
        penalties = [
            {
                "severity": "CRITICAL",
                "triggered_by": ["emotion recognition"],
                "min_penalty": 15000000,
                "max_penalty": 35000000,
                "currency": "EUR"
            }
        ]

        total_exposure = {
            "total_min_eur": 15000000,
            "total_max_eur": 35000000,
            "currencies": ["EUR"]
        }

        summary = self.loader._generate_executive_summary(
            penalties, total_exposure
        )

        # Should mention CRITICAL
        self.assertIn("CRITICAL", summary)

        # Should include EUR amount
        self.assertIn("€15,000,000", summary)
        self.assertIn("€35,000,000", summary)

        # Should list violation
        self.assertIn("emotion recognition", summary)

    def test_high_summary_format(self):
        """HIGH summary should have warning format."""
        penalties = [
            {
                "severity": "HIGH",
                "triggered_by": ["proxy discrimination"],
                "min_penalty": 7500000,
                "max_penalty": 15000000,
                "currency": "EUR"
            }
        ]

        total_exposure = {
            "total_min_eur": 7500000,
            "total_max_eur": 15000000,
            "currencies": ["EUR"]
        }

        summary = self.loader._generate_executive_summary(
            penalties, total_exposure
        )

        # Should have warning indicator
        self.assertIn("HIGH", summary)
        self.assertIn("€", summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
