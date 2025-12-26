"""
Human Oversight Dashboard Service

Implementa:
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
    Serviço de supervisão humana para decisões de alto risco

    Features:
    - Criação de requisições de revisão
    - Workflow de aprovação/rejeição
    - Tracking de justificativas

    Compliance:
        EU AI Act Art. 14 (Human Oversight Requirements)
    """

    def __init__(self, ledger_path: Path):
        """
        Inicializa serviço de oversight

        Args:
            ledger_path: Path do ledger principal (para derivar path das reviews)
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
        Cria requisição de revisão humana

        Args:
            decision: Decisão de enforcement que foi bloqueada
            task: Dados da tarefa
            system_id: ID do sistema

        Returns:
            ID da requisição de revisão

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
            f"Risk: {decision.get('risk_score')} | Sistema: {system_id}"
        )

        return request_id

    def approve_request(
            self,
            request_id: str,
            reviewer: str,
            justification: str
    ) -> bool:
        """
        Aprova requisição de revisão (admin ou auditor apenas)

        Args:
            request_id: ID da requisição
            reviewer: Email/ID do revisor
            justification: Justificativa da aprovação

        Returns:
            True se sucesso
        """
        return self._update_review(request_id, "APPROVED", reviewer, justification)

    def reject_request(
            self,
            request_id: str,
            reviewer: str,
            justification: str
    ) -> bool:
        """
        Rejeita requisição de revisão (mantém bloqueio)

        Args:
            request_id: ID da requisição
            reviewer: Email/ID do revisor
            justification: Justificativa da rejeição

        Returns:
            True se sucesso
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
        Atualiza status da revisão

        Note:
            Implementação simplificada (append-only log).
            Em produção: usar DB transacional para updates atômicos.

        Args:
            request_id: ID da requisição
            decision: APPROVED ou REJECTED
            reviewer: Email/ID do revisor
            justification: Justificativa

        Returns:
            True se sucesso
        """
        update_entry = {
            "request_id": request_id,
            "status": decision,
            "reviewer": reviewer,
            "reviewed_at": datetime.now().isoformat(),
            "justification": justification
        }

        # Em produção: atualizar entrada existente no DB
        # Aqui: apenas logamos a atualização
        with open(self.pending_reviews_file, "a") as f:
            f.write(json.dumps(update_entry) + "\n")

        logger.info(
            f"Review {request_id}: {decision} by {reviewer} | "
            f"Justification: {justification[:100]}..."
        )

        return True

    def get_pending_reviews(self, limit: int = 10) -> List[Dict]:
        """
        Lista revisões pendentes

        Args:
            limit: Número máximo de resultados

        Returns:
            Lista de revisões pendentes
        """
        pending = []

        if not self.pending_reviews_file.exists():
            return []

        # Lê arquivo e filtra por status PENDING
        with open(self.pending_reviews_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("status") == "PENDING":
                        pending.append(entry)
                except json.JSONDecodeError:
                    continue

        # Ordena por timestamp (mais recentes primeiro)
        pending.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        return pending[:limit]
