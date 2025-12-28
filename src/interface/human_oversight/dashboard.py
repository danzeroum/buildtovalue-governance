"""
Human Oversight Dashboard Service

Implements:
- EU AI Act Art. 14 (Human Oversight)
- ISO 42001 10.2 (Nonconformity and Corrective Action)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger("btv.oversight")


class HumanOversightService:
    """
    Human supervision service for high-risk decisions

    Features:
    - Review request creation
    - Approval/rejection workflow
    - Justification tracking

    Compliance:
        EU AI Act Art. 14 (Human Oversight Requirements)
    """

    def __init__(self, ledger_path: Path):
        """
        Initialize oversight service

        Args:
            ledger_path: Main ledger path (to derive reviews path)
        """
        self.ledger_path = ledger_path
        self.pending_reviews_file = ledger_path.parent / "pending_reviews.jsonl"
        self.pending_reviews_file.touch(exist_ok=True)
        logger.info(f"HumanOversightService initialized")

    def create_review_request(
            self,
            decision: Dict,
            task: Dict,
            system_id: str
    ) -> str:
        """
        Create human review request

        Args:
            decision: Enforcement decision that was blocked
            task: Task data
            system_id: System ID

        Returns:
            Review request ID

        Compliance:
            EU AI Act Art. 14 (Human Oversight)
        """
        request_id = f"REV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{system_id[:8]}"

        review_entry = {
            "request_id": request_id,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "system_id": system_id,
            "task": {
                "title": task.get("title", "")[:200],
                "description": task.get("description", "")[:500]
            },
            "decision": decision,
            "reviewer": None,
            "reviewed_at": None,
            "review_decision": None,
            "justification": None
        }

        with open(self.pending_reviews_file, "a") as f:
            f.write(json.dumps(review_entry) + "\n")

        logger.warning(
            f"🔔 Decision escalated to human review: {request_id} | "
            f"Risk: {decision.get('risk_score')} | System: {system_id}"
        )

        return request_id

    def approve_request(
            self,
            request_id: str,
            reviewer: str,
            justification: str
    ) -> bool:
        """
        Approve review request (admin or auditor only)

        Args:
            request_id: Request ID
            reviewer: Reviewer email/ID
            justification: Approval justification

        Returns:
            True if successful
        """
        return self._update_review(request_id, "APPROVED", reviewer, justification)

    def reject_request(
            self,
            request_id: str,
            reviewer: str,
            justification: str
    ) -> bool:
        """
        Reject review request (maintains block)

        Args:
            request_id: Request ID
            reviewer: Reviewer email/ID
            justification: Rejection justification

        Returns:
            True if successful
        """
        return self._update_review(request_id, "REJECTED", reviewer, justification)

    def _update_review(
            self,
            request_id: str,
            decision: str,
            reviewer: str,
            justification: str
    ) -> bool:
        """
        Update review status

        Note:
            Simplified implementation (append-only log).
            In production: use transactional DB for atomic updates.

        Args:
            request_id: Request ID
            decision: APPROVED or REJECTED
            reviewer: Reviewer email/ID
            justification: Justification

        Returns:
            True if successful
        """
        update_entry = {
            "request_id": request_id,
            "status": decision,
            "reviewer": reviewer,
            "reviewed_at": datetime.now().isoformat(),
            "justification": justification
        }

        # In production: update existing entry in DB
        # Here: just log the update
        with open(self.pending_reviews_file, "a") as f:
            f.write(json.dumps(update_entry) + "\n")

        logger.info(
            f"Review {request_id}: {decision} by {reviewer} | "
            f"Justification: {justification[:100]}..."
        )

        return True

    def get_pending_reviews(self, limit: int = 10) -> List[Dict]:
        """
        List pending reviews

        Args:
            limit: Maximum number of results

        Returns:
            List of pending reviews
        """
        pending = []

        if not self.pending_reviews_file.exists():
            return []

        # Read file and filter by PENDING status
        with open(self.pending_reviews_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("status") == "PENDING":
                        pending.append(entry)
                except json.JSONDecodeError:
                    continue

        # Sort by timestamp (most recent first)
        pending.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        return pending[:limit]
