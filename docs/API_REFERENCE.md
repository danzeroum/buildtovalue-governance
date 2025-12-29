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