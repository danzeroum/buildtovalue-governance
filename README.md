
# 🛡️ BuildToValue Framework

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![ISO 42001:2023](https://img.shields.io/badge/ISO%2042001-Compliant-green.svg)](docs/compliance/ISO_42001_MAPPING.md)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Ready-green.svg)](docs/compliance/EU_AI_ACT_COMPLIANCE.md)
[![NIST AI RMF](https://img.shields.io/badge/NIST%20AI%20RMF-70%25%20Compatible-brightgreen.svg)](docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/buildtovalue/btv-framework)

**O primeiro middleware open source de governança de IA com conformidade ISO 42001, EU AI Act e NIST AI RMF integrada.**

BuildToValue é uma plataforma de runtime enforcement para sistemas de Inteligência Artificial que implementa controles automatizados de risco, auditoria criptográfica, isolamento multi-tenant enterprise-grade e **kill switch para operações críticas**.

---

## 🎯 **Por que BuildToValue?**


# Antes (sem governança)
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": user_prompt}]
)

# ⚠️ Sem controle de risco, sem auditoria, sem compliance

```
# Depois (com BuildToValue)
decision = btv_engine.enforce(
    task=Task(title=user_prompt),
    system=registered_ai_system,
    env="production"
)
if decision["decision"] == "ALLOWED":
    response = openai.chat.completions.create(...)

# ✅ Risco avaliado, decisão auditada, ISO 42001 compliant
```

### **Problema que Resolvemos**

Empresas que usam IA enfrentam 3 desafios críticos:

1. **Conformidade Regulatória**: EU AI Act exige rastreabilidade de decisões (Art. 12), avaliação de risco (Art. 9) e supervisão humana (Art. 14)
2. **Isolamento Multi-Tenant**: SaaS AI precisa garantir que dados do Cliente A nunca vazem para Cliente B
3. **Auditoria Imutável**: Reguladores exigem logs tamper-proof (ISO 42001 A.7.5)

**BuildToValue resolve os 3 simultaneamente.**

---

## 🚀 **What's New in v0.9.0**

BuildToValue v0.9.0 introduces **enterprise-grade governance features** aligned with international AI standards:

### 🔥 Kill Switch (Emergency Stop)
One-click system shutdown for safety-critical situations:
```
curl -X PUT /v1/systems/my-system/emergency-stop \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"operational_status": "emergency_stop", "reason": "Bias detected"}'
```

**Compliance:** NIST AI RMF MANAGE-2.4, Policy Cards emergency controls, EU AI Act Art. 14

### 📊 NIST AI RMF 1.0 Compatible (70%)
First open-source framework with **runtime enforcement** of NIST AI RMF functions:
- ✅ **GOVERN:** Third-party component registry (GOVERN-6.1)
- ✅ **MAP:** Lifecycle phase tracking (MAP-1.2), context documentation (MAP-1.1)
- ✅ **MEASURE:** Environmental impact fields (MEASURE-2.12)
- ✅ **MANAGE:** Operational controls + kill switch (MANAGE-2.4)

**Evidence:** [NIST Compliance Report](./docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)

### 🎯 Scientifically Validated Threat Taxonomy
Threat classification based on **Huwyler (2025) - Standardized Threat Taxonomy**:
- 📊 **Validated against 133 real-world AI incidents** (2019-2025)
- 🎯 **88% coverage** with MISUSE (61%) + UNRELIABLE (27%) categories
- 🔬 **Scientific reference:** [arXiv:2511.21901v1](https://arxiv.org/abs/2511.21901)

```
# Automatic threat classification in enforcement logs
{
  "decision": "BLOCKED",
  "threat_classification": {
    "primary_threat": "misuse",
    "detected_vectors": ["misuse", "privacy"],
    "taxonomy_version": "Huwyler 2025",
    "confidence_scores": {"misuse": 0.85}
  }
}
```

### 🔗 Policy Cards Architecture Ready
Schema prepared for **Policy Cards (Mavracic 2025)** runtime governance:
- 🔗 `policy_card_uri` field for machine-readable policies
- ✅ Operational status controls (5 states: active, degraded, maintenance, suspended, emergency_stop)
- 📋 Full lifecycle tracking (7 phases: design → retirement)

**Reference:** [Policy Cards Paper (arXiv:2510.24383)](https://arxiv.org/abs/2510.24383)

### 📄 Compliance Report Generator
One-command compliance documentation:
```
curl -X GET /v1/systems/my-system/compliance-report \
  -H "Authorization: Bearer $TOKEN"
```

**Output includes:**
- NIST AI RMF assessment (70% compliance)
- EU AI Act high-risk status
- Supply chain risk analysis (NIST GAP-1)
- Actionable recommendations

---

## 📊 Framework Comparison

| Feature | Competitor A | Competitor B | **BuildToValue v0.9.0** |
|---------|--------------|--------------|------------------------|
| **NIST AI RMF** | Documentation only | Checklist tool | **70% runtime enforcement** |
| **Kill Switch** | Manual process | API call | **1-click emergency stop** |
| **Threat Taxonomy** | Ad-hoc categories | MITRE ATLAS only | **Huwyler (133 incidents validated)** |
| **Lifecycle Tracking** | Not supported | Custom fields | **7 phases (NIST-aligned)** |
| **Supply Chain** | Not supported | Manual spreadsheet | **Automated third-party registry** |
| **Carbon Tracking** | Not supported | Not supported | **EU AI Act Annex IV compliant** |
| **License** | Proprietary | Proprietary | **Open Source (Apache 2.0)** |


---

## 📦 What's Included (Open Core Model)

BuildToValue uses an **Open Core** licensing model. We believe security and compliance features should never be paywalled, while management tools enable enterprise scale.

| Feature | 🟢 Open Source (Apache 2.0) | 💼 Enterprise Edition |
| :--- | :---: | :---: |
| **Core Governance Engine** | ✅ Included | ✅ Included |
| **Real-time Enforcement** | ✅ Included | ✅ Included |
| **Kill Switch (Emergency Stop)** | ✅ Included | ✅ Included |
| **Huwyler Threat Taxonomy** | ✅ Included | ✅ Included |
| **NIST AI RMF + EU AI Act Schema** | ✅ Included | ✅ Included |
| **HMAC-Signed Audit Logs** | ✅ Included | ✅ Included |
| **Multi-Tenant Isolation** | ✅ Included | ✅ Included |
| **Python SDK & CLI** | ✅ Included | ✅ Included |
| **Supply Chain Registry** | ✅ Included | ✅ Included |
| **Docker Compose Setup** | ✅ Included | ✅ Included |
| **Web Dashboard (GUI)** | ❌ CLI/API Only | ✅ React UI |
| **SSO / SAML (Okta/Azure AD)** | ❌ Not Included | ✅ Native Connectors |
| **SIEM Integrations** | ❌ Raw JSON Logs | ✅ Splunk/Datadog/ELK |
| **PDF Compliance Reports** | ❌ JSON/HTML Only | ✅ Auditor-Ready PDFs |
| **Visual Policy Editor** | ❌ YAML Files | ✅ No-Code UI |
| **Team Management & Approvals** | ❌ Not Included | ✅ Workflow Engine |
| **SLA Support** | Community (Best Effort) | Priority 24/7 |

### Why This Split?

**Security is not a paywall.** Every feature required to secure AI systems (kill switch, threat detection, cryptographic logs) is open source. Enterprise adds *convenience* (dashboards, SSO) and *management* (approvals, teams) for organizations at scale.

**See full details:** [PRODUCT_SCOPE.md](./PRODUCT_SCOPE.md)

> **🎯 Enterprise Design Partners:** We are currently accepting 5 design partners for the Enterprise beta (Q1 2026).  
> **Benefits:** Early access, 50% discount year 1, $10k consulting credits, roadmap influence.  
> [Apply now →](mailto:enterprise@buildtovalue.com)

---

***


---

## 🚀 **Quick Start (5 minutos)**

### **Opção 1: Docker (Recomendado)**

```
# Clone o repositório
git clone https://github.com/buildtovalue/btv-framework.git
cd btv-framework

# Gere secrets
./scripts/rotate_secrets.sh

# Suba a stack
docker-compose up -d

# Gere token de admin
python scripts/generate_token.py --role admin --tenant global_admin --days 90

# Teste a API
curl http://localhost:8000/health
```

### **Opção 2: Instalação Local**

```
# Instale dependências
pip install -r requirements.txt

# Configure ambiente
cp .env.example .env
export JWT_SECRET=$(openssl rand -hex 32)
export HMAC_KEY=$(openssl rand -hex 32)

# Inicie a API
uvicorn src.interface.api.gateway:app --reload

# Acesse: http://localhost:8000/docs
```

### **Quick Start (v0.9.0 Schema)**

```
from src.domain.entities import AISystem, ThirdPartyComponent
from src.domain.enums import AIPhase, OperationalStatus
from src.core.governance.enforcement import EnforcementEngine

# Register AI system with v0.9.0 schema
system = AISystem(
    id="credit-scoring-v2",
    tenant_id="acme-bank",
    name="Credit Risk Assessment AI",
    
    # NEW v0.9.0: NIST MAP fields
    intended_purpose="Assess loan application risk",
    prohibited_domains=["social_scoring", "political_profiling"],
    lifecycle_phase=AIPhase.DEPLOYMENT,
    operational_status=OperationalStatus.ACTIVE,
    
    # NEW v0.9.0: Supply chain tracking
    external_dependencies=[
        ThirdPartyComponent(
            name="scikit-learn",
            version="1.3.0",
            vendor="Scikit-Learn",
            license_type="BSD-3-Clause",
            risk_level="LOW"
        )
    ],
    
    # NEW v0.9.0: Environmental impact
    estimated_carbon_kg_co2=120.5,
    energy_consumption_kwh=450.3
)

# Activate kill switch if needed
system.operational_status = OperationalStatus.EMERGENCY_STOP

# All subsequent tasks will be BLOCKED
engine = EnforcementEngine()
decision = engine.enforce(task, system)
# {"outcome": "BLOCKED", "reason": "KILL_SWITCH_ACTIVE", "risk_score": 10.0}
```

---

## 📚 **Documentação**

### **Core Documentation**
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Primeiros passos
- **[Architecture Overview](docs/architecture/ARCHITECTURE.md)** - Como funciona
- **[Multi-Tenant Design](docs/architecture/MULTI_TENANT_DESIGN.md)** - Isolamento de dados
- **[API Reference](docs/API_REFERENCE.md)** - Referência completa da API

### **Compliance & Standards (v0.9.0)**
- **[ISO 42001 Compliance](docs/compliance/ISO_42001_MAPPING.md)** - Mapeamento de controles
- **[EU AI Act Compliance](docs/compliance/EU_AI_ACT_COMPLIANCE.md)** - Artigos implementados
- **[NIST AI RMF Compatibility](docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)** - 70% compliance evidence ✨ **NEW**
- **[Framework Readiness](docs/compliance/FRAMEWORK_READINESS.md)** - Policy Cards, AICM integration ✨ **NEW**

---

## 🏗️ **Arquitetura**

```
┌─────────────────────────────────────────────────────────────────┐
│                    BuildToValue Framework v0.9.0                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Adaptive   │──▶│   Runtime    │──▶│ HMAC-Signed  │         │
│  │ Risk Router  │  │ Enforcement  │  │  Audit Log   │         │
│  │  (3 Agents)  │  │    Engine    │  │ (Immutable)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                 │                   │                 │
│         ▼                 ▼                   ▼                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │    Multi-Tenant Registry (SQL Injection              │      │
│  │    Protected, UUID Validated, RBAC Enforced)         │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  JWT Auth +  │  │    Human     │  │  Compliance  │         │
│  │     RBAC     │  │  Oversight   │  │  Memory RAG  │         │
│  │  (4 Roles)   │  │  Dashboard   │  │ (Historical) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ NEW v0.9.0: Kill Switch + Threat Classifier          │      │
│  │ -  Emergency Stop (NIST MANAGE-2.4)                   │      │
│  │ -  Huwyler Taxonomy (133 incidents validated)         │      │
│  │ -  Supply Chain Registry (NIST GOVERN-6.1)            │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Camadas de Governança (Merge Conservador)**

1. **Global Policy** (`governance.yaml`) - Leis não negociáveis (EU AI Act Art. 5)
2. **Tenant Policy** (Empresa) - Regras da organização
3. **System Policy** (Projeto) - Configurações específicas

**Regra de Ouro**: A política mais restritiva sempre vence.

---

## 🔐 **Segurança Enterprise-Grade**

### **Vulnerabilidades Corrigidas (OWASP API Top 10 2023)**

| Vulnerabilidade | OWASP | Proteção BuildToValue |
|-----------------|-------|------------------------|
| SQL Injection | API8 | SQLAlchemy ORM + parametrized queries |
| BOLA/IDOR | API1 | `requesting_tenant` validation em todas as queries |
| Auth Bypass | API2 | JWT com expiração + claims validation |
| Mass Assignment | API6 | `tenant_id` extraído do token (não do payload) |
| Privilege Escalation | API5 | `_validate_tenant_policy()` hardening |
| JSON Injection | API8 | Pydantic schema validation (whitelist) |
| Ledger Tampering | API9 | HMAC-SHA256 digital signatures |
| Path Traversal | API3 | Absolute path + ".." sanitization |
| DoS | API4 | Rate limiting (SlowAPI + Nginx) |
| Timing Attack | API7 | `hmac.compare_digest()` constant-time |

### **Certificações de Conformidade**

- ✅ **ISO/IEC 42001:2023** - AI Management System (32/32 controles Annex A)
- ✅ **EU AI Act (2024/1689)** - Art. 5, 6, 9, 11, 12, 14, 15, 27, 51, 71
- ✅ **NIST AI RMF 1.0** - 70% Compatible (GOVERN, MAP, MEASURE, MANAGE) ✨ **NEW**
- ✅ **ISO/IEC 27001:2022** - Annex A.14 (System Security)
- ✅ **GDPR** - Art. 25 (Privacy by Design), Art. 32 (Security)

**[Veja o mapeamento completo de compliance →](docs/compliance/ISO_42001_MAPPING.md)**

---

## 💡 **Casos de Uso**

### **1. SaaS Multi-Tenant com Isolamento de Dados**

```
# Tenant A (Banco) registra sistema com política conservadora
btv_api.register_tenant(
    id="bank-uuid",
    name="Banco Seguro S.A.",
    policy={
        "autonomy_matrix": {
            "production": {"max_risk_level": 2.0}  # Muito restritivo
        }
    }
)

# Tenant B (Agência) registra com política menos restritiva
btv_api.register_tenant(
    id="agency-uuid",
    name="Agência Criativa LTDA",
    policy={
        "autonomy_matrix": {
            "production": {"max_risk_level": 5.0}  # Mais permissivo
        }
    }
)

# BuildToValue garante: Banco NUNCA verá dados da Agência
```

### **2. Conformidade Automática com EU AI Act**

```
# Sistema classificado como Alto Risco (Art. 6)
high_risk_system = AISystem(
    id="credit-scoring-ai",
    tenant_id="bank-uuid",
    sector=AISector.BANKING,
    risk_classification=EUComplianceRisk.HIGH,
    eu_database_registration_id="EU-DB-12345"  # Art. 71
)

# BuildToValue automaticamente:
# ✅ Exige supervisão humana (Art. 14)
# ✅ Registra todas as decisões (Art. 12)
# ✅ Avalia impacto em indivíduos (Art. 27)
# ✅ Bloqueia práticas proibidas (Art. 5)
```

### **3. Auditoria Criptográfica Imutável**

```
# Valida integridade do ledger
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

# Output:
# ✅ 15,432 entradas analisadas
# ✅ 100% das assinaturas HMAC válidas
# ✅ Ledger íntegro - Nenhuma adulteração detectada
```

### **4. Kill Switch para Sistemas de Alto Risco (NEW v0.9.0)**

```
# Ativar kill switch em produção
system.operational_status = OperationalStatus.EMERGENCY_STOP

# Todas as decisões subsequentes serão bloqueadas
decision = engine.enforce(task, system)
# {"outcome": "BLOCKED", "reason": "KILL_SWITCH_ACTIVE", "risk_score": 10.0}

# Auditores veem no log:
# 🔴 EMERGENCY_STOP activated for system credit-scoring-v2
# 🔴 Operator: admin@bank.com
# 🔴 Reason: Detected bias in production outputs
```

---

## 🎯 Use Cases by Stakeholder

### For CISOs
> "BTV v0.9.0 implements the **NIST MANAGE function in code**, not PDFs. Your auditors will see `OperationalStatus.EMERGENCY_STOP` in logs, not governance theater."

### For AI/ML Teams
> "Track models across **7 lifecycle phases** (NIST-aligned), not generic 'dev/prod'. When regulators ask 'Where's your validation evidence?', point to `AIPhase.VALIDATION` logs."

### For Compliance Officers
> "We mapped **243 CSA AICM controls** to metadata fields. Your ISO 42001 audit? **Pre-populated compliance report in 1 command**."

---

## 🔬 Scientific Validation

BuildToValue v0.9.0 is grounded in peer-reviewed research:

1. **Huwyler, H. (2025).** "Standardized Threat Taxonomy for AI Security, Governance, and Regulatory Compliance."  
   *arXiv:2511.21901v1* - [Read Paper](https://arxiv.org/abs/2511.21901)  
   → **Used for:** Threat classification (133 incidents analyzed)

2. **Mavracic, J. (2025).** "Policy Cards: Machine-Readable Runtime Governance for Autonomous AI Agents."  
   *arXiv:2510.24383v1* - [Read Paper](https://arxiv.org/abs/2510.24383)  
   → **Used for:** Architecture design (kill switch, operational controls)

3. **NIST AI Risk Management Framework 1.0 (2023).**  
   *NIST AI 100-1* - [Official Document](https://doi.org/10.6028/NIST.AI.100-1)  
   → **Used for:** Schema design (70% compatible)

---

## 🧪 **Testes**

```
# Testes de segurança
pytest tests/security/test_bola.py -v
pytest tests/security/test_injection.py -v

# Testes unitários
pytest tests/unit/ --cov=src --cov-report=html

# Testes de integração
pytest tests/integration/test_e2e.py

# NEW v0.9.0: Testes de threat classifier e kill switch
pytest tests/test_threat_classifier.py -v
pytest tests/test_kill_switch.py -v
```

**Cobertura Atual**: 87% (objetivo: 90%)

---

## 🤝 **Contribuindo**

BuildToValue é um projeto comunitário **open-source** (Apache 2.0). Aceitamos contribuições que melhoram a governança de IA:

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- 💡 **Feature requests:** Use "enhancement" label
- 📖 **Documentation:** Help us improve compliance guides
- 🔬 **Research:** Cite new papers for framework updates

**Código de Conduta**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## 📊 **Roadmap**

### **v0.9.0 (Atual - Dezembro 2025)** ✅
- ✅ Kill Switch (Emergency Stop) - NIST MANAGE-2.4
- ✅ NIST AI RMF 1.0 (70% Compatible)
- ✅ Huwyler Threat Taxonomy (133 incidents validated)
- ✅ Supply Chain Registry (NIST GOVERN-6.1)
- ✅ Environmental Impact Tracking (EU AI Act Annex IV)
- ✅ Policy Cards Architecture Ready
- ✅ Compliance Report Generator

### **v0.9.5 (Q1 2026)** 🚧
- [ ] Automated fairness testing (NIST MEASURE-2.11)
- [ ] Policy Card JSON Schema validator
- [ ] Workforce diversity tracking (NIST GAP-12)
- [ ] AICM control automated validation

### **v1.0 (Q2 2026)** 📅
- [ ] Policy Card runtime enforcement
- [ ] User feedback API (NIST MEASURE-3.3)
- [ ] Decommissioning automation (NIST MANAGE-4.1)
- [ ] Dashboard Web UI (React + TypeScript)
- [ ] MLOps integrations (MLflow, Kubeflow)

### **v1.5 (Q3 2026)** 🔮
- [ ] Predictive compliance scoring (ML-based)
- [ ] Multi-cloud deployment (AWS, Azure, GCP)
- [ ] SOC 2 Type II certification
- [ ] API Gateway plugin (Kong, Nginx)

**[Veja o roadmap completo →](https://github.com/danzeroum/buildtovalue-governance/projects)**

---

## 📜 **Licença**

BuildToValue é licenciado sob [Apache License 2.0](LICENSE).

**Estratégia Open Core**:
- ✅ **Open Source**: Todo o código core (multi-tenant, enforcement, compliance, kill switch)
- 💼 **Enterprise Edition**: SSO, SIEM integrations, SLA 24/7, Dashboard avançado

**[Contate para Enterprise Edition →](mailto:enterprise@buildtovalue.com)**

**Compliance Claims:**  
All framework compatibility statements (NIST, EU AI Act) are self-assessed and verifiable through our public codebase. For official certifications, engage an accredited third-party auditor.

---

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=buildtovalue/btv-framework&type=Date)](https://star-history.com/#buildtovalue/btv-framework&Date)

---

## 📞 **Suporte**

- **Documentação**: https://docs.buildtovalue.ai
- **Issues**: https://github.com/danzeroum/buildtovalue-governance/issues
- **Discord**: https://discord.gg/buildtovalue
- **Email**: support@buildtovalue.com

---

## 🙏 **Agradecimentos**

BuildToValue é construído sobre os ombros de gigantes:

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM robusto
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [python-jose](https://python-jose.readthedocs.io/) - JWT implementation

**Research Acknowledgments (v0.9.0):**
- **NIST AI RMF Team** - For open governance framework
- **Prof. Hernan Huwyler** - For validated threat taxonomy
- **Juraj Mavracic** - For Policy Cards architecture inspiration
- **Cloud Security Alliance** - For AI Controls Matrix

---

<div align="center">

**Construído com ❤️ por desenvolvedores que se importam com IA responsável**

[Website](https://buildtovalue.com) • [Docs](https://docs.buildtovalue.ai) • [Blog](https://blog.buildtovalue.ai)

**Version:** 0.9.0  
**Last Updated:** December 26, 2025  
**Maintainer:** BuildToValue Core Team

</div>
```
---

## Test Status

[![Tests](https://img.shields.io/badge/tests-61%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-89.74%25-brightgreen)](htmlcov/index.html)
[![Security](https://img.shields.io/badge/OWASP-API%20Top%2010-blue)](tests/security/)
[![Skipped](https://img.shields.io/badge/skipped-7%20(v0.9.5)-yellow)](tests/TEST_STATUS_v0.9.0.md)
