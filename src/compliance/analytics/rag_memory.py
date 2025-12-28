"""
Compliance Memory RAG (Retrieval-Augmented Generation)

Implements:
- ISO 42001 A.7.5 (Data Provenance)
- ISO 42001 9.1 (Monitoring and Measurement)
- Historical violation tracking
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger("btv.memory")


class ComplianceMemoryRAG:
    """
    Simplified RAG system for compliance and auditing

    Features:
    - Historical violation storage
    - Similar task queries (text-based search)
    - Analytics by tenant/period

    Future: Upgrade to vector embeddings (ChromaDB, Pinecone)
    """

    def __init__(self, memory_path: Path):
        """
        Initialize compliance memory

        Args:
            memory_path: Directory to store memory
        """
        self.memory_path = Path(memory_path)
        self.violations_file = self.memory_path / "violations.jsonl"

        # Create directory structure
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.violations_file.touch(exist_ok=True)

        logger.info(f"ComplianceMemoryRAG initialized at {self.memory_path}")

    def add_violation(
            self,
            task_title: str,
            system_id: str,
            risk: float,
            reason: str
    ):
        """
        Log violation to history

        Args:
            task_title: Title of the violating task
            system_id: System ID
            risk: Risk score
            reason: Reason for blocking

        Compliance:
            ISO 42001 9.1 (Monitoring and Measurement)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_title": task_title[:500],  # Limit size
            "system_id": system_id,
            "risk_score": round(risk, 2),
            "reason": reason
        }

        with open(self.violations_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.warning(
            f"Violation logged: {system_id} | Risk: {risk:.2f} | "
            f"Task: {task_title[:50]}..."
        )

    def query_similar(self, task_title: str, limit: int = 5) -> List[Dict]:
        """
        Search for similar violations (simple text search)

        Args:
            task_title: Task title to search for
            limit: Maximum number of results

        Returns:
            List of similar violations

        Note:
            Current implementation uses keyword-based search.
            TODO: Upgrade to semantic embeddings (sentence-transformers)
        """
        if not self.violations_file.exists():
            return []

        results = []
        task_lower = task_title.lower()
        task_words = set(task_lower.split())

        with open(self.violations_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())

                    # Simple similarity (common words)
                    entry_words = set(entry["task_title"].lower().split())
                    common_words = task_words & entry_words

                    if len(common_words) >= 2:  # At least 2 words in common
                        entry["similarity"] = len(common_words) / max(len(task_words), 1)
                        results.append(entry)

                except json.JSONDecodeError:
                    continue

        # Sort by similarity (descending)
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

        if results:
            logger.info(
                f"Found {len(results[:limit])} similar violations for task: "
                f"{task_title[:50]}..."
            )

        return results[:limit]

    def get_violations_by_tenant(
            self,
            tenant_id: str,
            days: int = 30
    ) -> List[Dict]:
        """
        Retrieve violations for a tenant within a specific period

        Args:
            tenant_id: Tenant ID
            days: Number of days to look back

        Returns:
            List of tenant violations

        Note:
            Current implementation returns all (no tenant filter).
            TODO: Add tenant_id to violation log
        """
        violations = []

        if self.violations_file.exists():
            with open(self.violations_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        violations.append(entry)
                    except json.JSONDecodeError:
                        continue

        logger.info(f"Retrieved {len(violations)} total violations")
        return violations

    def get_statistics(self) -> Dict:
        """
        Return violation statistics

        Returns:
            Dict with aggregated metrics
        """
        violations = []

        if self.violations_file.exists():
            with open(self.violations_file, "r") as f:
                for line in f:
                    try:
                        violations.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

        if not violations:
            return {
                "total_violations": 0,
                "avg_risk_score": 0.0,
                "most_common_reason": None
            }

        # Calculate statistics
        total = len(violations)
        avg_risk = sum(v["risk_score"] for v in violations) / total

        # Most common reason
        reasons = [v["reason"] for v in violations]
        most_common = max(set(reasons), key=reasons.count) if reasons else None

        return {
            "total_violations": total,
            "avg_risk_score": round(avg_risk, 2),
            "most_common_reason": most_common
        }
