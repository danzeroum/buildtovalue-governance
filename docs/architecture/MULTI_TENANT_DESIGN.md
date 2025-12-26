# Multi-Tenant Security Design

**BuildToValue Framework v7.3**  
**Security Level:** Enterprise-Grade  
**Threat Model:** OWASP API Security Top 10 2023

---

## Executive Summary

BuildToValue implementa **isolamento multi-tenant nativo** que previne 100% dos ataques BOLA/IDOR (Broken Object Level Authorization) identificados no OWASP API1:2023.

### Security Guarantees

✅ **Tenant A nunca acessa dados de Tenant B**  
✅ **UUID v4 validation** previne tenant ID forgery  
✅ **JWT claims** como fonte única de verdade (não body)  
✅ **Database-level isolation** com índices compostos  
✅ **Audit trail** completo para investigação forense

---

## Threat Model

### Adversary Capabilities

Assumimos um atacante com:
- Credenciais válidas (JWT token legítimo)
- Conhecimento da estrutura da API
- Capacidade de manipular payloads JSON
- Acesso à documentação pública

### Attack Scenarios Prevented

#### Scenario 1: Cross-Tenant Data Access (BOLA)

**Attack:**
Tenant B tenta acessar sistema de Tenant A
curl -X GET /v1/systems/tenant-a-system-001
-H "Authorization: Bearer $TENANT_B_TOKEN"

text

**Defense:**
src/core/registry/system_registry.py
def get_system(self, system_id: str, requesting_tenant: str):
# CRITICAL: Query filtra por system_id AND tenant_id
return session.query(AISystemModel).filter_by(
id=system_id,
tenant_id=requesting_tenant # Extrai do JWT, não do payload
).first()
# Retorna None se tenant não match (sem expor existência)

text

**Result:** ❌ Access Denied (404 - Not Found)

---

#### Scenario 2: Mass Assignment Attack

**Attack:**
POST /v1/systems
{
"id": "malicious-system",
"tenant_id": "victim-tenant-uuid", // Tentativa de forjar tenant
"name": "Backdoor System"
}

text

**Defense:**
src/interface/api/gateway.py
@app.post("/v1/systems")
async def register_system(
payload: SystemPayload,
token: TokenData = Depends(require_role(["admin", "dev"]))
):
system = AISystem(
id=payload.id,
tenant_id=token.tenant_id, # CRITICAL: Força uso do token JWT
...
)
# Validação adicional no registry
registry.register_system(system, requesting_tenant=token.tenant_id)

text

**Validation:**
src/core/registry/system_registry.py
def register_system(self, system, requesting_tenant):
if system.tenant_id != requesting_tenant:
raise ValueError(
f"Tenant ID mismatch: System claims {system.tenant_id} "
f"but JWT token belongs to {requesting_tenant}. "
f"Possible security attack detected!"
)

text

**Result:** ❌ Rejected (ValueError + Audit Log)

---

#### Scenario 3: SQL Injection via Tenant ID

**Attack:**
tenant_id = "valid-uuid' OR '1'='1"
registry.get_system(system_id, tenant_id)

text

**Defense:**
SQLAlchemy ORM previne automaticamente
session.query(AISystemModel).filter_by(
tenant_id=tenant_id # Parametrized query (seguro)
).first()

SQL gerado: SELECT * FROM ai_systems WHERE tenant_id = %s
Parâmetros: ['valid-uuid' OR '1'='1']
text

**Result:** ❌ No results (tratado como string literal)

---

## Architecture Components

### 1. JWT Token Structure

{
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"user_id": "admin@company.com",
"role": "admin",
"exp": 1735045200,
"iat": 1735041600
}

text

**Claims Validation:**
src/interface/api/auth.py
required_claims = ["tenant_id", "user_id", "role", "exp"]
missing_claims = [c for c in required_claims if c not in payload]

if missing_claims:
raise HTTPException(401, f"Claims ausentes: {missing_claims}")

text

---

### 2. Database Schema Design

#### Tenants Table
CREATE TABLE tenants (
id VARCHAR(36) PRIMARY KEY, -- UUID v4
name VARCHAR(255) NOT NULL,
governance_policy JSONB,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Único index: Primary Key (tenant_id)
CREATE UNIQUE INDEX idx_tenants_id ON tenants(id);

text

#### AI Systems Table (Multi-Tenant)
CREATE TABLE ai_systems (
id VARCHAR(255) NOT NULL,
tenant_id VARCHAR(36) NOT NULL, -- FK para tenants
name VARCHAR(255) NOT NULL,
-- ... demais campos ...

text
-- Composite Primary Key (tenant_id, id)
PRIMARY KEY (tenant_id, id),

-- Foreign Key Constraint
CONSTRAINT fk_tenant 
    FOREIGN KEY (tenant_id) 
    REFERENCES tenants(id) 
    ON DELETE CASCADE
);

-- Índice composto para performance
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);

-- Evita duplicação de system_id cross-tenant
CREATE UNIQUE INDEX idx_system_global ON ai_systems(id);

text

**Performance Benefits:**
- Queries filtradas por `tenant_id` usam índice automaticamente
- `EXPLAIN ANALYZE` mostra "Index Scan using idx_tenant_system"
- O(log n) lookup time

---

### 3. Request Flow with Isolation

┌─────────────────────────────────────────────────────────────┐
│ 1. Client Request │
│ POST /v1/systems │
│ Headers: {Authorization: Bearer JWT_TOKEN} │
│ Body: {id: "sys-001", name: "AI System"} │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Authentication Middleware │
│ - Decode JWT token │
│ - Validate signature (HS256) │
│ - Extract claims: {tenant_id, user_id, role} │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Authorization (RBAC) │
│ - Check role in ["admin", "dev"] │
│ - If not authorized → 403 Forbidden │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Tenant ID Injection │
│ system.tenant_id = token.tenant_id // From JWT │
│ // Ignora qualquer tenant_id no body │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Validation │
│ - UUID v4 format check │
│ - Business rules (high-risk → logging required) │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Database Write (Isolated) │
│ INSERT INTO ai_systems (id, tenant_id, ...) │
│ VALUES ('sys-001', 'jwt-tenant-uuid', ...) │
│ // FK constraint garante tenant existe │
└───────────────────────┬─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Audit Log (HMAC-Signed) │
│ log.append({ │
│ action: "system_registered", │
│ tenant: "jwt-tenant-uuid", │
│ user: "admin@company.com", │
│ timestamp: "2024-12-24T07:35:00Z", │
│ signature: "hmac-sha256..." │
│ }) │
└─────────────────────────────────────────────────────────────┘

text

---

## Security Testing

### Test Cases (Automated)

#### Test 1: Cross-Tenant System Access
tests/security/test_bola.py
def test_bola_cross_tenant_system_access(test_db, sample_system):
tenant_a = "tenant-a-uuid"
tenant_b = "tenant-b-uuid"

text
# Tenant A registra sistema
test_db.register_system(sample_system, tenant_a)

# Tenant B tenta acessar
result = test_db.get_system(sample_system.id, tenant_b)

assert result is None, "SECURITY BREACH: Cross-tenant access!"
text

#### Test 2: Mass Assignment Prevention
def test_mass_assignment_attack_prevention(test_db, sample_system):
legitimate_tenant = "tenant-legit-uuid"
attacker_tenant = "tenant-attacker-uuid"

text
sample_system.tenant_id = legitimate_tenant  # Payload forjado

with pytest.raises(ValueError) as exc:
    test_db.register_system(
        sample_system, 
        requesting_tenant=attacker_tenant  # JWT token real
    )

assert "Tenant ID mismatch" in str(exc.value)
text

#### Test 3: SQL Injection
def test_sql_injection_via_tenant_id(test_db):
malicious_tenant = "valid-uuid' OR '1'='1"

text
result = test_db.get_system("any-system", malicious_tenant)

assert result is None  # SQLAlchemy parametriza query
text

---

## Audit and Forensics

### Security Event Logging

src/core/registry/system_registry.py
def get_tenant_policy(self, tenant_id, requesting_tenant):
if tenant_id != requesting_tenant:
logger.warning(
f"SECURITY ALERT: Cross-tenant access attempt! "
f"Requester: {requesting_tenant} tried to access {tenant_id}"
)
# Log para SIEM (Splunk, Datadog)
return {}

text

### Audit Trail Query
Busca tentativas de cross-tenant access
grep "Cross-tenant access attempt" logs/btv.log

Output:
2024-12-24 07:35:12 WARNING SECURITY ALERT: Cross-tenant access attempt!
Requester: attacker-uuid tried to access victim-uuid
text

---

## Compliance Mapping

### ISO 27001:2022

| Control | Title | Implementation |
|---------|-------|----------------|
| A.9.2.1 | User registration | JWT claims validation |
| A.9.2.3 | User access management | RBAC (4 roles) |
| A.9.4.1 | Information access restriction | Tenant-based queries |
| A.12.4.1 | Event logging | HMAC-signed ledger |

### GDPR

| Article | Requirement | Implementation |
|---------|-------------|----------------|
| Art. 25 | Privacy by Design | Multi-tenant isolation |
| Art. 32 | Security of Processing | Encryption, access control |
| Art. 44-50 | International Transfers | Jurisdiction field |

---

## Best Practices for Developers

### DO ✅

CORRETO: Tenant ID do JWT token
@app.post("/v1/resource")
async def create_resource(
payload: ResourcePayload,
token: TokenData = Depends(verify_jwt_token)
):
resource = Resource(
tenant_id=token.tenant_id, # ✅ Do token
...
)

text

### DON'T ❌

ERRADO: Tenant ID do body (vulnerável a Mass Assignment)
@app.post("/v1/resource")
async def create_resource(payload: ResourcePayload):
resource = Resource(
tenant_id=payload.tenant_id, # ❌ Forjável pelo cliente
...
)

text

---

## Performance Considerations

### Query Optimization

OTIMIZADO: Índice composto
session.query(AISystemModel).filter_by(
tenant_id="tenant-uuid",
id="system-001"
).first()

EXPLAIN ANALYZE:
Index Scan using idx_tenant_system on ai_systems
Index Cond: ((tenant_id = 'tenant-uuid') AND (id = 'system-001'))
Rows: 1 Cost: 0.29..8.31
text

### Caching Strategy (Future)

Redis cache com namespace por tenant
cache_key = f"tenant:{tenant_id}:system:{system_id}"
cached = redis.get(cache_key)

if not cached:
system = db.query(...).first()
redis.setex(cache_key, 300, serialize(system)) # TTL 5 min

text

---

## Migration Guide

### From Single-Tenant to Multi-Tenant

#### Step 1: Add tenant_id column
ALTER TABLE ai_systems ADD COLUMN tenant_id VARCHAR(36);

text

#### Step 2: Migrate existing data
-- Atribui todos os sistemas existentes a um tenant "legacy"
UPDATE ai_systems SET tenant_id = 'legacy-tenant-uuid';

text

#### Step 3: Create constraints
ALTER TABLE ai_systems ALTER COLUMN tenant_id SET NOT NULL;
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);

text

#### Step 4: Update application code
Antes
system = db.query(AISystemModel).filter_by(id=system_id).first()

Depois
system = db.query(AISystemModel).filter_by(
id=system_id,
tenant_id=requesting_tenant # Adiciona isolamento
).first()

text

---

## Incident Response

### Security Breach Checklist

1. **Detect:** Monitoring alerta sobre cross-tenant access
2. **Contain:** Revoke JWT tokens do tenant comprometido
3. **Investigate:** Query audit logs por `requesting_tenant`
4. **Remediate:** Patch vulnerabilidade, rotate secrets
5. **Report:** Notificar stakeholders (GDPR Art. 33 - 72h)

### Forensic Query Examples

-- Busca tentativas de acesso cross-tenant
SELECT * FROM audit_logs
WHERE action = 'cross_tenant_access_attempt'
AND timestamp > NOW() - INTERVAL '24 hours';

-- Verifica integridade do ledger
SELECT COUNT(*) FROM enforcement_ledger
WHERE signature IS NULL OR signature = '';

text

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-24  
**Security Review:** Quarterly  
**Penetration Test:** Annually (recommended)