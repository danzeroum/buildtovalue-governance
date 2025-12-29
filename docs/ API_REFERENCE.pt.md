# BuildToValue Framework v0.9.0 - API Reference

**Base URL (Production)**: `https://api.buildtovalue.ai`  
**Base URL (Local)**: `http://localhost:8000`  
**Last Updated**: December 28, 2025

---

## 🔐 Authentication

All endpoints except `/health` require JWT authentication.

### JWT Bearer Token

Authorization: Bearer <JWT_TOKEN>


**Generate Token:**
python scripts/generate_token.py --role admin --tenant <TENANT_UUID> --days 30


**Token Claims:**
- `tenant_id`: Multi-tenant isolation (required)
- `user_id`: User identifier
- `role`: RBAC role (`admin`, `dev`, `auditor`, `app`)
- `exp`: Expiration timestamp (default: 30 minutes)

---

## 📡 Endpoints

### Health Check

#### `GET /health`

Verify service status (no authentication required).

**Response 200:**
{
"status": "healthy",
"version": "0.9.0",
"security": "hardened",
"features": {
"kill_switch": true,
"compliance_reports": true,
"threat_classification": true
}
}


---

### Admin Endpoints

#### `POST /v1/tenants`

Register or update tenant (Layer 2 - Organization).

**Auth**: `admin` role required  
**Rate Limit**: 10 req/min

**Request Body:**
{
"id": "550e8400-e29b-41d4-a716-446655440000",
"name": "Secure Bank Inc.",
"policy": {
"autonomy_matrix": {
"production": {
"max_risk_level": 2.0
}
},
"custom_rules": {
"block_public_apis_in_prod": true
}
}
}


**Response 201:**
{
"status": "registered",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "Tenant 'Secure Bank Inc.' registered successfully"
}


**Errors:**
- `401 Unauthorized`: Invalid/expired token
- `403 Forbidden`: Insufficient role
- `400 Bad Request`: Invalid UUID format

---

### Developer Endpoints

#### `POST /v1/systems`

Register AI system (Layer 3 - Project).

**Auth**: `admin` or `dev` role  
**Rate Limit**: 50 req/min

**Request Body:**
{
"id": "credit-scoring-v2",
"name": "Credit Risk Scoring AI",
"version": "2.1.0",
"sector": "banking",
"role": "deployer",
"risk": "high",
"sandbox": false,
"eu_database_id": "EU-DB-12345",
"training_flops": 1e24,
"logging_enabled": true,
"jurisdiction": "EU",
"intended_purpose": "Assess credit risk for loan applications",
"prohibited_domains": ["social_scoring", "political_profiling"],
"lifecycle_phase": "deployment",
"operational_status": "active"
}


**Response 201:**
{
"status": "registered",
"system_id": "credit-scoring-v2",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "System 'Credit Risk Scoring AI' registered successfully",
"compliance_summary": {
"lifecycle_phase": "deployment",
"operational_status": "active",
"requires_human_oversight": true,
"nist_alignment": "70%"
}
}


---

#### `GET /v1/systems/{system_id}`

Retrieve AI system details.

**Auth**: `admin`, `dev`, or `auditor`

**Response 200:**
{
"id": "credit-scoring-v2",
"name": "Credit Risk Scoring AI",
"version": "2.1.0",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"sector": "banking",
"role": "deployer",
"risk_classification": "high",
"operational_status": "active",
"lifecycle_phase": "deployment",
"logging_enabled": true
}


---

#### `GET /v1/systems`

List all systems for the requesting tenant.

**Auth**: `admin`, `dev`, or `auditor`  
**Query Params**: `limit` (int, default: 100)

**Response 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"count": 2,
"systems": [
{
"id": "credit-scoring-v2",
"name": "Credit Risk Scoring AI",
"version": "2.1.0",
"sector": "banking",
"risk": "high",
"operational_status": "active"
}
]
}


---

### Enforcement Endpoint

#### `POST /v1/enforce`

Execute governance enforcement at runtime.

**Auth**: `admin`, `dev`, or `app` role  
**Rate Limit**: 100 req/min

**✅ UPDATED v0.9.0**: `env` parameter is now **REQUIRED**

**Request Body:**
{
"system_id": "credit-scoring-v2",
"prompt": "Assess credit risk for customer ID 12345",
"env": "production",
"artifact_type": "code"
}


**Response 200 (APPROVED):**
{
"outcome": "APPROVED",
"risk_score": 4.2,
"reason": "Approved: Low risk (4.2/10.0). Standard monitoring applies.",
"detected_threats": [],
"confidence": 0.15,
"recommendations": [
"📈 Enable continuous monitoring for drift and quality degradation"
],
"controls_applied": [],
"baseline_risk": 4.2,
"regulatory_impact": null
}


**Response 200 (BLOCKED):**
{
"outcome": "BLOCKED",
"risk_score": 10.0,
"reason": "BLOCKED: Critical risk score (10.0/10.0) for prompt_injection. Immediate review required.",
"detected_threats": ["MISUSE"],
"confidence": 0.95,
"recommendations": [
"🚨 URGENT: Engage Legal Dept for regulatory compliance review",
"📋 Document decision in compliance ledger (ISO 42001 Clause 9.1)",
"🛡️ Implement robust input validation and output monitoring"
],
"controls_applied": [],
"baseline_risk": 10.0,
"sub_threat_type": "prompt_injection",
"regulatory_impact": {
"executive_summary": "🚨 CRITICAL: 1 prohibited practice(s) detected. EU regulatory exposure: €15,000,000 - €35,000,000.",
"applicable_regulations": [
{
"penalty_id": "eu_ai_act_prohibited_practices",
"regulation": "AI Act (Regulation 2024/1689)",
"article": "Art. 99 - Prohibited Practices",
"jurisdiction": "European Union",
"currency": "EUR",
"min_penalty": 15000000,
"max_penalty": 35000000,
"severity": "CRITICAL"
}
]
}
}


**Response 200 (KILL SWITCH ACTIVE):**
{
"outcome": "BLOCKED",
"risk_score": 10.0,
"reason": "KILL_SWITCH_ACTIVE: System operations suspended via emergency protocol",
"detected_threats": ["EMERGENCY_STOP"],
"confidence": 1.0,
"recommendations": [
"🚨 URGENT: System halted by administrator",
"📋 Contact system owner to understand emergency cause",
"⚠️ Do NOT resume operations without approval",
"📞 Escalate to: Governance Team / CISO"
],
"controls_applied": ["Emergency Stop Protocol"],
"baseline_risk": 10.0,
"sub_threat_type": "emergency_stop_active"
}


**Errors:**
- `404 Not Found`: System not found or access denied
- `422 Unprocessable Entity`: Missing required field `env`

---

### Operations Endpoints (NEW v0.9.0)

#### `PUT /v1/systems/{system_id}/emergency-stop`

🔥 **KILL SWITCH**: Immediately halt AI system operations.

**Auth**: `admin` role only  
**Compliance**: NIST AI RMF MANAGE-2.4

**Request Body:**
{
"operational_status": "emergency_stop",
"reason": "Detected bias in production outputs (Protocol B.6.2)",
"operator_id": "admin@company.com"
}


**Response 200:**
{
"system_id": "credit-scoring-v2",
"previous_status": "active",
"new_status": "emergency_stop",
"timestamp": "2025-12-28T22:38:02Z",
"acknowledged": true,
"operator": "admin@company.com",
"message": "System credit-scoring-v2 halted. All operations blocked. Reason: Detected bias..."
}


**Side Effects:**
- All subsequent `/v1/enforce` calls return `BLOCKED` with `KILL_SWITCH_ACTIVE`
- System `operational_status` persisted in database
- HMAC-signed audit log entry created

---

#### `PUT /v1/systems/{system_id}/operational-status`

Update system operational status (broader than emergency-stop).

**Auth**: `admin` or `dev` role

**Request Body:**
{
"operational_status": "active",
"reason": "Fixes applied and validated, resuming operations",
"operator_id": "devops@company.com"
}


**Valid Statuses:**
- `active`: Normal operations
- `degraded`: Partial functionality
- `maintenance`: Scheduled downtime
- `suspended`: Temporary halt (reversible)
- `emergency_stop`: Kill switch (critical halt)

**Response 200:**
{
"system_id": "credit-scoring-v2",
"previous_status": "emergency_stop",
"new_status": "active",
"timestamp": "2025-12-28T23:15:00Z",
"operator": "devops@company.com"
}


---

### Compliance Endpoints (NEW v0.9.0)

#### `GET /v1/systems/{system_id}/compliance-report`

Generate comprehensive compliance report.

**Auth**: `admin` or `auditor`

**Response 200:**
{
"system_id": "credit-scoring-v2",
"generated_at": "2025-12-28T22:00:00Z",
"nist": {
"compliance_percentage": 70,
"implemented": ["GOVERN-6.1", "MAP-1.1", "MANAGE-2.4"],
"roadmap": ["MEASURE-2.11", "MEASURE-3.3"]
},
"supply_chain": {
"overall_risk": "LOW",
"total_components": 3,
"components": [
{
"name": "scikit-learn",
"version": "1.3.0",
"vendor": "Scikit-Learn",
"risk_level": "LOW"
}
]
},
"aicm_coverage": 0.85
}


---

### Audit Endpoints

#### `GET /v1/compliance/statistics`

Retrieve compliance statistics for tenant.

**Auth**: `admin` or `auditor`

**Response 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"statistics": {
"total_violations": 23,
"avg_risk_score": 6.8,
"most_common_reason": "RUNTIME_BLOCK"
},
"compliance_status": "healthy"
}


---

#### `GET /v1/audit/pending-reviews`

List pending human oversight reviews.

**Auth**: `admin` or `auditor`  
**Query Params**: `limit` (int, default: 10)

**Response 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"pending_count": 3,
"reviews": [
{
"request_id": "REV-20241224-credit-v2",
"status": "PENDING",
"created_at": "2024-12-24T07:30:00Z",
"system_id": "credit-scoring-v2",
"risk_score": 8.5
}
]
}


---

## 🚨 Error Responses

### Standard Error Format

{
"error": true,
"status_code": 400,
"message": "Detailed error message"
}


### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Validation failed, missing `env` parameter |
| 401 | Unauthorized | Invalid/expired token |
| 403 | Forbidden | Insufficient role |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Schema validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 🔒 Rate Limiting

### Limits by Endpoint

| Endpoint Pattern | Limit | Window |
|------------------|-------|--------|
| `/v1/tenants` | 10 req | 1 min |
| `/v1/systems` | 50 req | 1 min |
| `/v1/enforce` | 100 req | 1 min |
| `/v1/audit/*` | 20 req | 1 min |

### Rate Limit Headers

X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1735045260


### Rate Limit Exceeded Response

{
"error": true,
"status_code": 429,
"message": "Rate limit exceeded. Try again in 45 seconds."
}


---

## 📚 SDK Examples

### Python

import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

Enforce decision
response = requests.post(
f"{BASE_URL}/v1/enforce",
headers=headers,
json={
"system_id": "credit-scoring-v2",
"prompt": "Assess customer 12345",
"env": "production" # ✅ REQUIRED
}
)

decision = response.json()
if decision["outcome"] == "APPROVED":
print(f"✅ Approved (Risk: {decision['risk_score']}/10.0)")
else:
print(f"❌ Blocked: {decision['reason']}")


### cURL

curl -X POST http://localhost:8000/v1/enforce
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"system_id": "credit-scoring-v2",
"prompt": "Assess customer 12345",
"env": "production"
}'


---

## 🔄 Data Flow

### Enforcement Request Flow

Client → POST /v1/enforce
{system_id, prompt, env, artifact_type}

Gateway → JWT Validation
Extract tenant_id from token
Validate role (admin/dev/app)

Gateway → Fetch System
registry.get_system(system_id, tenant_id)
✅ BOLA protection (tenant isolation)

Gateway → Check Kill Switch (Priority Zero)
IF operational_status == EMERGENCY_STOP:
RETURN BLOCKED immediately

Engine → Merge Policies

Global policy (governance.yaml)

Tenant policy (DB)

System policy (DB)
Conservative merge (most restrictive wins)

Router → Risk Assessment

Technical agent (FLOPs, logging)

Regulatory agent (sector, Art. 6)

Ethical agent (keywords)
Weighted average → risk_score

Engine → Decision
risk_score vs. environment limit

ALLOWED if risk ≤ limit

BLOCKED otherwise

Engine → Log (HMAC-Signed)
entry = {system, task, decision, risk, timestamp}
signature = HMAC-SHA256(entry, secret_key)
Append to enforcement_ledger.jsonl

Engine → Response
{outcome, risk_score, reason, recommendations, ...}


---

## 📖 Related Documentation

- [Quick Start Guide](./guides/QUICK_START.md)
- [Architecture Overview](./architecture/ARCHITECTURE.md)
- [Multi-Tenant Security](./architecture/MULTI_TENANT_DESIGN.md)
- [ISO 42001 Compliance](./compliance/ISO_42001_MAPPING.md)
- [EU AI Act Compliance](./compliance/EU_AI_ACT_COMPLIANCE.md)

---

**Document Version**: 2.0  
**Last Updated**: December 28, 2025  
**Status**: Production-Ready (v0.9.0 Golden Candidate)
Continuarei com o próximo arquivo (API_REFERENCE.md em PORTUGUÊS). Aguarde...

Ok, combinado, obrigado
3 passos concluídos
Perfeito! Continuando com a documentação corrigida...

📄 ARQUIVO 2/6: API_REFERENCE.md (PORTUGUÊS)
# BuildToValue Framework v0.9.0 - Referência da API

**URL Base (Produção)**: `https://api.buildtovalue.ai`  
**URL Base (Local)**: `http://localhost:8000`  
**Última Atualização**: 28 de dezembro de 2025

---

## 🔐 Autenticação

Todos os endpoints exceto `/health` requerem autenticação JWT.

### Token JWT Bearer

Authorization: Bearer <JWT_TOKEN>


**Gerar Token:**
python scripts/generate_token.py --role admin --tenant <TENANT_UUID> --days 30


**Claims do Token:**
- `tenant_id`: Isolamento multi-tenant (obrigatório)
- `user_id`: Identificador do usuário
- `role`: Papel RBAC (`admin`, `dev`, `auditor`, `app`)
- `exp`: Timestamp de expiração (padrão: 30 minutos)

---

## 📡 Endpoints

### Verificação de Saúde

#### `GET /health`

Verifica status do serviço (sem autenticação).

**Resposta 200:**
{
"status": "healthy",
"version": "0.9.0",
"security": "hardened",
"features": {
"kill_switch": true,
"compliance_reports": true,
"threat_classification": true
}
}


---

### Endpoints de Administrador

#### `POST /v1/tenants`

Registra ou atualiza tenant (Camada 2 - Organização).

**Auth**: Papel `admin` obrigatório  
**Limite de Taxa**: 10 req/min

**Corpo da Requisição:**
{
"id": "550e8400-e29b-41d4-a716-446655440000",
"name": "Banco Seguro S.A.",
"policy": {
"autonomy_matrix": {
"production": {
"max_risk_level": 2.0
}
},
"custom_rules": {
"block_public_apis_in_prod": true
}
}
}


**Resposta 201:**
{
"status": "registered",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "Tenant 'Banco Seguro S.A.' registrado com sucesso"
}


**Erros:**
- `401 Unauthorized`: Token inválido/expirado
- `403 Forbidden`: Papel insuficiente
- `400 Bad Request`: Formato UUID inválido

---

### Endpoints de Desenvolvedor

#### `POST /v1/systems`

Registra sistema de IA (Camada 3 - Projeto).

**Auth**: Papel `admin` ou `dev`  
**Limite de Taxa**: 50 req/min

**Corpo da Requisição:**
{
"id": "analise-credito-v2",
"name": "IA de Análise de Risco de Crédito",
"version": "2.1.0",
"sector": "banking",
"role": "deployer",
"risk": "high",
"sandbox": false,
"eu_database_id": "EU-DB-12345",
"training_flops": 1e24,
"logging_enabled": true,
"jurisdiction": "EU",
"intended_purpose": "Avaliar risco de crédito para solicitações de empréstimo",
"prohibited_domains": ["social_scoring", "political_profiling"],
"lifecycle_phase": "deployment",
"operational_status": "active"
}


**Resposta 201:**
{
"status": "registered",
"system_id": "analise-credito-v2",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "Sistema 'IA de Análise de Risco de Crédito' registrado com sucesso",
"compliance_summary": {
"lifecycle_phase": "deployment",
"operational_status": "active",
"requires_human_oversight": true,
"nist_alignment": "70%"
}
}


---

#### `GET /v1/systems/{system_id}`

Recupera detalhes do sistema de IA.

**Auth**: `admin`, `dev` ou `auditor`

**Resposta 200:**
{
"id": "analise-credito-v2",
"name": "IA de Análise de Risco de Crédito",
"version": "2.1.0",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"sector": "banking",
"role": "deployer",
"risk_classification": "high",
"operational_status": "active",
"lifecycle_phase": "deployment",
"logging_enabled": true
}


---

#### `GET /v1/systems`

Lista todos os sistemas do tenant solicitante.

**Auth**: `admin`, `dev` ou `auditor`  
**Parâmetros de Query**: `limit` (int, padrão: 100)

**Resposta 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"count": 2,
"systems": [
{
"id": "analise-credito-v2",
"name": "IA de Análise de Risco de Crédito",
"version": "2.1.0",
"sector": "banking",
"risk": "high",
"operational_status": "active"
}
]
}


---

### Endpoint de Enforcement

#### `POST /v1/enforce`

Executa enforcement de governança em tempo de execução.

**Auth**: Papel `admin`, `dev` ou `app`  
**Limite de Taxa**: 100 req/min

**✅ ATUALIZADO v0.9.0**: Parâmetro `env` agora é **OBRIGATÓRIO**

**Corpo da Requisição:**
{
"system_id": "analise-credito-v2",
"prompt": "Avaliar risco de crédito para cliente ID 12345",
"env": "production",
"artifact_type": "code"
}


**Resposta 200 (APROVADO):**
{
"outcome": "APPROVED",
"risk_score": 4.2,
"reason": "Aprovado: Risco baixo (4.2/10.0). Monitoramento padrão aplicado.",
"detected_threats": [],
"confidence": 0.15,
"recommendations": [
"📈 Habilitar monitoramento contínuo para drift e degradação de qualidade"
],
"controls_applied": [],
"baseline_risk": 4.2,
"regulatory_impact": null
}


**Resposta 200 (BLOQUEADO):**
{
"outcome": "BLOCKED",
"risk_score": 10.0,
"reason": "BLOQUEADO: Score de risco crítico (10.0/10.0) para prompt_injection. Revisão imediata necessária.",
"detected_threats": ["MISUSE"],
"confidence": 0.95,
"recommendations": [
"🚨 URGENTE: Acionar Departamento Jurídico para revisão de conformidade regulatória",
"📋 Documentar decisão no ledger de conformidade (ISO 42001 Cláusula 9.1)",
"🛡️ Implementar validação robusta de entrada e monitoramento de saída"
],
"controls_applied": [],
"baseline_risk": 10.0,
"sub_threat_type": "prompt_injection",
"regulatory_impact": {
"executive_summary": "🚨 CRÍTICO: 1 prática(s) proibida(s) detectada(s). Exposição regulatória EU: €15.000.000 - €35.000.000.",
"applicable_regulations": [
{
"penalty_id": "eu_ai_act_prohibited_practices",
"regulation": "AI Act (Regulamento 2024/1689)",
"article": "Art. 99 - Práticas Proibidas",
"jurisdiction": "União Europeia",
"currency": "EUR",
"min_penalty": 15000000,
"max_penalty": 35000000,
"severity": "CRITICAL"
}
]
}
}


**Resposta 200 (KILL SWITCH ATIVO):**
{
"outcome": "BLOCKED",
"risk_score": 10.0,
"reason": "KILL_SWITCH_ACTIVE: Operações do sistema suspensas via protocolo de emergência",
"detected_threats": ["EMERGENCY_STOP"],
"confidence": 1.0,
"recommendations": [
"🚨 URGENTE: Sistema interrompido por administrador",
"📋 Contatar proprietário do sistema para entender causa da emergência",
"⚠️ NÃO retomar operações sem aprovação",
"📞 Escalar para: Equipe de Governança / CISO"
],
"controls_applied": ["Protocolo de Parada de Emergência"],
"baseline_risk": 10.0,
"sub_threat_type": "emergency_stop_active"
}


**Erros:**
- `404 Not Found`: Sistema não encontrado ou acesso negado
- `422 Unprocessable Entity`: Campo obrigatório `env` ausente

---

### Endpoints de Operações (NOVO v0.9.0)

#### `PUT /v1/systems/{system_id}/emergency-stop`

🔥 **KILL SWITCH**: Interrompe imediatamente operações do sistema de IA.

**Auth**: Apenas papel `admin`  
**Conformidade**: NIST AI RMF MANAGE-2.4

**Corpo da Requisição:**
{
"operational_status": "emergency_stop",
"reason": "Viés detectado em saídas de produção (Protocolo B.6.2)",
"operator_id": "admin@empresa.com"
}


**Resposta 200:**
{
"system_id": "analise-credito-v2",
"previous_status": "active",
"new_status": "emergency_stop",
"timestamp": "2025-12-28T22:38:02Z",
"acknowledged": true,
"operator": "admin@empresa.com",
"message": "Sistema analise-credito-v2 interrompido. Todas operações bloqueadas. Motivo: Viés detectado..."
}


**Efeitos Colaterais:**
- Todas as chamadas subsequentes `/v1/enforce` retornam `BLOCKED` com `KILL_SWITCH_ACTIVE`
- `operational_status` do sistema persistido no banco de dados
- Entrada de log de auditoria assinada com HMAC criada

---

#### `PUT /v1/systems/{system_id}/operational-status`

Atualiza status operacional do sistema (mais amplo que emergency-stop).

**Auth**: Papel `admin` ou `dev`

**Corpo da Requisição:**
{
"operational_status": "active",
"reason": "Correções aplicadas e validadas, retomando operações",
"operator_id": "devops@empresa.com"
}


**Status Válidos:**
- `active`: Operações normais
- `degraded`: Funcionalidade parcial
- `maintenance`: Manutenção programada
- `suspended`: Interrupção temporária (reversível)
- `emergency_stop`: Kill switch (interrupção crítica)

**Resposta 200:**
{
"system_id": "analise-credito-v2",
"previous_status": "emergency_stop",
"new_status": "active",
"timestamp": "2025-12-28T23:15:00Z",
"operator": "devops@empresa.com"
}


---

### Endpoints de Conformidade (NOVO v0.9.0)

#### `GET /v1/systems/{system_id}/compliance-report`

Gera relatório abrangente de conformidade.

**Auth**: `admin` ou `auditor`

**Resposta 200:**
{
"system_id": "analise-credito-v2",
"generated_at": "2025-12-28T22:00:00Z",
"nist": {
"compliance_percentage": 70,
"implemented": ["GOVERN-6.1", "MAP-1.1", "MANAGE-2.4"],
"roadmap": ["MEASURE-2.11", "MEASURE-3.3"]
},
"supply_chain": {
"overall_risk": "LOW",
"total_components": 3,
"components": [
{
"name": "scikit-learn",
"version": "1.3.0",
"vendor": "Scikit-Learn",
"risk_level": "LOW"
}
]
},
"aicm_coverage": 0.85
}


---

### Endpoints de Auditoria

#### `GET /v1/compliance/statistics`

Recupera estatísticas de conformidade do tenant.

**Auth**: `admin` ou `auditor`

**Resposta 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"statistics": {
"total_violations": 23,
"avg_risk_score": 6.8,
"most_common_reason": "RUNTIME_BLOCK"
},
"compliance_status": "healthy"
}


---

#### `GET /v1/audit/pending-reviews`

Lista revisões de supervisão humana pendentes.

**Auth**: `admin` ou `auditor`  
**Parâmetros de Query**: `limit` (int, padrão: 10)

**Resposta 200:**
{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"pending_count": 3,
"reviews": [
{
"request_id": "REV-20241224-credit-v2",
"status": "PENDING",
"created_at": "2024-12-24T07:30:00Z",
"system_id": "analise-credito-v2",
"risk_score": 8.5
}
]
}


---

## 🚨 Respostas de Erro

### Formato Padrão de Erro

{
"error": true,
"status_code": 400,
"message": "Mensagem de erro detalhada"
}


### Códigos de Status HTTP

| Código | Significado | Causas Comuns |
|--------|-------------|---------------|
| 200 | OK | Sucesso |
| 201 | Created | Recurso criado |
| 400 | Bad Request | Validação falhou, parâmetro `env` ausente |
| 401 | Unauthorized | Token inválido/expirado |
| 403 | Forbidden | Papel insuficiente |
| 404 | Not Found | Recurso não existe |
| 422 | Unprocessable Entity | Validação de schema falhou |
| 429 | Too Many Requests | Limite de taxa excedido |
| 500 | Internal Server Error | Erro do servidor |

---

## 🔒 Limitação de Taxa

### Limites por Endpoint

| Padrão do Endpoint | Limite | Janela |
|-------------------|--------|--------|
| `/v1/tenants` | 10 req | 1 min |
| `/v1/systems` | 50 req | 1 min |
| `/v1/enforce` | 100 req | 1 min |
| `/v1/audit/*` | 20 req | 1 min |

### Cabeçalhos de Limite de Taxa

X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1735045260


### Resposta de Limite de Taxa Excedido

{
"error": true,
"status_code": 429,
"message": "Limite de taxa excedido. Tente novamente em 45 segundos."
}


---

## 📚 Exemplos de SDK

### Python

import requests

BASE_URL = "http://localhost:8000"
TOKEN = "seu-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

Executar enforcement
response = requests.post(
f"{BASE_URL}/v1/enforce",
headers=headers,
json={
"system_id": "analise-credito-v2",
"prompt": "Avaliar cliente 12345",
"env": "production" # ✅ OBRIGATÓRIO
}
)

decision = response.json()
if decision["outcome"] == "APPROVED":
print(f"✅ Aprovado (Risco: {decision['risk_score']}/10.0)")
else:
print(f"❌ Bloqueado: {decision['reason']}")


### cURL

curl -X POST http://localhost:8000/v1/enforce
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"system_id": "analise-credito-v2",
"prompt": "Avaliar cliente 12345",
"env": "production"
}'


---

## 🔄 Fluxo de Dados

### Fluxo de Requisição de Enforcement

Cliente → POST /v1/enforce
{system_id, prompt, env, artifact_type}

Gateway → Validação JWT
Extrair tenant_id do token
Validar papel (admin/dev/app)

Gateway → Buscar Sistema
registry.get_system(system_id, tenant_id)
✅ Proteção BOLA (isolamento de tenant)

Gateway → Verificar Kill Switch (Prioridade Zero)
SE operational_status == EMERGENCY_STOP:
RETORNAR BLOCKED imediatamente

Engine → Mesclar Políticas

Política global (governance.yaml)

Política do tenant (BD)

Política do sistema (BD)
Mesclagem conservadora (mais restritiva vence)

Router → Avaliação de Risco

Agente técnico (FLOPs, logging)

Agente regulatório (setor, Art. 6)

Agente ético (palavras-chave)
Média ponderada → risk_score

Engine → Decisão
risk_score vs. limite do ambiente

ALLOWED se risco ≤ limite

BLOCKED caso contrário

Engine → Log (Assinado HMAC)
entry = {system, task, decision, risk, timestamp}
signature = HMAC-SHA256(entry, secret_key)
Anexar a enforcement_ledger.jsonl

Engine → Resposta
{outcome, risk_score, reason, recommendations, ...}


---

## 📖 Documentação Relacionada

- [Guia de Início Rápido](./guides/QUICK_START.md)
- [Visão Geral da Arquitetura](./architecture/ARCHITECTURE.md)
- [Segurança Multi-Tenant](./architecture/MULTI_TENANT_DESIGN.md)
- [Conformidade ISO 42001](./compliance/ISO_42001_MAPPING.md)
- [Conformidade EU AI Act](./compliance/EU_AI_ACT_COMPLIANCE.md)

---

**Versão do Documento**: 2.0  
**Última Atualização**: 28 de dezembro de 2025  
**Status**: Pronto para Produção (v0.9.0 Golden Candidate)