# API Reference

**BuildToValue Framework v0.9**  
**Base URL:** `https://api.buildtovalue.ai` (production)  
**Base URL (Local):** `http://localhost:8000`

---

## Authentication

### JWT Bearer Token

Todos os endpoints (exceto `/health`) requerem autenticação via JWT.

**Header:**
Authorization: Bearer <JWT_TOKEN>

text

**Generate Token:**
python scripts/generate_token.py
--role admin
--tenant 550e8400-e29b-41d4-a716-446655440000
--days 30

text

---

## Endpoints

### Health Check

#### `GET /health`

Verifica status do serviço (sem autenticação).

**Response 200:**
{
"status": "healthy",
"version": "0.9.0",
"security": "hardened"
}

text

---

### Admin Endpoints

#### `POST /v1/tenants`

Registra ou atualiza tenant (Camada 2 - Empresa).

**Auth:** `admin` role required  
**Rate Limit:** 10 req/min

**Request:**
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

text

**Response 201:**
{
"status": "registered",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "Tenant 'Banco Seguro S.A.' registered successfully"
}

text

**Errors:**
- `401 Unauthorized` - Token inválido/expirado
- `403 Forbidden` - Role não autorizada
- `400 Bad Request` - UUID inválido

---

### Developer Endpoints

#### `POST /v1/systems`

Registra sistema de IA (Camada 3 - Projeto).

**Auth:** `admin` ou `dev` role  
**Rate Limit:** 50 req/min

**Request:**
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
"jurisdiction": "EU"
}

text

**Response 201:**
{
"status": "registered",
"system_id": "credit-scoring-v2",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "System 'Credit Risk Scoring AI' registered successfully"
}

text

**Validation Errors:**
{
"error": true,
"status_code": 400,
"message": "Sistema de ALTO RISCO deve ter logging_capabilities=True (Art. 12 EU AI Act)"
}

text

---

#### `GET /v1/systems/{system_id}`

Busca detalhes de um sistema.

**Auth:** `admin`, `dev` ou `auditor`

**Response 200:**
{
"id": "credit-scoring-v2",
"name": "Credit Risk Scoring AI",
"version": "2.1.0",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"sector": "banking",
"role": "deployer",
"risk_classification": "high",
"is_sandbox": false,
"jurisdiction": "EU",
"eu_database_id": "EU-DB-12345",
"logging_enabled": true
}

text

**Errors:**
- `404 Not Found` - Sistema não existe ou sem acesso

---

#### `GET /v1/systems`

Lista sistemas do tenant.

**Auth:** `admin`, `dev` ou `auditor`  
**Query Params:**
- `limit` (int, default=100) - Máximo de resultados

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
"risk": "high"
},
{
"id": "chatbot-v1",
"name": "Customer Support Bot",
"version": "1.0.0",
"sector": "general_commercial",
"risk": "minimal"
}
]
}

text

---

### Enforcement Endpoint

#### `POST /v1/enforce`

Executa enforcement de governança em runtime.

**Auth:** `admin`, `dev` ou `app` role  
**Rate Limit:** 100 req/min

**Request:**
{
"system_id": "credit-scoring-v2",
"prompt": "Avaliar risco de crédito para cliente ID 12345",
"env": "production",
"artifact_type": "code"
}

text

**Response 200 (ALLOWED):**
{
"decision": "ALLOWED",
"risk_score": 4.2,
"limit": 5.0,
"active_policy_hash": "a3f2c1d4",
"issues": [],
"escalation_required": false,
"environment": "production",
"timestamp": "2024-12-24T07:35:00Z"
}

text

**Response 200 (BLOCKED):**
{
"decision": "BLOCKED",
"risk_score": 8.5,
"limit": 3.0,
"active_policy_hash": "a3f2c1d4",
"issues": [
"🔴 Sistema de ALTO RISCO: banking (Anexo III EU AI Act)",
"⚠️ Termos suspeitos detectados: manipulação, exploração"
],
"escalation_required": true,
"review_id": "REV-20241224-credit-v2",
"environment": "production",
"timestamp": "2024-12-24T07:35:00Z"
}

text

**Errors:**
- `404 Not Found` - Sistema não encontrado ou sem acesso

---

### Audit Endpoints

#### `GET /v1/compliance/statistics`

Retorna estatísticas de compliance.

**Auth:** `admin` ou `auditor`

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

text

---

#### `GET /v1/audit/pending-reviews`

Lista revisões humanas pendentes.

**Auth:** `admin` ou `auditor`  
**Query Params:**
- `limit` (int, default=10)

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
"task": {
"title": "Avaliar risco de crédito...",
"description": ""
},
"decision": {
"risk_score": 8.5,
"limit": 3.0
}
}
]
}

text

---

## Error Responses

### Standard Error Format

{
"error": true,
"status_code": 400,
"message": "Detailed error message"
}

text

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Sucesso |
| 201 | Created | Recurso criado |
| 400 | Bad Request | Validação falhou |
| 401 | Unauthorized | Token inválido/expirado |
| 403 | Forbidden | Role não autorizada |
| 404 | Not Found | Recurso não existe |
| 500 | Internal Error | Erro do servidor |

---

## Rate Limiting

### Limits

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

text

### Rate Limit Exceeded

**Response 429:**
{
"error": true,
"status_code": 429,
"message": "Rate limit exceeded. Try again in 45 seconds."
}

text

---

## SDK Examples

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
"prompt": "Avaliar cliente 12345",
"env": "production"
}
)

decision = response.json()
if decision["decision"] == "ALLOWED":
# Prosseguir com IA
result = call_openai_api(...)
else:
# Bloqueado - escalar para humano
print(f"Blocked: {decision['issues']}")

text

### cURL

Enforce
curl -X POST http://localhost:8000/v1/enforce
-H "Authorization: Bearer $TOKEN"
-H "Content-Type: application/json"
-d '{
"system_id": "credit-scoring-v2",
"prompt": "Avaliar cliente 12345",
"env": "production"
}'

text

---

## OpenAPI Specification

**Interactive Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Download OpenAPI JSON:**
curl http://localhost:8000/openapi.json > btv-openapi.json

text

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-24  
**API Stability:** Stable (v0.9+)