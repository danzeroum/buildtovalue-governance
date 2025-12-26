"""
Compliance Memory RAG (Retrieval-Augmented Generation)

Implementa:
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
    Sistema RAG simplificado para compliance e auditoria

    Features:
    - Armazenamento de violações históricas
    - Query de tarefas similares (text-based search)
    - Analytics por tenant/período

    Future: Upgrade para vector embeddings (ChromaDB, Pinecone)
    """

    def __init__(self, memory_path: Path):
        """
        Inicializa compliance memory

        Args:
            memory_path: Diretório para armazenar memória
        """
        self.memory_path = Path(memory_path)
        self.violations_file = self.memory_path / "violations.jsonl"

        # Cria estrutura de diretórios
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
        Registra violação no histórico

        Args:
            task_title: Título da tarefa que violou
            system_id: ID do sistema
            risk: Score de risco
            reason: Razão do bloqueio

        Compliance:
            ISO 42001 9.1 (Monitoring and Measurement)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_title": task_title[:500],  # Limita tamanho
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
        Busca violações similares (busca textual simples)

        Args:
            task_title: Título da tarefa para buscar
            limit: Número máximo de resultados

        Returns:
            Lista de violações similares

        Note:
            Implementação atual usa busca por palavras-chave.
            TODO: Upgrade para embeddings semânticos (sentence-transformers)
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

                    # Similaridade simples (palavras em comum)
                    entry_words = set(entry["task_title"].lower().split())
                    common_words = task_words & entry_words

                    if len(common_words) >= 2:  # Pelo menos 2 palavras em comum
                        entry["similarity"] = len(common_words) / max(len(task_words), 1)
                        results.append(entry)

                except json.JSONDecodeError:
                    continue

        # Ordena por similaridade (descendente)
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
        Busca violações de um tenant em período específico

        Args:
            tenant_id: ID do tenant
            days: Número de dias para lookback

        Returns:
            Lista de violações do tenant

        Note:
            Implementação atual retorna todas (sem filtro de tenant).
            TODO: Adicionar tenant_id no violation log
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
        Retorna estatísticas de violações

        Returns:
            Dict com métricas agregadas
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

        # Calcula estatísticas
        total = len(violations)
        avg_risk = sum(v["risk_score"] for v in violations) / total

        # Razão mais comum
        reasons = [v["reason"] for v in violations]
        most_common = max(set(reasons), key=reasons.count) if reasons else None

        return {
            "total_violations": total,
            "avg_risk_score": round(avg_risk, 2),
            "most_common_reason": most_common
        }
