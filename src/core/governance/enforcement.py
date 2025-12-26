"""
Runtime Enforcement Engine com Merge Conservador de Políticas

Implementa:
- 3-Layer Policy Hierarchy (Global > Tenant > System)
- HMAC-Signed Audit Ledger (tamper-proof)
- ISO 42001 6.1.3 (AI Risk Treatment)
- EU AI Act Art. 12 (Logging)
"""

import yaml
import json
import hashlib
import hmac
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.domain.entities import Task, AISystem
from src.intelligence.routing.adaptive_router import AdaptiveRiskRouter
from src.compliance.analytics.rag_memory import ComplianceMemoryRAG
from src.interface.human_oversight.dashboard import HumanOversightService
from src.core.registry.system_registry import SystemRegistry

logger = logging.getLogger("btv.enforcement")


class RuntimeEnforcementEngine:
    """
    Motor de Enforcement de Governança em Runtime

    Arquitetura:
    1. Global Policy (governance.yaml) - Leis não negociáveis
    2. Tenant Policy (DB) - Regras da empresa
    3. System Policy (DB) - Configurações do projeto

    Security:
    - HMAC-SHA256 signed ledger (tamper-proof)
    - Conservative policy merge (mais restritivo vence)
    - Validation against prohibited practices (Art. 5 EU AI Act)
    """

    def __init__(self, config_path: Path, memory_path: Path):
        """
        Inicializa engine de enforcement

        Args:
            config_path: Caminho para governance.yaml
            memory_path: Diretório para compliance memory
        """
        # Carrega política global (Camada 1 - Lei)
        with open(config_path) as f:
            self.global_policy = yaml.safe_load(f)
            logger.info(f"Global policy loaded: {self.global_policy.get('version', 'unknown')}")

        # Componentes
        self.registry = SystemRegistry()
        self.router = AdaptiveRiskRouter()
        self.memory = ComplianceMemoryRAG(memory_path)

        # Ledger setup (ISO 42001 A.7.5 - Data Provenance)
        self.ledger = Path("logs/enforcement_ledger.jsonl")
        self.ledger.parent.mkdir(exist_ok=True, parents=True)
        self.ledger.touch(exist_ok=True)

        # Oversight (Art. 14 EU AI Act - Human Oversight)
        self.oversight = HumanOversightService(self.ledger)

        # HMAC key para assinatura do ledger
        self.hmac_key = os.getenv("HMAC_KEY", "default-insecure-key-change-in-prod").encode()

        if self.hmac_key == b"default-insecure-key-change-in-prod":
            logger.warning(
                "⚠️  USING DEFAULT HMAC KEY! Set HMAC_KEY environment variable in production!"
            )

    def _validate_tenant_policy(self, policy: Dict) -> Dict:
        """
        Valida que política do tenant não viola leis (Art. 5 EU AI Act)

        Args:
            policy: Política proposta pelo tenant

        Returns:
            Política validada (com regras ilegais removidas)

        Security:
            Previne Privilege Escalation via policy tampering
        """
        validated = policy.copy()
        prohibited = self.global_policy.get("prohibited_practices", [])

        if "custom_rules" in validated:
            for practice in prohibited:
                # Checa se tenant tentou permitir prática proibida
                key = f"allow_{practice}"
                if validated["custom_rules"].get(key, False):
                    logger.warning(
                        f"🚨 SECURITY: Tenant tried to enable PROHIBITED practice: {practice}. "
                        f"This violates Art. 5 EU AI Act. Rule removed from policy."
                    )
                    del validated["custom_rules"][key]

        # Valida limites de risco (não podem exceder global)
        if "autonomy_matrix" in validated:
            for env, limits in validated["autonomy_matrix"].items():
                global_limit = self.global_policy["autonomy_matrix"].get(env, {}).get(
                    "max_risk_level", 5.0
                )
                tenant_limit = limits.get("max_risk_level", 10.0)

                if tenant_limit > global_limit:
                    logger.warning(
                        f"Tenant tried to set risk limit {tenant_limit} > global {global_limit}. "
                        f"Applying global limit."
                    )
                    validated["autonomy_matrix"][env]["max_risk_level"] = global_limit

        return validated

    def _merge_policies(self, system: AISystem) -> Dict[str, Any]:
        """
        Merge inteligente das 3 camadas de política (Global > Tenant > System)

        Args:
            system: Sistema de IA sendo avaliado

        Returns:
            Política final consolidada

        Strategy:
            Conservative merge - A regra mais RESTRITIVA vence
        """
        # Base: Política Global (Lei)
        final_policy = self.global_policy.copy()

        # Camada 2: Tenant (Empresa)
        tenant_policy = self.registry.get_tenant_policy(
            system.tenant_id,
            system.tenant_id  # Mesmo tenant (sem cross-access)
        )

        if tenant_policy:
            safe_tenant_policy = self._validate_tenant_policy(tenant_policy)
            final_policy = self._conservative_merge(final_policy, safe_tenant_policy)

        # Camada 3: System (Projeto)
        if system.governance_policy:
            final_policy = self._conservative_merge(final_policy, system.governance_policy)

        return final_policy

    def _conservative_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Merge conservador de políticas

        Rules:
        - risk_level: Mantém o MENOR (mais seguro)
        - toggles booleanos: False vence (blocklist approach)

        Args:
            base: Política base
            override: Política sobreposta

        Returns:
            Política mergeada
        """
        merged = base.copy()

        # Merge de Autonomy Matrix (menor risco vence)
        if "autonomy_matrix" in override:
            for env, limits in override["autonomy_matrix"].items():
                if env in merged["autonomy_matrix"]:
                    current_max = merged["autonomy_matrix"][env]["max_risk_level"]
                    new_max = limits.get("max_risk_level", current_max)
                    # Conservador: pega o menor
                    merged["autonomy_matrix"][env]["max_risk_level"] = min(current_max, new_max)

        # Merge de Custom Rules (True vence para blocks)
        if "custom_rules" in override:
            if "custom_rules" not in merged:
                merged["custom_rules"] = {}
            # Para regras de "block_*", True (bloquear) vence
            for key, value in override["custom_rules"].items():
                if key.startswith("block_") and value is True:
                    merged["custom_rules"][key] = True
                elif key not in merged["custom_rules"]:
                    merged["custom_rules"][key] = value

        return merged

    def enforce(self, task: Task, system: AISystem, env: str) -> Dict:
        """
        Executa enforcement de governança em runtime

        Args:
            task: Tarefa sendo executada
            system: Sistema de IA executor
            env: Ambiente (development, staging, production)

        Returns:
            Dict com decisão (ALLOWED/BLOCKED) e metadados

        Compliance:
            ISO 42001 8.2 (AI Risk Assessment - Operation)
            EU AI Act Art. 12 (Logging)
        """
        # 1. Resolver política ativa (merge das 3 camadas)
        active_policy = self._merge_policies(system)

        # 2. Avaliação de risco (3 agentes especializados)
        assessment = self.router.assess_risk(task, system)
        risk = assessment["risk_score"]

        # 3. Consultar memória de compliance (histórico de violações)
        history = self.memory.query_similar(task.title)
        if history:
            risk = min(10.0, risk + 1.0)  # Penaliza se há histórico
            logger.info(f"Historical violations found for similar task. Risk adjusted to {risk}")

        # 4. Determinar limite baseado na política ativa
        limit = active_policy["autonomy_matrix"].get(env, {}).get("max_risk_level", 5.0)

        # Sandbox override (Art. 57 EU AI Act)
        if system.is_sandbox_mode:
            original_limit = limit
            limit += 2.0
            logger.info(
                f"Sandbox mode: limit increased from {original_limit} to {limit}"
            )

        # 5. Decisão final
        decision = "ALLOWED" if risk <= limit else "BLOCKED"
        escalation = (risk > limit)

        # Hash da política (audit trail)
        policy_hash = hashlib.sha256(
            json.dumps(active_policy, sort_keys=True).encode()
        ).hexdigest()

        result = {
            "decision": decision,
            "risk_score": round(risk, 2),
            "limit": limit,
            "active_policy_hash": policy_hash[:8],
            "issues": assessment["issues"],
            "escalation_required": escalation,
            "environment": env,
            "timestamp": datetime.now().isoformat()
        }

        # 6. Log assinado (HMAC - tamper-proof)
        self._log_signed(system.id, task.title, result, active_policy)

        # 7. Se bloqueado, registra violação e escala
        if decision == "BLOCKED":
            self.memory.add_violation(
                task_title=task.title,
                system_id=system.id,
                risk=risk,
                reason="RUNTIME_BLOCK"
            )

            if escalation:
                review_id = self.oversight.create_review_request(
                    decision=result,
                    task={"title": task.title, "description": task.description},
                    system_id=system.id
                )
                result["review_id"] = review_id
                logger.warning(
                    f"Decision escalated to human review: {review_id}"
                )

        return result

    def _log_signed(self, sys_id: str, task: str, res: Dict, policy: Dict):
        """
        Registra decisão no ledger com assinatura HMAC

        Args:
            sys_id: ID do sistema
            task: Título da tarefa
            res: Resultado da decisão
            policy: Política ativa usada

        Security:
            HMAC-SHA256 digital signature (tamper-proof)
            Compliance: ISO 42001 A.7.5 (Data Provenance)
        """
        entry = {
            "system": sys_id,
            "task": task[:200],  # Limita tamanho
            **res
        }

        # Assinatura HMAC (previne adulteração do ledger)
        msg = json.dumps(entry, sort_keys=True).encode()
        entry["signature"] = hmac.new(
            self.hmac_key,
            msg,
            hashlib.sha256
        ).hexdigest()

        # Persiste no ledger (append-only)
        with open(self.ledger, "a") as f:
            f.write(json.dumps(entry) + "\n")
