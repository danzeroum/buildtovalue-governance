# BuildToValue Framework - Visão Geral da Arquitetura

**Versão**: v0.9.0  
**Última Atualização**: 28 de dezembro de 2025  
**Status**: Pronto para Produção

---

## 🎯 Resumo Executivo

BuildToValue Framework implementa uma **arquitetura em camadas** inspirada em princípios de Domain-Driven Design (DDD), permitindo enforcement em runtime de políticas de governança de IA com auditabilidade criptográfica.

**Inovação Principal**: **Kill Switch de Prioridade Zero** - primeira implementação open-source do NIST AI RMF MANAGE-2.4 em nível arquitetural.

---

## 📊 Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICAÇÕES CLIENTE                           │
│  SDK Python  │  REST API  │  CLI  │  Sistemas Terceiros        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTPS/TLS 1.3
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     CAMADA DE API GATEWAY                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Gateway FastAPI (src/interface/api/gateway.py)        │     │
│  │ -  Autenticação JWT (RS256)                            │     │
│  │ -  Autorização RBAC (admin/dev/auditor/app)            │     │
│  │ -  Limitação de Taxa (100 req/min padrão)              │     │
│  │ -  Documentação OpenAPI (/docs)                        │     │
│  │ -  Exception Handlers (respostas de erro JSON)         │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼─────────┐                  ┌────────▼────────┐
│  POST /v1/enforce│                  │ PUT /emergency-stop│
│  (Fluxo Normal)  │                  │ (Kill Switch)   │
└───────┬─────────┘                  └────────┬────────┘
        │                                     │
        │                            ┌────────▼────────┐
        │                            │ Atualizar BD:   │
        │                            │ operational_    │
        │                            │ status =        │
        │                            │ "emergency_stop"│
        │                            └────────┬────────┘
        │                                     │
        │                            ┌────────▼────────┐
        │                            │ Log Auditoria   │
        │                            │ Assinado HMAC   │
        │                            └─────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│           PRIORIDADE ZERO: VERIFICAÇÃO KILL SWITCH               │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ if system.operational_status == "emergency_stop":     │       │
│  │     return Decision(                                  │       │
│  │         outcome="BLOCKED",                            │       │
│  │         risk_score=10.0,                              │       │
│  │         reason="KILL_SWITCH_ACTIVE"                   │       │
│  │     )                                                 │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  Conformidade: NIST MANAGE-2.4, EU AI Act Art. 14               │
└───────┬──────────────────────────────────────────────────────────┘
        │
        │ SE active, continuar...
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                  CAMADA DE INTELIGÊNCIA                          │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Roteador de Risco Adaptativo (3 Agentes)            │       │
│  │ src/intelligence/routing/adaptive_router.py          │       │
│  │                                                       │       │
│  │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │       │
│  │ │Agente Técnico│ │Agente        │ │Agente Ético  │ │       │
│  │ │              │ │Regulatório   │ │              │ │       │
│  │ │-  FLOPs       │ │-  Setor       │ │-  Palavras-   │ │       │
│  │ │-  Logging     │ │-  EU AI Act   │ │  chave       │ │       │
│  │ │-  Complexidade│ │-  ISO 42001   │ │-  Justiça     │ │       │
│  │ │              │ │-  NIST        │ │-  Transparência│ │      │
│  │ │Peso: 30%     │ │Peso: 40%     │ │Peso: 30%     │ │       │
│  │ └──────────────┘ └──────────────┘ └──────────────┘ │       │
│  │                                                       │       │
│  │ Saída: Pontuação de Risco Ponderada (0-10)          │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Taxonomia de Ameaças Huwyler (2024)                 │       │
│  │ src/intelligence/threats/huwyler_taxonomy.py         │       │
│  │                                                       │       │
│  │ -  133 incidentes de segurança de IA analisados      │       │
│  │ -  Detecção de domínio MISUSE (prompt injection)     │       │
│  │ -  Classificação de ameaças em tempo real             │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ RAG de Memória de Conformidade                       │       │
│  │ src/intelligence/memory/compliance_rag.py            │       │
│  │                                                       │       │
│  │ -  Rastreamento histórico de violações                │       │
│  │ -  Aprendizado de padrões (pontuação adaptativa)      │       │
│  │ -  Recuperação de incidentes similares                │       │
│  └──────────────────────────────────────────────────────┘       │
└───────┬──────────────────────────────────────────────────────────┘
        │
        │ risk_score, detected_threats, confidence
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                  MOTOR DE ENFORCEMENT                            │
│  src/core/governance/enforcement.py                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Merge de Políticas (Estratégia Conservadora)        │       │
│  │ -  Política Global (base)                             │       │
│  │ -  Política de Tenant (sobrescreve)                   │       │
│  │ -  Política de Sistema (mais específica)              │       │
│  │                                                       │       │
│  │ Regra: Mais restritiva vence                         │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Lógica de Decisão                                    │       │
│  │                                                       │       │
│  │ SE risk_score >= environment_threshold:              │       │
│  │     outcome = "BLOCKED"                              │       │
│  │ SENÃO SE risk_score >= escalation_threshold:         │       │
│  │     outcome = "ESCALATED"                            │       │
│  │     create_human_review_request()                    │       │
│  │ SENÃO:                                               │       │
│  │     outcome = "APPROVED"                             │       │
│  │                                                       │       │
│  │ Limiares de Ambiente (governance.yaml):              │       │
│  │ -  development: 8.0                                   │       │
│  │ -  staging: 6.0                                       │       │
│  │ -  production: 4.0                                    │       │
│  └──────────────────────────────────────────────────────┘       │
└───────┬──────────────────────────────────────────────────────────┘
        │
        │ Objeto Decision
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                  CAMADA DE AUDITORIA & LOGGING                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Ledger Assinado HMAC (À Prova de Adulteração)       │       │
│  │ logs/enforcement_ledger.jsonl                        │       │
│  │                                                       │       │
│  │ {                                                     │       │
│  │   "timestamp": "2025-12-28T22:15:30Z",               │       │
│  │   "system_id": "analise-credito-v2",                 │       │
│  │   "decision": "BLOCKED",                             │       │
│  │   "risk_score": 8.5,                                 │       │
│  │   "tenant_id": "banco-uuid",                         │       │
│  │   "signature": "a3f2c1d4e5f6..."  ← HMAC-SHA256     │       │
│  │ }                                                     │       │
│  │                                                       │       │
│  │ Retenção: 5 anos (EU AI Act Art. 12)                │       │
│  │ Validação: scripts/validate_ledger.py                │       │
│  └──────────────────────────────────────────────────────┘       │
└───────┬──────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                  CAMADA DE PERSISTÊNCIA                          │
│                                                                  │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │ BD PostgreSQL      │  │ Registro de Sistema│                │
│  │ (Produção)         │  │ src/domain/        │                │
│  │                    │  │ registry.py        │                │
│  │ Tabelas:           │  │                    │                │
│  │ -  ai_systems       │  │ -  Operações CRUD   │                │
│  │ -  tenants          │  │ -  Isolamento tenant│                │
│  │ -  policies         │  │ -  Validação        │                │
│  │ -  audit_trail      │  │                    │                │
│  └────────────────────┘  └────────────────────┘                │
│                                                                  │
│  Isolamento Multi-Tenant:                                       │
│  -  Índices compostos: (tenant_id, system_id)                   │
│  -  Segurança em nível de linha (RLS)                            │
│  -  Validação de claim JWT                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔥 Arquitetura do Kill Switch (NOVO v0.9.0)

### Princípios de Design

1. **Prioridade Zero**: Verificação do kill switch acontece ANTES de qualquer avaliação de risco
2. **Persistência em Banco de Dados**: Status sobrevive a reinicializações
3. **Auditoria Criptográfica**: Evento de ativação assinado com HMAC
4. **Apenas Admin**: Requer papel `admin` no token JWT
5. **Irreversível Sem Aprovação Humana**: Não pode ser desfeito programaticamente

### Diagrama de Sequência

```
┌──────────┐          ┌─────────────┐          ┌──────────┐          ┌──────────┐
│ Operador │          │ API Gateway │          │ Registry │          │ Banco de │
│ Admin    │          │             │          │          │          │ Dados    │
└────┬─────┘          └──────┬──────┘          └────┬─────┘          └────┬─────┘
     │                       │                      │                     │
     │ PUT /emergency-stop   │                      │                     │
     ├──────────────────────►│                      │                     │
     │                       │                      │                     │
     │                       │ Validar JWT          │                     │
     │                       │ (require role=admin) │                     │
     │                       │                      │                     │
     │                       │ get_system()         │                     │
     │                       ├─────────────────────►│                     │
     │                       │                      │                     │
     │                       │                      │ SELECT * FROM       │
     │                       │                      │ ai_systems WHERE... │
     │                       │                      ├────────────────────►│
     │                       │                      │                     │
     │                       │                      │◄────────────────────┤
     │                       │                      │ dados do sistema    │
     │                       │◄─────────────────────┤                     │
     │                       │                      │                     │
     │                       │ update_operational_  │                     │
     │                       │ status()             │                     │
     │                       ├─────────────────────►│                     │
     │                       │                      │                     │
     │                       │                      │ UPDATE ai_systems   │
     │                       │                      │ SET operational_    │
     │                       │                      │ status='emergency_  │
     │                       │                      │ stop' WHERE...      │
     │                       │                      ├────────────────────►│
     │                       │                      │                     │
     │                       │                      │◄────────────────────┤
     │                       │                      │ commit              │
     │                       │◄─────────────────────┤                     │
     │                       │                      │                     │
     │                       │ log_signed()         │                     │
     │                       │ (entrada HMAC)       │                     │
     │                       │                      │                     │
     │◄──────────────────────┤                      │                     │
     │ 200 OK                │                      │                     │
     │ {acknowledged: true}  │                      │                     │
     │                       │                      │                     │
     │                                                                    │
     │ [REQUISIÇÕES SUBSEQUENTES]                                         │
     │                       │                      │                     │
     │ POST /v1/enforce      │                      │                     │
     ├──────────────────────►│                      │                     │
     │                       │                      │                     │
     │                       │ get_system()         │                     │
     │                       ├─────────────────────►│                     │
     │                       │                      │                     │
     │                       │                      │ SELECT * (status=   │
     │                       │                      │ 'emergency_stop')   │
     │                       │                      ├────────────────────►│
     │                       │                      │◄────────────────────┤
     │                       │◄─────────────────────┤                     │
     │                       │                      │                     │
     │                       │ VERIFICAÇÃO PRIORIDADE ZERO:│              │
     │                       │ SE emergency_stop    │                     │
     │                       │ RETORNAR BLOCKED     │                     │
     │◄──────────────────────┤                      │                     │
     │ {outcome: "BLOCKED",  │                      │                     │
     │  reason: "KILL_SWITCH_│                      │                     │
     │  ACTIVE"}             │                      │                     │
     │                       │                      │                     │
```

### Transições de Estado

```
┌───────────────────────────────────────────────────────────────┐
│                  Estados de Status Operacional                │
└───────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │ DESIGN  │ (inicial)
    └────┬────┘
         │ register_system()
         ▼
    ┌─────────┐
    │ ACTIVE  │ ◄───────────────────┐
    └────┬────┘                      │
         │                           │ resume_operations()
         │                           │ (aprovação admin)
         │                           │
         ├──► DEGRADED ──────────────┤
         │   (problemas desempenho)  │
         │                           │
         ├──► MAINTENANCE ───────────┤
         │   (downtime planejado)    │
         │                           │
         ├──► SUSPENDED ─────────────┤
         │   (violação política)     │
         │                           │
         │                           │
         │ emergency_stop()          │
         │ (apenas admin)            │
         ▼                           │
    ┌──────────────┐                │
    │ EMERGENCY_   │                │
    │ STOP         │────────────────┘
    └──────────────┘
         │
         │ (ESTADO TERMINAL até aprovação humana)
         │
```

---

## 🏗️ Detalhes das Camadas

### 1. Camada de Domínio (Lógica de Negócio Principal)

**Localização**: `src/domain/`

**Componentes**:
- `entities.py` - Modelos de domínio principais (AISystem, Task, Decision, Policy)
- `enums.py` - Enumerações type-safe (AISector, AIPhase, OperationalStatus)
- `registry.py` - Gestão do ciclo de vida do sistema

**Entidades Principais**:

```
# AISystem (Raiz Agregada)
class AISystem(BaseModel):
    id: str
    tenant_id: str  # Isolamento multi-tenant
    operational_status: OperationalStatus  # Estado do kill switch
    lifecycle_phase: AIPhase  # NIST MAP-1.1
    risk_classification: Literal["minimal", "limited", "high", "unacceptable"]
    sector: AISector  # EU AI Act Anexo III
    eu_database_registration_id: Optional[str]  # Art. 71
    external_dependencies: List[ThirdPartyComponent]  # NIST GOVERN-6.1
    training_flops: Optional[float]  # Limiar Art. 51
```

**Mapeamento de Conformidade**:
- ISO 42001 Cláusula 7.2 (Gestão de Ativos)
- EU AI Act Art. 6 (Classificação)
- NIST AI RMF MAP-1.1 (Ciclo de Vida)

---

### 2. Camada de Inteligência (Avaliação de Riscos)

**Localização**: `src/intelligence/`

#### Roteador de Risco Adaptativo
**Arquivo**: `routing/adaptive_router.py`

**Arquitetura**: Sistema multi-agente com pontuação ponderada

```
def assess_risk(task, system):
    # Agente 1: Risco Técnico (30%)
    technical_score = evaluate_flops(system) + \
                     evaluate_logging(system) + \
                     evaluate_complexity(system)
    
    # Agente 2: Risco Regulatório (40%)
    regulatory_score = check_sector(system) + \
                      check_eu_registration(system) + \
                      check_prohibited_practices(task)
    
    # Agente 3: Risco Ético (30%)
    ethical_score = keyword_analysis(task) + \
                   transparency_check(system) + \
                   rights_impact_assessment(task)
    
    # Média ponderada
    final_score = (technical_score * 0.3) + \
                  (regulatory_score * 0.4) + \
                  (ethical_score * 0.3)
    
    return min(final_score, 10.0)
```

**Por que 40% de peso no Agente Regulatório?**  
Violações regulatórias carregam as maiores penalidades financeiras (€15M-€35M sob EU AI Act Art. 99).

---

#### Taxonomia de Ameaças Huwyler
**Arquivo**: `threats/huwyler_taxonomy.py`

**Integração**: Classificação de ameaças em tempo real baseada em 133 incidentes analisados.

```
# Exemplo: Detecção de Prompt Injection
MISUSE_PATTERNS = [
    "ignore previous instructions",
    "disregard system prompt",
    "jailbreak",
    "DAN mode"
]

if any(pattern in task.prompt.lower() for pattern in MISUSE_PATTERNS):
    detected_threats.append("PROMPT_INJECTION")
    risk_score += 5.0
```

**Referência**: Huwyler, H. (2024). *Taxonomia Padronizada de Ameaças para Segurança de IA*. [arXiv:2511.21901](https://arxiv.org/abs/2511.21901)

---

### 3. Motor de Enforcement (Lógica de Decisão)

**Localização**: `src/core/governance/enforcement.py`

**Método Principal**:

```
def enforce(self, task: Task, system: AISystem, env: str) -> Decision:
    """
    Enforcement em runtime com verificação de prioridade zero do kill switch.
    
    Args:
        task: Tarefa de IA a avaliar
        system: Metadados do sistema de IA
        env: Ambiente alvo (development/staging/production)
    
    Returns:
        Objeto Decision (APPROVED/BLOCKED/ESCALATED)
    
    Conformidade:
        - NIST AI RMF MANAGE-2.4 (Parada de Emergência)
        - EU AI Act Art. 14 (Supervisão Humana)
        - ISO 42001 Cláusula 8.32 (Controle Operacional)
    """
    
    # PASSO 1: Prioridade Zero - Verificação Kill Switch
    if system.operational_status == OperationalStatus.EMERGENCY_STOP:
        return self._create_kill_switch_decision()
    
    # PASSO 2: Merge de Políticas (Conservador)
    active_policy = self._merge_policies(system.tenant_id, system.id)
    
    # PASSO 3: Avaliar Risco (Sistema de 3 Agentes)
    risk_score, threats, confidence = self.router.assess_risk(task, system)
    
    # PASSO 4: Aplicar Limiares de Ambiente
    threshold = active_policy.autonomy_matrix[env]["max_risk_level"]
    
    if risk_score >= threshold:
        outcome = "BLOCKED"
    elif risk_score >= active_policy.escalation_threshold:
        outcome = "ESCALATED"
        self.oversight.create_review_request(system.id, risk_score)
    else:
        outcome = "APPROVED"
    
    # PASSO 5: Gerar Decisão
    decision = Decision(
        outcome=outcome,
        risk_score=risk_score,
        detected_threats=threats,
        confidence=confidence,
        active_policy_hash=active_policy.hash()
    )
    
    # PASSO 6: Log com Assinatura HMAC
    self.log_signed(system.id, task, decision, active_policy)
    
    return decision
```

---

### 4. API Gateway (Camada de Interface)

**Localização**: `src/interface/api/gateway.py`

**Tecnologia**: FastAPI 0.104+

**Funcionalidades de Segurança**:
- Autenticação JWT (algoritmo RS256)
- RBAC com 4 papéis: `admin`, `dev`, `auditor`, `app`
- Limitação de taxa (100 req/min padrão, configurável)
- Políticas CORS
- Exception handlers (erros JSON consistentes)

**Endpoints Principais**:

```
# Enforcement normal
POST /v1/enforce
Headers:
  Authorization: Bearer <JWT>
  Content-Type: application/json
Body:
  {
    "system_id": "analise-credito-v2",
    "prompt": "Avaliar solicitação de empréstimo",
    "env": "production"  # OBRIGATÓRIO v0.9.0
  }

# Ativação do kill switch
PUT /v1/systems/{system_id}/emergency-stop
Headers:
  Authorization: Bearer <ADMIN_JWT>
Body:
  {
    "operational_status": "emergency_stop",
    "reason": "Viés detectado em produção",
    "operator_id": "admin@empresa.com"
  }

# Registro de sistema
POST /v1/systems
Headers:
  Authorization: Bearer <DEV_JWT>
Body:
  {
    "id": "chatbot-v1",
    "sector": "general_commercial",
    "risk": "minimal"
  }
```

---

### 5. Camada de Persistência

**Banco de Dados**: PostgreSQL 14+ (produção) | SQLite 3.35+ (desenvolvimento)

**Design do Schema**:

```
-- Tabela AI Systems
CREATE TABLE ai_systems (
    id VARCHAR(255) PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    operational_status VARCHAR(50) NOT NULL DEFAULT 'active',
    lifecycle_phase VARCHAR(50) NOT NULL DEFAULT 'deployment',
    risk_classification VARCHAR(50),
    sector VARCHAR(100),
    eu_database_registration_id VARCHAR(255),
    training_flops BIGINT,
    external_dependencies JSONB,
    human_ai_configuration JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Isolamento multi-tenant
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) 
        REFERENCES tenants(id) ON DELETE CASCADE
);

-- Índice composto para desempenho
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);
CREATE INDEX idx_operational_status ON ai_systems(operational_status);
```

**Isolamento Multi-Tenant**:
- Row-Level Security (RLS) imposta em nível de banco de dados
- Claim `tenant_id` do JWT validado em cada query
- Índices compostos previnem vazamento de dados cross-tenant

---

## 🔐 Arquitetura de Segurança

### Modelo de Segurança Multi-Tenant

```
┌─────────────────────────────────────────────────────────┐
│                  Tenant A (Banco)                       │
│  ┌──────────────────────────────────────────────┐      │
│  │ Sistemas: analise-credito-v1, deteccao-fraude│      │
│  │ Política: max_risk_level = 2.0 (production)   │      │
│  │ JWT: tenant_id = "banco-uuid"                 │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Tenant B (Startup)                     │
│  ┌──────────────────────────────────────────────┐      │
│  │ Sistemas: chatbot-v2, gerador-conteudo       │      │
│  │ Política: max_risk_level = 7.0 (production)   │      │
│  │ JWT: tenant_id = "startup-uuid"               │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘

         ISOLAMENTO IMPOSTO EM:
         1. Validação JWT (API Gateway)
         2. Queries de Banco de Dados (Row-Level Security)
         3. Merge de Políticas (Configs Específicas de Tenant)
```

**Prevenção OWASP API1:2023 (BOLA)**:
```
# Arquivo: src/domain/registry.py (linhas 45-58)
def get_system(self, system_id: str, requesting_tenant: str) -> AISystem:
    """Buscar sistema com validação de tenant (prevenção BOLA)"""
    system = db.query(AISystem).filter(
        AISystem.id == system_id,
        AISystem.tenant_id == requesting_tenant  # ← Verificação crítica
    ).first()
    
    if not system:
        raise SystemNotFoundError(
            f"Sistema {system_id} não encontrado para tenant {requesting_tenant}"
        )
    
    return system
```

---

### Trilha de Auditoria Assinada com HMAC

**Algoritmo**: HMAC-SHA256  
**Gestão de Chaves**: Variável de ambiente `HMAC_SECRET_KEY` (rotacionada a cada 90 dias)

**Estrutura de Entrada**:
```
{
  "timestamp": "2025-12-28T22:15:30.123456Z",
  "event_type": "ENFORCEMENT_DECISION",
  "system_id": "analise-credito-v2",
  "tenant_id": "banco-uuid",
  "task_hash": "sha256:a1b2c3d4...",
  "decision": "BLOCKED",
  "risk_score": 8.5,
  "detected_threats": ["HIGH_RISK_SECTOR", "INSUFFICIENT_LOGGING"],
  "policy_hash": "sha256:e5f6g7h8...",
  "signature": "hmac-sha256:1a2b3c4d5e6f7g8h9i0j..."
}
```

**Validação**:
```
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

# Saída:
# ✅ INTEGRIDADE DO LEDGER VERIFICADA
# Escaneadas: 15.432 entradas
# Assinaturas válidas: 15.432 (100%)
# Assinaturas inválidas: 0
# Intervalo de datas: 2024-01-01 a 2025-12-28
```

---

## 📈 Características de Desempenho

### Benchmarks de Latência (P95)

| Operação | Meta | Real | Observações |
|:----------|:-------|:-------|:------|
| Ativação Kill Switch | <100ms | 8ms | Escrita BD + assinatura HMAC |
| Verificação Kill Switch | <1ms | 0.3ms | Lookup em memória de status operacional |
| Avaliação de Risco (3 agentes) | <10ms | 4ms | Execução paralela de agentes |
| Merge de Políticas | <5ms | 1.2ms | Algoritmo de merge conservador |
| Decisão de Enforcement | <20ms | 6ms | End-to-end (verificar → avaliar → decidir) |
| Geração Assinatura HMAC | <5ms | 2ms | Hashing SHA256 |
| Query BD (isolamento tenant) | <10ms | 3ms | Otimização de índice composto |

**Ambiente de Teste**: AWS EC2 t3.medium (2 vCPU, 4GB RAM), PostgreSQL 14, Python 3.10

---

### Escalabilidade

**Escalabilidade Horizontal**:
- API gateway stateless (escala linearmente)
- Réplicas de leitura do banco de dados para queries de enforcement
- Cache Redis para configurações de políticas

**Escalabilidade Vertical**:
- Sistema de 3 agentes paralelizável (suporte asyncio)
- Motor de enforcement otimizado para decisões <1ms

**Resultados de Teste de Carga** (v0.9.0):
- **1.000 req/seg**: Latência P95 = 12ms
- **5.000 req/seg**: Latência P95 = 35ms
- **10.000 req/seg**: Latência P95 = 78ms (aceitável)

---

## 🎓 Padrões de Design

### 1. Aggregate Root (DDD)
**AISystem** é a raiz agregada encapsulando:
- Status operacional (estado do kill switch)
- Fase do ciclo de vida
- Classificação de risco
- Metadados de conformidade

---

### 2. Padrão Strategy
**Roteador de Risco Adaptativo** usa padrão strategy para seleção de agente:
```
class RiskAgent(ABC):
    @abstractmethod
    def assess(self, task, system) -> float:
        pass

class TechnicalAgent(RiskAgent): ...
class RegulatoryAgent(RiskAgent): ...
class EthicalAgent(RiskAgent): ...
```

---

### 3. Chain of Responsibility
**Motor de Enforcement** implementa chain of responsibility:
1. Verificação Kill Switch
2. Merge de Políticas
3. Avaliação de Risco
4. Comparação de Limiares
5. Escalação para Supervisão Humana

---

### 4. Ledger Imutável
**Trilha de Auditoria** usa padrão de log append-only:
- Sem atualizações ou exclusões
- Assinaturas HMAC previnem adulteração
- Valida todo histórico criptograficamente

---

## 📖 Documentação Relacionada

- [Design de Segurança Multi-Tenant](./MULTI_TENANT_DESIGN.md)
- [Compatibilidade NIST AI RMF](../compliance/NIST_AI_RMF_COMPATIBILITY.md)
- [Conformidade EU AI Act](../compliance/EU_AI_ACT_COMPLIANCE.md)
- [Referência da API](../API_REFERENCE.md)

---

**Versão do Documento**: 2.0  
**Última Atualização**: 28 de dezembro de 2025  
**Status**: Validado para v0.9.0 Golden Candidate
