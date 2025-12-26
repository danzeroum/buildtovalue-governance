"""
Adaptive Risk Router com 3 Agentes Especializados

Implementa:
- ISO 42001 6.1.2 (AI Risk Assessment)
- EU AI Act Art. 9 (Risk Management System)
- Multi-dimensional risk scoring (technical, regulatory, ethical)
"""

import logging
from typing import Dict, List

from src.domain.entities import Task, AISystem
from src.domain.enums import EUComplianceRisk, AISector

logger = logging.getLogger("btv.router")


class AdaptiveRiskRouter:
    """
    Router Adaptativo de Risco com Agentes Especializados

    Arquitetura Multi-Agent:
    1. Technical Agent - Avalia complexidade técnica (FLOPs, logging)
    2. Regulatory Agent - Verifica conformidade (EU AI Act, ISO 42001)
    3. Ethical Agent - Analisa impacto societal (transparência, fairness)

    Risk Score: 0-10 (weighted average)
    """

    def __init__(self):
        """Inicializa router com pesos dos agentes"""
        self.risk_weights = {
            "technical": 0.3,
            "regulatory": 0.4,  # Maior peso (compliance crítica)
            "ethical": 0.3
        }

        # Keywords suspeitas para análise ética
        self.suspicious_keywords = [
            "discriminar", "manipular", "enganar", "social scoring",
            "subliminar", "vulnerabilidade", "criança", "emoção",
            "manipulação", "exploração", "preconceito", "viés",
            # English
            "discriminate", "manipulate", "deceive", "exploit",
            "bias", "prejudice", "vulnerability", "children"
        ]

    def assess_risk(self, task: Task, system: AISystem) -> Dict:
        """
        Avalia risco agregado da tarefa usando 3 agentes

        Args:
            task: Tarefa sendo executada
            system: Sistema de IA executor

        Returns:
            Dict com risk_score (0-10) e issues detectadas

        Compliance:
            ISO 42001 6.1.2 (AI Risk Assessment)
        """
        issues = []
        scores = {}

        # Agente 1: Análise Técnica
        scores["technical"] = self._assess_technical_risk(task, system, issues)

        # Agente 2: Análise Regulatória (EU AI Act + ISO 42001)
        scores["regulatory"] = self._assess_regulatory_risk(task, system, issues)

        # Agente 3: Análise Ética (Art. 69 EU AI Act)
        scores["ethical"] = self._assess_ethical_risk(task, system, issues)

        # Score agregado (ponderado)
        risk_score = sum(
            scores[agent] * self.risk_weights[agent]
            for agent in scores
        )

        # Penalização por histórico (se houver flags)
        if system.high_risk_flags:
            penalty = min(2.0, len(system.high_risk_flags) * 0.5)
            risk_score += penalty
            issues.append(
                f"⚠️ Sistema possui {len(system.high_risk_flags)} flags de alto risco"
            )

        logger.info(
            f"Risk assessed: {risk_score:.2f} | "
            f"Technical: {scores['technical']:.2f} | "
            f"Regulatory: {scores['regulatory']:.2f} | "
            f"Ethical: {scores['ethical']:.2f}"
        )

        return {
            "risk_score": min(10.0, risk_score),
            "breakdown": scores,
            "issues": issues
        }

    def _assess_technical_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agente 1: Avalia risco técnico

        Fatores:
        - FLOPs de treinamento (Art. 51 EU AI Act)
        - Capacidades de logging (Art. 12 EU AI Act)
        - Complexidade da tarefa

        Returns:
            Risk score (0-10)
        """
        risk = 2.0  # Base risk

        # FLOPs altíssimos = maior risco (GPAI Sistêmico)
        if system.training_compute_flops:
            if system.training_compute_flops > 1e25:
                risk += 3.0
                issues.append(
                    "🔴 Sistema GPAI sistêmico (FLOPs > 10^25) - Art. 51 EU AI Act"
                )
            elif system.training_compute_flops > 1e24:
                risk += 2.0
                issues.append(
                    "🟡 Sistema GPAI de alto compute (FLOPs > 10^24)"
                )

        # Sem logging = maior risco (Art. 12 ISO 42001)
        if not system.logging_capabilities:
            risk += 1.5
            issues.append(
                "⚠️ Sistema sem capacidade de logging - Violação Art. 12 ISO 42001"
            )

        # Tamanho da tarefa (proxy de complexidade)
        task_length = len(task.title) + len(task.description)
        if task_length > 1000:
            risk += 0.5
            issues.append("📝 Tarefa complexa detectada (> 1000 chars)")

        return min(10.0, risk)

    def _assess_regulatory_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agente 2: Avalia conformidade regulatória

        Checks:
        - Setor de aplicação (Anexo III EU AI Act)
        - Classificação de risco (Art. 6)
        - Jurisdição (GDPR Art. 44-50)
        - Registro EU Database (Art. 71)

        Returns:
            Risk score (0-10)
        """
        risk = 1.0  # Base risk

        # Mapeamento setor -> risco base
        high_risk_sectors = [
            AISector.BIOMETRIC,
            AISector.LAW_ENFORCEMENT,
            AISector.JUSTICE,
            AISector.CRITICAL_INFRASTRUCTURE,
            AISector.EMPLOYMENT,
            AISector.EDUCATION
        ]

        if system.sector in high_risk_sectors:
            risk += 4.0
            issues.append(
                f"🔴 Setor de ALTO RISCO: {system.sector.value} (Anexo III EU AI Act)"
            )

        # Classificação de risco do sistema
        if system.risk_classification == EUComplianceRisk.UNACCEPTABLE:
            risk = 10.0
            issues.append(
                "🚨 PRÁTICA PROIBIDA detectada - Art. 5 EU AI Act - BLOQUEIO IMEDIATO"
            )
        elif system.risk_classification == EUComplianceRisk.HIGH:
            risk += 3.0
            issues.append(
                "🔴 Sistema classificado como ALTO RISCO (Art. 6 EU AI Act)"
            )
        elif system.risk_classification == EUComplianceRisk.SYSTEMIC_GPAI:
            risk += 3.5
            issues.append(
                "🔴 Sistema GPAI com risco sistêmico (Art. 51 EU AI Act)"
            )

        # Jurisdição não-EU = mais risco (GDPR Art. 44-50)
        if system.jurisdiction != "EU":
            risk += 1.0
            issues.append(
                f"⚠️ Sistema em jurisdição não-EU: {system.jurisdiction} "
                f"(GDPR Art. 44 - Transferências Internacionais)"
            )

        # Alto risco sem registro EU = violação
        if (system.risk_classification == EUComplianceRisk.HIGH and
                not system.eu_database_registration_id):
            risk += 2.0
            issues.append(
                "🔴 Sistema de alto risco SEM registro na EU Database (Art. 71)"
            )

        return min(10.0, risk)

    def _assess_ethical_risk(
            self,
            task: Task,
            system: AISystem,
            issues: List[str]
    ) -> float:
        """
        Agente 3: Avalia risco ético e societal

        Checks:
        - Keywords suspeitas no prompt
        - Transparência (registro EU)
        - Explicabilidade

        Returns:
            Risk score (0-10)
        """
        risk = 1.0  # Base risk

        # Análise de keywords suspeitas
        task_lower = (task.title + " " + task.description).lower()
        detected_keywords = []

        for keyword in self.suspicious_keywords:
            if keyword in task_lower:
                detected_keywords.append(keyword)

        if detected_keywords:
            risk += min(3.0, len(detected_keywords) * 1.5)
            issues.append(
                f"⚠️ Termos suspeitos detectados no prompt: {', '.join(detected_keywords[:3])} "
                f"(Possível violação Art. 5 EU AI Act)"
            )

        # Sistema sem ID da EU Database = menos transparência
        if not system.eu_database_registration_id and system.risk_classification != EUComplianceRisk.MINIMAL:
            risk += 1.0
            issues.append(
                "⚠️ Sistema não registrado na EU Database (Art. 71) - "
                "Reduz transparência"
            )

        # Setores sensíveis (crianças, vulneráveis)
        if system.sector in [AISector.EDUCATION, AISector.HEALTHCARE]:
            risk += 0.5
            issues.append(
                f"ℹ️ Setor sensível: {system.sector.value} - "
                f"Requer atenção especial a vulnerabilidades"
            )

        return min(10.0, risk)
