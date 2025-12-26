#!/usr/bin/env python3
"""
BuildToValue - Base Simulation Class
Reusable framework for multi-sector compliance simulations
"""

import sys
import os
import random
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
from abc import ABC, abstractmethod

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.governance.enforcement import RuntimeEnforcementEngine
from src.core.registry.system_registry import SystemRegistry
from src.domain.entities import Task, AISystem
from src.domain.enums import AIRole, EUComplianceRisk, AISector, ArtifactType


class BaseSectorSimulation(ABC):
    """
    Abstract base class for sector-specific simulations

    Implements common functionality:
        - Environment setup
        - Dataset generation
        - Simulation execution
        - Report generation

    Subclasses must implement:
        - get_sector_config()
        - get_safe_prompts()
        - get_adversarial_prompts()
    """

    def __init__(self, total_requests: int = 1150, adversarial_ratio: float = 0.30):
        self.total_requests = total_requests
        self.adversarial_ratio = adversarial_ratio
        self.config_path = Path("src/config/governance.yaml")
        self.memory_path = Path("data/compliance_memory")

        self.stats = {
            "ALLOWED": 0,
            "BLOCKED": 0,
            "ESCALATED": 0,
            "TRUE_POSITIVES": 0,
            "FALSE_POSITIVES": 0,
            "TRUE_NEGATIVES": 0,
            "FALSE_NEGATIVES": 0
        }
        self.decisions = []

    @abstractmethod
    def get_sector_config(self) -> Dict:
        """
        Returns sector-specific configuration

        Must return dict with:
            - sector_name: str
            - sector_enum: AISector
            - system_id: str
            - system_name: str
            - risk_classification: EUComplianceRisk
            - max_risk_level: float (autonomy matrix)
            - eu_database_id: str
        """
        pass

    @abstractmethod
    def get_safe_prompts(self) -> List[str]:
        """Returns list of compliant/safe prompts for this sector"""
        pass

    @abstractmethod
    def get_adversarial_prompts(self) -> List[str]:
        """Returns list of adversarial/violating prompts for this sector"""
        pass

    def setup_environment(self) -> Tuple[RuntimeEnforcementEngine, AISystem, str]:
        """
        Sets up simulation environment with sector-specific configuration
        """
        config = self.get_sector_config()

        print(f"🏢 Setting up {config['sector_name']} environment...")

        registry = SystemRegistry("sqlite:///:memory:")
        engine = RuntimeEnforcementEngine(self.config_path, self.memory_path)

        # Tenant setup
        tenant_id = f"tenant-{config['sector_enum'].value}-550e8400-e29b-41d4-a716-446655440000"
        registry.register_tenant(
            tenant_id=tenant_id,
            name=f"{config['sector_name']} Organization EU",
            policy={
                "autonomy_matrix": {
                    "production": {
                        "max_risk_level": config.get("max_risk_level", 3.0)
                    }
                },
                "custom_rules": config.get("custom_rules", {})
            }
        )

        # System setup
        system = AISystem(
            id=config["system_id"],
            tenant_id=tenant_id,
            name=config["system_name"],
            version="1.0.0",
            role=AIRole.DEPLOYER,
            sector=config["sector_enum"],
            risk_classification=config["risk_classification"],
            logging_capabilities=True,
            eu_database_registration_id=config["eu_database_id"],
            jurisdiction="EU",
            training_compute_flops=config.get("training_flops", 5e23)
        )
        registry.register_system(system, requesting_tenant=tenant_id)

        print(f"   ✅ Tenant: {tenant_id}")
        print(f"   ✅ System: {system.id} (Risk: {system.risk_classification.value.upper()})")

        return engine, system, tenant_id

    def generate_dataset(self) -> List[Tuple[str, str]]:
        """
        Generates synthetic dataset with safe and adversarial prompts
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

    def run_simulation(self, engine: RuntimeEnforcementEngine, system: AISystem):
        """
        Executes full simulation and collects statistics
        """
        dataset = self.generate_dataset()

        print(f"\n⚡ Running {self.get_sector_config()['sector_name']} simulation...")
        print(f"   Requests: {self.total_requests} | Adversarial: {self.adversarial_ratio * 100:.0f}%")
        print()

        start_time = time.time()

        for i, (prompt, ground_truth) in enumerate(dataset):
            task = Task(title=prompt, artifact_type=ArtifactType.CODE)
            result = engine.enforce(task, system, env="production")

            decision = result["decision"]
            self.stats[decision] += 1

            if result.get("escalation_required"):
                self.stats["ESCALATED"] += 1

            # Confusion matrix
            if ground_truth == "ADVERSARIAL":
                if decision == "BLOCKED":
                    self.stats["TRUE_POSITIVES"] += 1
                else:
                    self.stats["FALSE_NEGATIVES"] += 1
            else:
                if decision == "ALLOWED":
                    self.stats["TRUE_NEGATIVES"] += 1
                else:
                    self.stats["FALSE_POSITIVES"] += 1

            self.decisions.append({
                "prompt": prompt[:80] + "..." if len(prompt) > 80 else prompt,
                "ground_truth": ground_truth,
                "decision": decision,
                "risk_score": result["risk_score"]
            })

            if (i + 1) % 100 == 0 or (i + 1) == self.total_requests:
                progress = ((i + 1) / self.total_requests) * 100
                print(f"   Progress: {i + 1}/{self.total_requests} ({progress:.1f}%)", end="\r")

        duration = time.time() - start_time
        self.stats["duration"] = duration
        self.stats["avg_latency_ms"] = (duration / self.total_requests) * 1000

        print("\n")

    def generate_report(self) -> Dict:
        """
        Generates performance report with ML metrics
        """
        config = self.get_sector_config()

        tp = self.stats["TRUE_POSITIVES"]
        fp = self.stats["FALSE_POSITIVES"]
        tn = self.stats["TRUE_NEGATIVES"]
        fn = self.stats["FALSE_NEGATIVES"]

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        total_adversarial = int(self.total_requests * self.adversarial_ratio)
        prevention_rate = (tp / total_adversarial * 100) if total_adversarial > 0 else 0

        print("=" * 70)
        print(f"📊 {config['sector_name'].upper()} SIMULATION RESULTS")
        print("=" * 70)
        print(f"\n### Dataset: {self.total_requests} requests ({self.adversarial_ratio * 100:.0f}% adversarial)")
        print(f"\n### Decisions")
        print(f"   ✅ ALLOWED:   {self.stats['ALLOWED']}")
        print(f"   🛡️  BLOCKED:   {self.stats['BLOCKED']}")
        print(f"   👤 ESCALATED: {self.stats['ESCALATED']}")
        print(f"\n### Performance Metrics")
        print(f"   Precision:        {precision:.2%}")
        print(f"   Recall:           {recall:.2%}")
        print(f"   F1-Score:         {f1_score:.2%}")
        print(f"   Prevention Rate:  {prevention_rate:.1f}% ⭐")
        print(f"   Avg Latency:      {self.stats['avg_latency_ms']:.2f} ms")
        print("=" * 70)
        print()

        return {
            "sector": config["sector_name"],
            "metrics": {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "prevention_rate": prevention_rate
            },
            "statistics": self.stats
        }

    def run(self) -> Dict:
        """
        Main execution method
        """
        engine, system, tenant_id = self.setup_environment()
        self.run_simulation(engine, system)
        return self.generate_report()
