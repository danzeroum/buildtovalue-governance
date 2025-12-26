# BuildToValue Architecture

**Version:** 7.3.0  
**Type:** Enterprise AI Governance Framework  
**Architecture Pattern:** Layered Architecture + Domain-Driven Design

---

## System Overview

BuildToValue é um **middleware de governança de IA** que intercepta decisões de sistemas de IA, avalia riscos em tempo real e aplica políticas de conformidade automaticamente.

### Core Value Proposition

> "A IA pode automatizar o trabalho — mas a governança garante o valor."

### High-Level Architecture

┌─────────────────────────────────────────────────────────────────┐
│ External AI Systems │
│ (OpenAI, Anthropic, Internal Models) │
└─────────────────────┬───────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ API Gateway (FastAPI) │
│ JWT Auth + RBAC → Rate Limiting → Request Validation │
└─────────────────────┬───────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Runtime Enforcement Engine │
│ ┌───────────────┐ ┌────────────────┐ ┌──────────────────┐ │
│ │ Policy Merger │→ │ Risk Assessment│→ │ Decision + Log │ │
│ │ (3 Layers) │ │ (3 Agents) │ │ (HMAC-Signed) │ │
│ └───────────────┘ └────────────────┘ └──────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
│
┌───────────┴────────────┬──────────────┐
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
│ System │ │ Compliance │ │ Human │
│ Registry │ │ Memory (RAG) │ │ Oversight │
│ (Multi-Tenant) │ │ (Historical) │ │ (Reviews) │
└─────────────────┘ └─────────────────┘ └──────────────┘
│ │ │
└────────────────────────┴───────────────────┘
│
▼
┌─────────────────────────┐
│ PostgreSQL Database │
│ (Tenants + Systems) │
└─────────────────────────┘

text

---

## Layered Architecture

### Layer 1: Domain Layer (`src/domain/`)

**Purpose:** Business entities and rules (framework-agnostic)

**Components:**
- `entities.py` - Core business objects (AISystem, Task)
- `enums.py` - Type-safe enumerations (AISector, EUComplianceRisk)

**Design Principles:**
- No dependencies on frameworks (pure Python)
- Validation logic in entity constructors
- Immutable where possible (Pydantic `frozen=True`)

**Example:**
class AISystem(BaseModel):
"""ISO 42001 + EU AI Act compliant entity"""
id: str
tenant_id: str # UUID v4 validated
risk_classification: EUComplianceRisk

text
@field_validator('tenant_id')
def validate_uuid(cls, v):
    # Domain-level validation
    if not is_valid_uuid_v4(v):
        raise ValueError("Invalid UUID v4")
text

---

### Layer 2: Core Layer (`src/core/`)

**Purpose:** Business logic and orchestration

**Components:**
- `registry/` - System and Tenant management
- `governance/` - Enforcement engine and policy merge

**Key Classes:**

#### SystemRegistry
class SystemRegistry:
"""Multi-tenant registry with BOLA protection"""

text
def get_system(self, system_id: str, requesting_tenant: str):
    # CRITICAL: Query filters by tenant_id (isolation)
    return session.query(AISystemModel).filter_by(
        id=system_id,
        tenant_id=requesting_tenant  # BOLA protection
    ).first()
text

#### RuntimeEnforcementEngine
class RuntimeEnforcementEngine:
"""3-layer policy merge + risk assessment"""

text
def enforce(self, task, system, env):
    # 1. Merge policies (Global > Tenant > System)
    active_policy = self._merge_policies(system)
    
    # 2. Assess risk (3 agents)
    assessment = self.router.assess_risk(task, system)
    
    # 3. Compare against limit
    decision = "ALLOWED" if risk <= limit else "BLOCKED"
    
    # 4. Log signed
    self._log_signed(decision)
text

---

### Layer 3: Intelligence Layer (`src/intelligence/`)

**Purpose:** AI-powered risk assessment

**Components:**
- `routing/adaptive_router.py` - Multi-agent risk scoring

**3-Agent Architecture:**

class AdaptiveRiskRouter:
def assess_risk(self, task, system):
scores = {
"technical": self._assess_technical_risk(), # 30% weight
"regulatory": self._assess_regulatory_risk(), # 40% weight (critical)
"ethical": self._assess_ethical_risk() # 30% weight
}
return weighted_average(scores)

text

**Agent Details:**

| Agent | Focus | Inputs | Output |
|-------|-------|--------|--------|
| Technical | Compute, logging, complexity | FLOPs, logging_capabilities, task_length | 0-10 risk |
| Regulatory | EU AI Act, ISO 42001 | sector, risk_class, jurisdiction | 0-10 risk |
| Ethical | Fairness, transparency | keywords, sector, transparency | 0-10 risk |

---

### Layer 4: Compliance Layer (`src/compliance/`)

**Purpose:** Regulatory compliance tools

**Components:**
- `analytics/rag_memory.py` - Historical violation tracking

**RAG Memory Design:**
violations.jsonl (append-only log)
├── Entry 1: {timestamp, task, system, risk, reason}
├── Entry 2: {timestamp, task, system, risk, reason}
└── Entry N: {timestamp, task, system, risk, reason}

query_similar(task) → Top-K similar violations (text-based search)

text

**Future Enhancement:**
- Upgrade to vector embeddings (ChromaDB)
- Semantic similarity search (sentence-transformers)

---

### Layer 5: Interface Layer (`src/interface/`)

**Purpose:** External interactions (APIs, UI)

**Components:**
- `api/gateway.py` - REST API (FastAPI)
- `api/auth.py` - JWT + RBAC
- `human_oversight/dashboard.py` - Review workflow

**API Gateway Architecture:**

Request → CORS Middleware → Authentication → RBAC → Rate Limiting → Endpoint
↓ ↓ ↓
JWT Verify Role Check SlowAPI
(HS256) (4 roles) (100/min)

text

**RBAC Matrix:**

| Endpoint | admin | dev | auditor | app |
|----------|-------|-----|---------|-----|
| POST /v1/tenants | ✅ | ❌ | ❌ | ❌ |
| POST /v1/systems | ✅ | ✅ | ❌ | ❌ |
| POST /v1/enforce | ✅ | ✅ | ❌ | ✅ |
| GET /v1/audit/* | ✅ | ❌ | ✅ | ❌ |

---

## Security Architecture

### Defense-in-Depth Layers

Layer 7: Application Logic
└─ Input validation (Pydantic schemas)
└─ Business rules enforcement

Layer 6: Authorization
└─ RBAC (4 roles)
└─ Tenant isolation (BOLA protection)

Layer 5: Authentication
└─ JWT (30-min expiration)
└─ Claim validation

Layer 4: API Security
└─ Rate limiting (100 req/min)
└─ CORS policies

Layer 3: Data Security
└─ SQL injection prevention (ORM)
└─ UUID v4 validation

Layer 2: Network Security
└─ HTTPS/TLS 1.3
└─ Docker network isolation

Layer 1: Infrastructure Security
└─ Non-root containers
└─ Read-only filesystem

text

### OWASP API Top 10 2023 Mitigations

| Vulnerability | Mitigation | Code Reference |
|---------------|------------|----------------|
| API1: BOLA | tenant_id in all queries | `SystemRegistry.get_system()` |
| API2: Auth | JWT validation + claims | `auth.py:verify_jwt_token()` |
| API5: RBAC | require_role decorator | `auth.py:require_role()` |
| API6: Mass Assignment | tenant_id from token | `gateway.py:register_system()` |
| API8: SQL Injection | SQLAlchemy ORM | `system_registry.py` (no raw SQL) |

---

## Data Flow

### Enforcement Request Flow

Client → POST /v1/enforce
{
"system_id": "credit-ai",
"prompt": "Evaluate loan application",
"env": "production"
}

Gateway → JWT Validation

Extract tenant_id from token

Validate role (admin/dev/app)

Gateway → Fetch System

registry.get_system(system_id, tenant_id)

BOLA protection ensures isolation

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

ALLOWED if risk <= limit

BLOCKED otherwise

Engine → Log (HMAC-Signed)

entry = {system, task, decision, risk, timestamp}

signature = HMAC-SHA256(entry, secret_key)

Append to enforcement_ledger.jsonl

Engine → Response
{
"decision": "ALLOWED",
"risk_score": 4.2,
"limit": 5.0,
"issues": []
}

text

---

## Database Schema

### Tenants Table
CREATE TABLE tenants (
id VARCHAR PRIMARY KEY, -- UUID v4
name VARCHAR NOT NULL,
governance_policy JSONB,
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()
);

text

### AI Systems Table
CREATE TABLE ai_systems (
id VARCHAR PRIMARY KEY,
tenant_id VARCHAR NOT NULL, -- Foreign key + Index
name VARCHAR NOT NULL,
version VARCHAR DEFAULT '1.0.0',
sector VARCHAR NOT NULL,
role VARCHAR NOT NULL,
risk_classification VARCHAR NOT NULL,
high_risk_flags JSONB DEFAULT '[]',
governance_policy JSONB,
is_sandbox_mode INTEGER DEFAULT 0,
training_compute_flops BIGINT,
eu_database_registration_id VARCHAR,
logging_capabilities INTEGER DEFAULT 0,
jurisdiction VARCHAR DEFAULT 'EU',
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),

text
INDEX idx_tenant_system (tenant_id, id)  -- Performance + Security
);

text

---

## Deployment Architecture

### Docker Compose (Development)
┌─────────────────┐
│ btv-api │ :8000
│ (FastAPI) │
└────────┬────────┘
│
▼
┌─────────────────┐
│ btv-db │ :5432
│ (PostgreSQL) │
└─────────────────┘

text

### Production (Kubernetes)
text
               ┌──────────────┐
Internet ────────> │ Ingress │
│ (NGINX/TLS) │
└──────┬───────┘
│
┌─────────────┴─────────────┐
▼ ▼
┌───────────────┐ ┌───────────────┐
│ btv-api Pod 1 │ │ btv-api Pod 2 │
│ (4 workers) │ │ (4 workers) │
└───────┬───────┘ └───────┬───────┘
│ │
└──────────┬────────────────┘
▼
┌─────────────────┐
│ PostgreSQL │
│ (StatefulSet) │
└─────────────────┘

text

---

## Performance Characteristics

### Latency Targets (p95)

| Operation | Target | Typical |
|-----------|--------|---------|
| JWT validation | < 5ms | 2ms |
| System lookup (DB) | < 10ms | 5ms |
| Risk assessment | < 50ms | 30ms |
| Total enforcement | < 100ms | 60ms |

### Scalability

- **Horizontal:** Add more API pods (stateless)
- **Vertical:** Increase DB resources (indexed queries)
- **Caching:** Redis for system metadata (future)

### Throughput

- **Single Pod:** 100-200 req/s
- **4 Pods:** 400-800 req/s
- **Bottleneck:** Database writes (ledger)

---

## Observability

### Metrics (Prometheus)

Future implementation
from prometheus_client import Counter, Histogram

enforcement_total = Counter('btv_enforcement_total', 'Total enforcements')
enforcement_blocked = Counter('btv_enforcement_blocked', 'Blocked decisions')
enforcement_latency = Histogram('btv_enforcement_duration_seconds', 'Latency')

text

### Logging

- **Structured JSON logs** (for Datadog, Splunk)
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Sensitive data:** Redacted (PII, credentials)

### Tracing (OpenTelemetry)

Future: Distributed tracing
from opentelemetry import trace

tracer = trace.get_tracer("btv.enforcement")

with tracer.start_as_current_span("enforce_decision"):
decision = engine.enforce(task, system, env)

text

---

## Design Decisions (ADRs)

### ADR-001: SQLAlchemy ORM vs Raw SQL
**Decision:** SQLAlchemy ORM  
**Rationale:** Prevents SQL injection, supports multiple DBs  
**Trade-off:** Slight performance overhead (acceptable for security)

### ADR-002: JWT vs Session Cookies
**Decision:** JWT (stateless)  
**Rationale:** Horizontal scalability, no session store needed  
**Trade-off:** Cannot revoke individual tokens (use short expiration)

### ADR-003: HMAC vs Digital Signatures
**Decision:** HMAC-SHA256  
**Rationale:** Faster, simpler, sufficient for tamper-proof logs  
**Trade-off:** Shared secret (vs. public/private keys)

### ADR-004: Append-Only Ledger vs Database
**Decision:** JSONL append-only file  
**Rationale:** Immutability, simplicity, auditability  
**Trade-off:** Query performance (acceptable for audit logs)

---

## Future Architecture Enhancements

### v8.0 Roadmap

1. **Dashboard UI (React)**
   - Real-time compliance monitoring
   - Human oversight interface
   - Grafana-style dashboards

2. **Vector Database (ChromaDB)**
   - Semantic search for violations
   - Embedding-based similarity

3. **Auto-Remediation Agents**
   - LLM-powered policy suggestions
   - Automated corrective actions

4. **Multi-Cloud Support**
   - AWS, Azure, GCP deployment templates
   - Cloud-native secrets management

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-24  
**Author:** BuildToValue Architecture Team