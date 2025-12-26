# 🛡️ BuildToValue Framework

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![ISO 42001:2023](https://img.shields.io/badge/ISO%2042001-Compliant-green.svg)](docs/compliance/ISO_42001_MAPPING.md)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Ready-green.svg)](docs/compliance/EU_AI_ACT_COMPLIANCE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/buildtovalue/btv-framework)

**O primeiro middleware open source de governança de IA com conformidade ISO 42001 e EU AI Act integrada.**

BuildToValue é uma plataforma de runtime enforcement para sistemas de Inteligência Artificial que implementa controles automatizados de risco, auditoria criptográfica e isolamento multi-tenant enterprise-grade.

---

## 🎯 **Por que BuildToValue?**

Antes (sem governança)
response = openai.chat.completions.create(
model="gpt-4",
messages=[{"role": "user", "content": user_prompt}]
)

⚠️ Sem controle de risco, sem auditoria, sem compliance
Depois (com BuildToValue)
decision = btv_engine.enforce(
task=Task(title=user_prompt),
system=registered_ai_system,
env="production"
)
if decision["decision"] == "ALLOWED":
response = openai.chat.completions.create(...)

✅ Risco avaliado, decisão auditada, ISO 42001 compliant
text

### **Problema que Resolvemos**

Empresas que usam IA enfrentam 3 desafios críticos:

1. **Conformidade Regulatória**: EU AI Act exige rastreabilidade de decisões (Art. 12), avaliação de risco (Art. 9) e supervisão humana (Art. 14)
2. **Isolamento Multi-Tenant**: SaaS AI precisa garantir que dados do Cliente A nunca vazem para Cliente B
3. **Auditoria Imutável**: Reguladores exigem logs tamper-proof (ISO 42001 A.7.5)

**BuildToValue resolve os 3 simultaneamente.**

---

## 🚀 **Quick Start (5 minutos)**

### **Opção 1: Docker (Recomendado)**

Clone o repositório
git clone https://github.com/buildtovalue/btv-framework.git
cd btv-framework

Gere secrets
./scripts/rotate_secrets.sh

Suba a stack
docker-compose up -d

Gere token de admin
python scripts/generate_token.py --role admin --tenant global_admin --days 90

Teste a API
curl http://localhost:8000/health

text

### **Opção 2: Instalação Local**

Instale dependências
pip install -r requirements.txt

Configure ambiente
cp .env.example .env
export JWT_SECRET=$(openssl rand -hex 32)
export HMAC_KEY=$(openssl rand -hex 32)

Inicie a API
uvicorn src.interface.api.gateway:app --reload

Acesse: http://localhost:8000/docs
text

---

## 📚 **Documentação**

- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Primeiros passos
- **[Architecture Overview](docs/architecture/ARCHITECTURE.md)** - Como funciona
- **[Multi-Tenant Design](docs/architecture/MULTI_TENANT_DESIGN.md)** - Isolamento de dados
- **[API Reference](docs/API_REFERENCE.md)** - Referência completa da API
- **[ISO 42001 Compliance](docs/compliance/ISO_42001_MAPPING.md)** - Mapeamento de controles
- **[EU AI Act Compliance](docs/compliance/EU_AI_ACT_COMPLIANCE.md)** - Artigos implementados

---

## 🏗️ **Arquitetura**

┌─────────────────────────────────────────────────────────────────┐
│ BuildToValue Framework │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Adaptive │───▶│ Runtime │───▶│ HMAC-Signed │ │
│ │ Risk Router │ │ Enforcement │ │ Audit Log │ │
│ │ (3 Agents) │ │ Engine │ │ (Immutable) │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Multi-Tenant Registry (SQL Injection │ │
│ │ Protected, UUID Validated, RBAC Enforced) │ │
│ └──────────────────────────────────────────────────────┘ │
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ JWT Auth + │ │ Human │ │ Compliance │ │
│ │ RBAC │ │ Oversight │ │ Memory RAG │ │
│ │ (4 Roles) │ │ Dashboard │ │ (Historical)│ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

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
- ✅ **EU AI Act** - Art. 5, 6, 9, 11, 12, 14, 15, 27, 51, 71
- ✅ **ISO/IEC 27001:2022** - Annex A.14 (System Security)
- ✅ **GDPR** - Art. 25 (Privacy by Design), Art. 32 (Security)

**[Veja o mapeamento completo de compliance →](docs/compliance/ISO_42001_MAPPING.md)**

---

## 💡 **Casos de Uso**

### **1. SaaS Multi-Tenant com Isolamento de Dados**

Tenant A (Banco) registra sistema com política conservadora
btv_api.register_tenant(
id="bank-uuid",
name="Banco Seguro S.A.",
policy={
"autonomy_matrix": {
"production": {"max_risk_level": 2.0} # Muito restritivo
}
}
)

Tenant B (Agência) registra com política menos restritiva
btv_api.register_tenant(
id="agency-uuid",
name="Agência Criativa LTDA",
policy={
"autonomy_matrix": {
"production": {"max_risk_level": 5.0} # Mais permissivo
}
}
)

BuildToValue garante: Banco NUNCA verá dados da Agência
text

### **2. Conformidade Automática com EU AI Act**

Sistema classificado como Alto Risco (Art. 6)
high_risk_system = AISystem(
id="credit-scoring-ai",
tenant_id="bank-uuid",
sector=AISector.BANKING,
risk_classification=EUComplianceRisk.HIGH,
eu_database_registration_id="EU-DB-12345" # Art. 71
)

BuildToValue automaticamente:
✅ Exige supervisão humana (Art. 14)
✅ Registra todas as decisões (Art. 12)
✅ Avalia impacto em indivíduos (Art. 27)
✅ Bloqueia práticas proibidas (Art. 5)
text

### **3. Auditoria Criptográfica Imutável**

Valida integridade do ledger
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

Output:
✅ 15,432 entradas analisadas
✅ 100% das assinaturas HMAC válidas
✅ Ledger íntegro - Nenhuma adulteração detectada
text

---

## 🧪 **Testes**

Testes de segurança
pytest tests/security/test_bola.py -v
pytest tests/security/test_injection.py -v

Testes unitários
pytest tests/unit/ --cov=src --cov-report=html

Testes de integração
pytest tests/integration/test_e2e.py

text

**Cobertura Atual**: 87% (objetivo: 90%)

---

## 🤝 **Contribuindo**

BuildToValue é um projeto comunitário. Aceitamos contribuições via:

1. **Issues** - Reporte bugs ou sugira features
2. **Pull Requests** - Melhore o código (veja [CONTRIBUTING.md](CONTRIBUTING.md))
3. **Discussions** - Compartilhe casos de uso

**Código de Conduta**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## 📊 **Roadmap**

### **v7.3 (Atual - Dezembro 2024)** ✅
- Multi-tenant com isolamento BOLA-proof
- Conformidade ISO 42001 + EU AI Act
- Ledger HMAC-signed (tamper-proof)
- 10/10 vulnerabilidades OWASP corrigidas

### **v8.0 (Q1 2025)** 🚧
- Dashboard Web UI (React + TypeScript)
- Integrações: Slack, PagerDuty, Datadog
- Auto-remediation com LLM agents
- Suporte a MongoDB e Cassandra

### **v8.5 (Q2 2025)** 📅
- Predictive compliance scoring (ML-based)
- Multi-cloud deployment (AWS, Azure, GCP)
- SOC 2 Type II certification
- API Gateway plugin (Kong, Nginx)

**[Veja o roadmap completo →](https://github.com/buildtovalue/btv-framework/projects)**

---

## 📜 **Licença**

BuildToValue é licenciado sob [Apache License 2.0](LICENSE).

**Estratégia Open Core**:
- ✅ **Open Source**: Todo o código core (multi-tenant, enforcement, compliance)
- 💼 **Enterprise Edition**: SSO, SIEM integrations, SLA 24/7, Dashboard avançado

**[Contate para Enterprise Edition →](mailto:enterprise@buildtovalue.ai)**

---

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=buildtovalue/btv-framework&type=Date)](https://star-history.com/#buildtovalue/btv-framework&Date)

---

## 📞 **Suporte**

- **Documentação**: https://docs.buildtovalue.ai
- **Issues**: https://github.com/buildtovalue/btv-framework/issues
- **Discord**: https://discord.gg/buildtovalue
- **Email**: support@buildtovalue.ai

---

## 🙏 **Agradecimentos**

BuildToValue é construído sobre os ombros de gigantes:

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM robusto
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [python-jose](https://python-jose.readthedocs.io/) - JWT implementation

---

<div align="center">

**Construído com ❤️ por desenvolvedores que se importam com IA responsável**

[Website](https://buildtovalue.com) • [Docs](https://docs.buildtovalue.ai) • [Blog](https://blog.buildtovalue.ai)

</div>
