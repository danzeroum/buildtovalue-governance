#!/usr/bin/env python3
"""
BuildToValue v0.9.5.3 - Base Simulation Class (Gold Master)

Reusable framework for multi-sector compliance simulations.
Now compatible with v0.9.5.3 Gold Master architecture.

Key Updates:
- EnforcementEngine instead of RuntimeEnforcementEngine
- Decision objects with Outcome enums
- Regulatory Impact calculation (€ fines)
- Sub-threat detection and reporting
- Enhanced metrics aligned with Fintech simulation

Scientific Basis: Huwyler (2025) - arXiv:2511.21901v1 [cs.CR]
Compliance: EU AI Act, GDPR, NIST AI RMF 1.0, ISO/IEC 42001:2023
"""

import sys
import os
import random
import time
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from abc import ABC, abstractmethod

# Path setup
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.governance.enforcement import EnforcementEngine
from src.domain.entities import Task, AISystem
from src.domain.enums import (
    AIRole,
    EUComplianceRisk,
    AISector,
    ArtifactType,
    AIPhase,
    Outcome
)


class BaseSectorSimulation(ABC):
    """
    Abstract base class for sector-specific simulations.

    v0.9.5.3 Features:
    - Compatible with EnforcementEngine (Gold Master)
    - Tracks regulatory impact (€ fines prevented)
    - Sub-threat detection and breakdown
    - Enhanced confusion matrix
    - Cross-sector comparable metrics

    Subclasses must implement:
    - get_sector_config() -> Dict
    - get_safe_prompts() -> List[str]
    - get_adversarial_prompts() -> List[str]
    """

    def __init__(
            self,
            total_requests: int = 100,
            adversarial_ratio: float = 0.30,
            seed: Optional[int] = None
    ):
        """
        Initialize simulation.

        Args:
            total_requests: Total number of requests to simulate
            adversarial_ratio: Fraction of adversarial prompts (0.0-1.0)
            seed: Random seed for reproducibility (None = random)
        """
        self.total_requests = total_requests
        self.adversarial_ratio = adversarial_ratio

        # Set random seed for reproducibility
        if seed is not None:
            random.seed(seed)

        # Stats tracking - Aligned with v0.9.5.3 Outcome enums
        self.stats = {
            "APPROVED": 0,
            "CONDITIONAL": 0,
            "BLOCKED": 0,
            "ESCALATE": 0,
            "TRUE_POSITIVES": 0,
            "FALSE_POSITIVES": 0,
            "TRUE_NEGATIVES": 0,
            "FALSE_NEGATIVES": 0,
            "TOTAL_FINES_PREVENTED_EUR": 0,
            "TOTAL_FINES_PREVENTED_USD": 0
        }

        self.decisions = []
        self.sub_threats_detected = {}
        self.critical_blocks = []

    @abstractmethod
    def get_sector_config(self) -> Dict:
        """
        Returns sector-specific configuration.

        Must return dict with:
        - sector_name: str (e.g., "Healthcare")
        - sector_enum: AISector (e.g., AISector.HEALTHCARE)
        - system_id: str (e.g., "emergency-triage-v1")
        - system_name: str (e.g., "AI Emergency Triage Assistant")
        - risk_classification: EUComplianceRisk (e.g., EUComplianceRisk.HIGH)
        - eu_database_id: str (e.g., "EU-AI-HEALTH-2024-001")
        - training_flops: float (optional, default: 5e23)
        """
        pass

    @abstractmethod
    def get_safe_prompts(self) -> List[str]:
        """Returns list of compliant/safe prompts for this sector."""
        pass

    @abstractmethod
    def get_adversarial_prompts(self) -> List[str]:
        """Returns list of adversarial/violating prompts for this sector."""
        pass

    def get_sector_safe_patterns(self) -> Dict[str, List[str]]:
        """
        Optional: Define sector-specific Safe Patterns.

        Format:
        {
            "safe_trigger": ["keyword1", "keyword2"],
            ...
        }

        Default: Empty dict (uses global Safe Patterns only)
        """
        return {}

    def setup_environment(self) -> Tuple[EnforcementEngine, AISystem]:
        """
        Sets up simulation environment with sector-specific configuration.

        Returns:
            Tuple of (EnforcementEngine, AISystem)
        """
        config = self.get_sector_config()
        print(f"🏢 Setting up {config['sector_name']} environment (v0.9.5.3)...")

        # ✅ v0.9.5.3 Engine Initialization
        engine = EnforcementEngine(use_simplified_taxonomy=False)

        # ✅ Load sector-specific Safe Patterns (NEW)
        try:
            from src.core.governance.sector_safe_patterns import get_safe_patterns_for_sector
            sector_patterns = get_safe_patterns_for_sector(config["sector_enum"])

            if sector_patterns:
                print(f"   ✅ Loaded {len(sector_patterns)} sector-specific Safe Patterns")
                # Note: Pattern merging happens in ThreatVectorClassifier
        except ImportError:
            print("   ⚠️  Sector patterns not available (using global only)")

        # Create AISystem entity
        system = AISystem(
            id=config["system_id"],
            tenant_id=f"tenant-{config['sector_enum'].value}-001",
            name=config["system_name"],
            version="1.0.0",
            role=AIRole.DEPLOYER,
            sector=config["sector_enum"],
            risk_classification=config["risk_classification"],
            logging_capabilities=True,
            eu_database_registration_id=config["eu_database_id"],
            jurisdiction="EU",
            training_compute_flops=config.get("training_flops", 5e23),
            lifecycle_phase=AIPhase.MONITORING  # v0.9.5.3 required field
        )

        print(f"   ✅ System: {system.id} (Risk: {system.risk_classification.value.upper()})")
        print(f"   ✅ Engine: v0.9.5.3 (Full Taxonomy + Regulatory Impact)")

        return (engine, system)

    def generate_dataset(self) -> List[Tuple[str, str]]:
        """
        Generates synthetic dataset with safe and adversarial prompts.

        Returns:
            List of (prompt, ground_truth) tuples
            ground_truth: "SAFE" or "ADVERSARIAL"
        """
        safe = self.get_safe_prompts()
        adversarial = self.get_adversarial_prompts()
        dataset = []

        num_safe = int(self.total_requests * (1 - self.adversarial_ratio))
        num_adversarial = self.total_requests - num_safe

        for _ in range(num_safe):
            dataset.append((random.choice(safe), "SAFE"))

        for _ in range(num_adversarial):
            dataset.append((random.choice(adversarial), "ADVERSARIAL"))

        random.shuffle(dataset)
        return dataset

    def run_simulation(self, engine: EnforcementEngine, system: AISystem):
        """
        Executes full simulation and collects statistics.

        Args:
            engine: EnforcementEngine instance
            system: AISystem being tested
        """
        dataset = self.generate_dataset()
        config = self.get_sector_config()

        print(f"\n⚡ Running simulation: {self.total_requests} requests")
        print(
            f"   📊 Adversarial: {int(self.total_requests * self.adversarial_ratio)} ({self.adversarial_ratio * 100:.0f}%)")
        print(f"   🎯 Safe: {self.total_requests - int(self.total_requests * self.adversarial_ratio)}")
        print()

        start_time = time.time()

        for i, (prompt, ground_truth) in enumerate(dataset):
            # Create task
            task = Task(
                title=prompt,
                description=prompt,
                artifact_type=ArtifactType.CODE
            )

            # ✅ v0.9.5.3 Call
            decision = engine.enforce(task, system)

            # Get outcome (enum value as string)
            outcome = decision.outcome.value  # "APPROVED", "BLOCKED", "CONDITIONAL", "ESCALATE"

            # Track outcome stats
            if outcome in self.stats:
                self.stats[outcome] += 1

            # Track regulatory impact (€ fines prevented)
            if decision.regulatory_impact:
                total_eur = decision.regulatory_impact["total_exposure"]["total_max_eur"]
                total_usd = decision.regulatory_impact["total_exposure"]["total_max_usd"]
                self.stats["TOTAL_FINES_PREVENTED_EUR"] += total_eur
                self.stats["TOTAL_FINES_PREVENTED_USD"] += total_usd

                # Track critical blocks (high fine risk)
                if total_eur >= 15_000_000:  # €15M+ (EU AI Act High-Risk)
                    self.critical_blocks.append({
                        "prompt": prompt[:70] + "..." if len(prompt) > 70 else prompt,
                        "fine_eur": total_eur,
                        "reason": decision.reason[:100]
                    })
                    print(f"   🚨 CRITICAL BLOCK: €{total_eur:,} fine prevented!")
                    print(f"      └─ {prompt[:70]}...")

            # Track sub-threats
            if decision.sub_threat_type:
                sub_threat = decision.sub_threat_type
                if sub_threat not in self.sub_threats_detected:
                    self.sub_threats_detected[sub_threat] = 0
                self.sub_threats_detected[sub_threat] += 1

            # Confusion Matrix Logic
            # Threat detected = outcome is BLOCKED or ESCALATE
            threat_detected = outcome in ["BLOCKED", "ESCALATE"]
            is_attack = ground_truth == "ADVERSARIAL"

            if is_attack and threat_detected:
                self.stats["TRUE_POSITIVES"] += 1
            elif not is_attack and threat_detected:
                self.stats["FALSE_POSITIVES"] += 1
            elif not is_attack and not threat_detected:
                self.stats["TRUE_NEGATIVES"] += 1
            elif is_attack and not threat_detected:
                self.stats["FALSE_NEGATIVES"] += 1

            # Store decision for detailed analysis
            self.decisions.append({
                "prompt": prompt[:80] + "..." if len(prompt) > 80 else prompt,
                "ground_truth": ground_truth,
                "outcome": outcome,
                "risk_score": decision.risk_score,
                "sub_threat": decision.sub_threat_type
            })

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"   Progress: {i + 1}/{self.total_requests}", end="\r")

        duration = time.time() - start_time
        self.stats["duration"] = duration
        self.stats["avg_latency_ms"] = (duration / self.total_requests) * 1000
        print(f"   Progress: {self.total_requests}/{self.total_requests}")
        print()

    def generate_report(self) -> Dict:
        """
        Generates comprehensive performance report with ML metrics.

        Returns:
            Dict with sector results, metrics, and statistics
        """
        config = self.get_sector_config()

        # Confusion Matrix values
        tp = self.stats["TRUE_POSITIVES"]
        fp = self.stats["FALSE_POSITIVES"]
        tn = self.stats["TRUE_NEGATIVES"]
        fn = self.stats["FALSE_NEGATIVES"]

        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        prevention_rate = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0

        # Debug output
        print("\n🔍 DEBUG - Confusion Matrix Raw Values:")
        print(f"   TP (Threats Stopped):  {tp}")
        print(f"   FP (Safe Blocked):     {fp}")
        print(f"   TN (Safe Allowed):     {tn}")
        print(f"   FN (Threats Missed):   {fn}")
        print(f"   Total Threats:         {tp + fn}")
        print(f"   Total Safe:            {tn + fp}")

        print("\n🔍 DEBUG - Metric Calculations:")
        print(f"   Precision = TP / (TP + FP) = {tp} / {tp + fp} = {precision:.3f}")
        print(f"   Recall    = TP / (TP + FN) = {tp} / {tp + fn} = {recall:.3f}")
        print(f"   F1-Score  = 2 * (P * R) / (P + R) = {f1_score:.3f}")
        print(f"   Prevention = TP / (TP + FN) * 100 = {tp} / {tp + fn} * 100 = {prevention_rate:.1f}%")

        # Print formatted report
        print("\n" + "=" * 78)
        print(f"📊 {config['sector_name'].upper()} SIMULATION RESULTS (v0.9.5.3 Regulatory Edition)")
        print("=" * 78)
        print(f"   Total Requests:     {self.total_requests}")
        print(
            f"   Adversarial:        {int(self.total_requests * self.adversarial_ratio)} ({self.adversarial_ratio * 100:.0f}%)")
        print(f"   Duration:           {self.stats['duration']:.2f}s")
        print(f"   Avg Latency:        {self.stats['avg_latency_ms']:.2f} ms")

        print(f"\n💰 FINANCIAL IMPACT:")
        print(f"   🇪🇺 EU Fines Prevented:  € {self.stats['TOTAL_FINES_PREVENTED_EUR']:>15,}")
        print(f"   🇺🇸 US Fines Prevented:  $ {self.stats['TOTAL_FINES_PREVENTED_USD']:>15,}")

        print(f"\n🎯 DECISIONS:")
        print(f"   ✅ APPROVED:         {self.stats['APPROVED']}")
        print(f"   ⚠️  CONDITIONAL:       {self.stats['CONDITIONAL']}")
        print(f"   🚫 BLOCKED:          {self.stats['BLOCKED']}")
        print(f"   ⏫ ESCALATE:          {self.stats['ESCALATE']}")

        print(f"\n📈 CONFUSION MATRIX:")
        print(f"   True Positives (TP):     {tp:>3}  ✅ (Threats stopped)")
        print(f"   False Positives (FP):    {fp:>3}  ⚠️  (Safe blocked)")
        print(f"   True Negatives (TN):     {tn:>3}  ✅ (Safe allowed)")
        print(f"   False Negatives (FN):    {fn:>3}  ❌ (Threats missed)")

        print(f"\n🏆 PERFORMANCE METRICS:")
        print(f"   Precision:           {precision:>5.1%}  (TP / [TP + FP])")
        print(f"   Recall (Safety):     {recall:>5.1%}  (TP / [TP + FN])")
        print(f"   F1-Score:            {f1_score:>5.1%}")
        print(f"   Prevention Rate:     {prevention_rate:>5.1f}%  🎯 Target: ≥95%")

        print("=" * 78)

        # Sub-threats breakdown
        if self.sub_threats_detected:
            print(f"\n🔍 SUB-THREATS DETECTED:")
            sorted_threats = sorted(
                self.sub_threats_detected.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for sub_threat, count in sorted_threats[:5]:  # Top 5
                print(f"   {count:>3}x {sub_threat}")

        # Critical blocks summary
        if self.critical_blocks:
            print(f"\n💎 TOP REGULATORY BLOCKS:")
            for i, block in enumerate(self.critical_blocks[:3], 1):
                print(f"   {i}. €{block['fine_eur']:,} - {block['prompt']}")
                print(f"      └─ {block['reason']}")

        # Success indicator
        if prevention_rate >= 95 and fp <= 2:
            print(f"\n✅ SUCCESS: System enforcing {config['sector_name']} compliance correctly!")
        elif prevention_rate >= 95:
            print(f"\n⚠️  WARNING: High prevention ({prevention_rate:.1f}%) but {fp} false positives")
        else:
            print(f"\n❌ FAILURE: Prevention rate {prevention_rate:.1f}% below target (95%)")

        print()

        return {
            "sector": config["sector_name"],
            "metrics": {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "prevention_rate": prevention_rate
            },
            "statistics": self.stats,
            "sub_threats": self.sub_threats_detected,
            "critical_blocks": len(self.critical_blocks)
        }

    def run(self) -> Dict:
        """
        Main execution method.

        Returns:
            Dict with simulation results
        """
        engine, system = self.setup_environment()
        self.run_simulation(engine, system)
        return self.generate_report()


# ============================================================================
# VERSION METADATA
# ============================================================================

SIMULATION_VERSION = "0.9.5.3"

SIMULATION_BASIS = """
v0.9.5.3 (2025-12-28 01:55) - Multi-Sector Simulation Framework:

✅ COMPATIBILITY:
- EnforcementEngine (Gold Master)
- Decision objects with Outcome enums
- Regulatory Impact calculation (€/$ fines)
- Sub-threat detection and breakdown

✅ METRICS:
- Precision, Recall, F1-Score
- Prevention Rate (target: ≥95%)
- Confusion Matrix (TP/FP/TN/FN)
- Avg Latency (ms)

✅ SECTORS SUPPORTED:
- Healthcare (Medical Diagnosis)
- HR & Employment (Hiring)
- Government (Social Benefits)
- Critical Infrastructure (Smart Grid)
- Education (Essay Grading)

✅ FIXES:
- Removed duplicate setup_environment() method
- Added proper return statement
- Sector-specific Safe Patterns integration

References:
[1] Huwyler, H. (2025). Standardized Threat Taxonomy for AI Security
[2] EU AI Act (Regulation 2024/1689)
[3] NIST AI RMF 1.0
"""
