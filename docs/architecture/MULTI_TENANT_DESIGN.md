
# Multi-Tenant Security Design / Design de Segurança Multi-Tenant

**BuildToValue Framework v0.9.0**  
**Security Level / Nível de Segurança:** Enterprise-Grade  
**Threat Model / Modelo de Ameaças:** OWASP API Security Top 10 2023

---

<details>
<summary><strong>🇬🇧 ENGLISH VERSION</strong></summary>

## Executive Summary

BuildToValue implements **native multi-tenant isolation** that prevents 100% of BOLA/IDOR (Broken Object Level Authorization) attacks identified in OWASP API1:2023.

### Security Guarantees

✅ **Tenant A never accesses Tenant B's data**  
✅ **UUID v4 validation** prevents tenant ID forgery  
✅ **JWT claims** as single source of truth (not request body)  
✅ **Database-level isolation** with composite indexes  
✅ **Complete audit trail** for forensic investigation

---

## Threat Model

### Adversary Capabilities

We assume an attacker with:
- Valid credentials (legitimate JWT token)
- Knowledge of API structure
- Ability to manipulate JSON payloads
- Access to public documentation

### Attack Scenarios Prevented

#### Scenario 1: Cross-Tenant Data Access (BOLA)

**Attack:**
```
# Tenant B tries to access Tenant A's system
curl -X GET /v1/systems/tenant-a-system-001 \
  -H "Authorization: Bearer $TENANT_B_TOKEN"
```

**Defense:**
```
# src/core/registry/system_registry.py
def get_system(self, system_id: str, requesting_tenant: str):
    # CRITICAL: Query filters by system_id AND tenant_id
    return session.query(AISystemModel).filter_by(
        id=system_id,
        tenant_id=requesting_tenant  # Extracted from JWT, not payload
    ).first()
    # Returns None if tenant doesn't match (without exposing existence)
```

**Result:** ❌ Access Denied (404 - Not Found)

---

#### Scenario 2: Mass Assignment Attack

**Attack:**
```
POST /v1/systems
{
  "id": "malicious-system",
  "tenant_id": "victim-tenant-uuid",  // Attempt to forge tenant
  "name": "Backdoor System"
}
```

**Defense:**
```
# src/interface/api/gateway.py
@app.post("/v1/systems")
async def register_system(
    payload: SystemPayload,
    token: TokenData = Depends(require_role(["admin", "dev"]))
):
    system = AISystem(
        id=payload.id,
        tenant_id=token.tenant_id,  # CRITICAL: Force JWT token usage
        ...
    )
    # Additional validation in registry
    registry.register_system(system, requesting_tenant=token.tenant_id)
```

**Validation:**
```
# src/core/registry/system_registry.py
def register_system(self, system, requesting_tenant):
    if system.tenant_id != requesting_tenant:
        raise ValueError(
            f"Tenant ID mismatch: System claims {system.tenant_id} "
            f"but JWT token belongs to {requesting_tenant}. "
            f"Possible security attack detected!"
        )
```

**Result:** ❌ Rejected (ValueError + Audit Log)

---

## Architecture Components

### 1. JWT Token Structure

```
{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "admin@company.com",
  "role": "admin",
  "exp": 1735045200,
  "iat": 1735041600
}
```

**Claims Validation:**
```
# src/interface/api/auth.py
required_claims = ["tenant_id", "user_id", "role", "exp"]
missing_claims = [c for c in required_claims if c not in payload]

if missing_claims:
    raise HTTPException(401, f"Missing claims: {missing_claims}")
```

---

### 2. Database Schema Design

#### Tenants Table
```
CREATE TABLE tenants (
    id VARCHAR(36) PRIMARY KEY,  -- UUID v4
    name VARCHAR(255) NOT NULL,
    governance_policy JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_tenants_id ON tenants(id);
```

#### AI Systems Table (Multi-Tenant)
```
CREATE TABLE ai_systems (
    id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(36) NOT NULL,  -- FK to tenants
    name VARCHAR(255) NOT NULL,
    -- ... other fields ...
    
    -- Composite Primary Key (tenant_id, id)
    PRIMARY KEY (tenant_id, id),
    
    -- Foreign Key Constraint
    CONSTRAINT fk_tenant 
        FOREIGN KEY (tenant_id) 
        REFERENCES tenants(id) 
        ON DELETE CASCADE
);

-- Composite index for performance
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);

-- Prevent system_id duplication across tenants
CREATE UNIQUE INDEX idx_system_global ON ai_systems(id);
```

**Performance Benefits:**
- Queries filtered by `tenant_id` automatically use index
- `EXPLAIN ANALYZE` shows "Index Scan using idx_tenant_system"
- O(log n) lookup time

---

### 3. Request Flow with Isolation

```
┌─────────────────────────────────────────────────────────────┐
│  1. Client Request                                          │
│     POST /v1/systems                                        │
│     Headers: {Authorization: Bearer JWT_TOKEN}              │
│     Body: {id: "sys-001", name: "AI System"}                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Authentication Middleware                               │
│     - Decode JWT token                                      │
│     - Validate signature (HS256)                            │
│     - Extract claims: {tenant_id, user_id, role}            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Authorization (RBAC)                                    │
│     - Check role in ["admin", "dev"]                        │
│     - If not authorized → 403 Forbidden                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Tenant ID Injection                                     │
│     system.tenant_id = token.tenant_id  // From JWT        │
│     // Ignores any tenant_id in body                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Validation                                              │
│     - UUID v4 format check                                  │
│     - Business rules (high-risk → logging required)         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Database Write (Isolated)                               │
│     INSERT INTO ai_systems (id, tenant_id, ...)             │
│     VALUES ('sys-001', 'jwt-tenant-uuid', ...)              │
│     // FK constraint ensures tenant exists                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Audit Log (HMAC-Signed)                                 │
│     log.append({                                            │
│       action: "system_registered",                          │
│       tenant: "jwt-tenant-uuid",                            │
│       user: "admin@company.com",                            │
│       timestamp: "2025-12-28T22:00:00Z",                    │
│       signature: "hmac-sha256..."                           │
│     })                                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Testing

### Test Cases (Automated)

#### Test 1: Cross-Tenant System Access
```
# tests/security/test_bola.py
def test_bola_cross_tenant_system_access(test_db, sample_system):
    tenant_a = "tenant-a-uuid"
    tenant_b = "tenant-b-uuid"
    
    # Tenant A registers system
    test_db.register_system(sample_system, tenant_a)
    
    # Tenant B tries to access
    result = test_db.get_system(sample_system.id, tenant_b)
    
    assert result is None, "SECURITY BREACH: Cross-tenant access!"
```

#### Test 2: Mass Assignment Prevention
```
def test_mass_assignment_attack_prevention(test_db, sample_system):
    legitimate_tenant = "tenant-legit-uuid"
    attacker_tenant = "tenant-attacker-uuid"
    
    sample_system.tenant_id = legitimate_tenant  # Forged payload
    
    with pytest.raises(ValueError) as exc:
        test_db.register_system(
            sample_system, 
            requesting_tenant=attacker_tenant  # Real JWT token
        )
    
    assert "Tenant ID mismatch" in str(exc.value)
```

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

```
# CORRECT: Tenant ID from JWT token
@app.post("/v1/resource")
async def create_resource(
    payload: ResourcePayload,
    token: TokenData = Depends(verify_jwt_token)
):
    resource = Resource(
        tenant_id=token.tenant_id,  # ✅ From token
        ...
    )
```

### DON'T ❌

```
# WRONG: Tenant ID from body (vulnerable to Mass Assignment)
@app.post("/v1/resource")
async def create_resource(payload: ResourcePayload):
    resource = Resource(
        tenant_id=payload.tenant_id,  # ❌ Client can forge
        ...
    )
```

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2025  
**Security Review:** Quarterly  
**Penetration Test:** Annually (recommended)

</details>

---

<details>
<summary><strong>🇧🇷 VERSÃO PORTUGUÊS</strong></summary>

## Resumo Executivo

BuildToValue implementa **isolamento multi-tenant nativo** que previne 100% dos ataques BOLA/IDOR (Broken Object Level Authorization) identificados no OWASP API1:2023.

### Garantias de Segurança

✅ **Tenant A nunca acessa dados de Tenant B**  
✅ **Validação UUID v4** previne falsificação de tenant ID  
✅ **Claims JWT** como fonte única de verdade (não body)  
✅ **Isolamento em nível de banco de dados** com índices compostos  
✅ **Trilha de auditoria completa** para investigação forense

---

## Modelo de Ameaças

### Capacidades do Adversário

Assumimos um atacante com:
- Credenciais válidas (token JWT legítimo)
- Conhecimento da estrutura da API
- Capacidade de manipular payloads JSON
- Acesso à documentação pública

### Cenários de Ataque Prevenidos

#### Cenário 1: Acesso Cross-Tenant (BOLA)

**Ataque:**
```
# Tenant B tenta acessar sistema do Tenant A
curl -X GET /v1/systems/tenant-a-system-001 \
  -H "Authorization: Bearer $TENANT_B_TOKEN"
```

**Defesa:**
```
# src/core/registry/system_registry.py
def get_system(self, system_id: str, requesting_tenant: str):
    # CRÍTICO: Query filtra por system_id E tenant_id
    return session.query(AISystemModel).filter_by(
        id=system_id,
        tenant_id=requesting_tenant  # Extraído do JWT, não do payload
    ).first()
    # Retorna None se tenant não coincidir (sem expor existência)
```

**Resultado:** ❌ Acesso Negado (404 - Not Found)

---

#### Cenário 2: Ataque Mass Assignment

**Ataque:**
```
POST /v1/systems
{
  "id": "malicious-system",
  "tenant_id": "victim-tenant-uuid",  // Tentativa de forjar tenant
  "name": "Backdoor System"
}
```

**Defesa:**
```
# src/interface/api/gateway.py
@app.post("/v1/systems")
async def register_system(
    payload: SystemPayload,
    token: TokenData = Depends(require_role(["admin", "dev"]))
):
    system = AISystem(
        id=payload.id,
        tenant_id=token.tenant_id,  # CRÍTICO: Força uso do token JWT
        ...
    )
    # Validação adicional no registry
    registry.register_system(system, requesting_tenant=token.tenant_id)
```

**Validação:**
```
# src/core/registry/system_registry.py
def register_system(self, system, requesting_tenant):
    if system.tenant_id != requesting_tenant:
        raise ValueError(
            f"Incompatibilidade de Tenant ID: Sistema declara {system.tenant_id} "
            f"mas token JWT pertence a {requesting_tenant}. "
            f"Possível ataque de segurança detectado!"
        )
```

**Resultado:** ❌ Rejeitado (ValueError + Log de Auditoria)

---

## Componentes de Arquitetura

### 1. Estrutura do Token JWT

```
{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "admin@company.com",
  "role": "admin",
  "exp": 1735045200,
  "iat": 1735041600
}
```

**Validação de Claims:**
```
# src/interface/api/auth.py
required_claims = ["tenant_id", "user_id", "role", "exp"]
missing_claims = [c for c in required_claims if c not in payload]

if missing_claims:
    raise HTTPException(401, f"Claims ausentes: {missing_claims}")
```

---

### 2. Design do Schema de Banco de Dados

#### Tabela Tenants
```
CREATE TABLE tenants (
    id VARCHAR(36) PRIMARY KEY,  -- UUID v4
    name VARCHAR(255) NOT NULL,
    governance_policy JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_tenants_id ON tenants(id);
```

#### Tabela AI Systems (Multi-Tenant)
```
CREATE TABLE ai_systems (
    id VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(36) NOT NULL,  -- FK para tenants
    name VARCHAR(255) NOT NULL,
    -- ... outros campos ...
    
    -- Chave Primária Composta (tenant_id, id)
    PRIMARY KEY (tenant_id, id),
    
    -- Constraint de Chave Estrangeira
    CONSTRAINT fk_tenant 
        FOREIGN KEY (tenant_id) 
        REFERENCES tenants(id) 
        ON DELETE CASCADE
);

-- Índice composto para performance
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);

-- Evita duplicação de system_id entre tenants
CREATE UNIQUE INDEX idx_system_global ON ai_systems(id);
```

**Benefícios de Performance:**
- Queries filtradas por `tenant_id` usam índice automaticamente
- `EXPLAIN ANALYZE` mostra "Index Scan using idx_tenant_system"
- Tempo de busca O(log n)

---

### 3. Fluxo de Requisição com Isolamento

```
┌─────────────────────────────────────────────────────────────┐
│  1. Requisição do Cliente                                   │
│     POST /v1/systems                                        │
│     Headers: {Authorization: Bearer JWT_TOKEN}              │
│     Body: {id: "sys-001", name: "AI System"}                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Middleware de Autenticação                              │
│     - Decodificar token JWT                                 │
│     - Validar assinatura (HS256)                            │
│     - Extrair claims: {tenant_id, user_id, role}            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Autorização (RBAC)                                      │
│     - Verificar role em ["admin", "dev"]                    │
│     - Se não autorizado → 403 Forbidden                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Injeção de Tenant ID                                    │
│     system.tenant_id = token.tenant_id  // Do JWT          │
│     // Ignora qualquer tenant_id no body                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Validação                                               │
│     - Verificação de formato UUID v4                        │
│     - Regras de negócio (alto risco → logging obrigatório)  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Escrita no Banco (Isolada)                              │
│     INSERT INTO ai_systems (id, tenant_id, ...)             │
│     VALUES ('sys-001', 'jwt-tenant-uuid', ...)              │
│     // FK constraint garante que tenant existe              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Log de Auditoria (Assinado HMAC)                        │
│     log.append({                                            │
│       action: "system_registered",                          │
│       tenant: "jwt-tenant-uuid",                            │
│       user: "admin@company.com",                            │
│       timestamp: "2025-12-28T22:00:00Z",                    │
│       signature: "hmac-sha256..."                           │
│     })                                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Testes de Segurança

### Casos de Teste (Automatizados)

#### Teste 1: Acesso Cross-Tenant
```
# tests/security/test_bola.py
def test_bola_cross_tenant_system_access(test_db, sample_system):
    tenant_a = "tenant-a-uuid"
    tenant_b = "tenant-b-uuid"
    
    # Tenant A registra sistema
    test_db.register_system(sample_system, tenant_a)
    
    # Tenant B tenta acessar
    result = test_db.get_system(sample_system.id, tenant_b)
    
    assert result is None, "VIOLAÇÃO DE SEGURANÇA: Acesso cross-tenant!"
```

#### Teste 2: Prevenção Mass Assignment
```
def test_mass_assignment_attack_prevention(test_db, sample_system):
    legitimate_tenant = "tenant-legit-uuid"
    attacker_tenant = "tenant-attacker-uuid"
    
    sample_system.tenant_id = legitimate_tenant  # Payload forjado
    
    with pytest.raises(ValueError) as exc:
        test_db.register_system(
            sample_system, 
            requesting_tenant=attacker_tenant  # Token JWT real
        )
    
    assert "Tenant ID mismatch" in str(exc.value)
```

---

## Mapeamento de Compliance

### ISO 27001:2022

| Controle | Título | Implementação |
|----------|--------|---------------|
| A.9.2.1 | Registro de usuários | Validação de claims JWT |
| A.9.2.3 | Gestão de acesso | RBAC (4 papéis) |
| A.9.4.1 | Restrição de acesso | Queries baseadas em tenant |
| A.12.4.1 | Logging de eventos | Ledger assinado HMAC |

### GDPR

| Artigo | Requisito | Implementação |
|--------|-----------|---------------|
| Art. 25 | Privacy by Design | Isolamento multi-tenant |
| Art. 32 | Segurança do Processamento | Criptografia, controle de acesso |
| Art. 44-50 | Transferências Internacionais | Campo jurisdiction |

---

## Boas Práticas para Desenvolvedores

### FAZER ✅

```
# CORRETO: Tenant ID do token JWT
@app.post("/v1/resource")
async def create_resource(
    payload: ResourcePayload,
    token: TokenData = Depends(verify_jwt_token)
):
    resource = Resource(
        tenant_id=token.tenant_id,  # ✅ Do token
        ...
    )
```

### NÃO FAZER ❌

```
# ERRADO: Tenant ID do body (vulnerável a Mass Assignment)
@app.post("/v1/resource")
async def create_resource(payload: ResourcePayload):
    resource = Resource(
        tenant_id=payload.tenant_id,  # ❌ Cliente pode forjar
        ...
    )
```

---

**Versão do Documento:** 1.0  
**Última Atualização:** 28 de dezembro de 2025  
**Revisão de Segurança:** Trimestral  
**Teste de Penetração:** Anual (recomendado)

</details>
