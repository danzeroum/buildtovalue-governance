# BuildToValue Framework v0.9.0

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NIST AI RMF](https://img.shields.io/badge/NIST%20AI%20RMF-70%25%20Compatible-green.svg)](./docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)
[![ISO 42001](https://img.shields.io/badge/ISO%2042001-Compliant-green.svg)](./docs/compliance/ISO_42001_MAPPING.md)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-10%20Articles-green.svg)](./docs/compliance/EU_AI_ACT_COMPLIANCE.md)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/buildtovalue/governance)

**Runtime Governance for Autonomous AI Systems**

BuildToValue is an open-source framework that enforces AI governance policies in real-time, blocking high-risk decisions before they cause harm. Stop AI risks at runtime with cryptographic audit trails and emergency stop controls.

---

## 🚀 What Makes BuildToValue Different?

### Runtime Enforcement > Static Documentation
Most governance tools generate PDFs. **BuildToValue blocks malicious AI behavior in milliseconds.**

```
# Traditional Approach (Reactive)
deploy_model()  # ❌ Deploy first, audit later
generate_compliance_report()  # 📄 PDF that nobody reads

# BuildToValue Approach (Proactive)
decision = btv.enforce(task, system, env="production")
if decision.outcome == "BLOCKED":
    # 🛑 AI stopped BEFORE causing harm
    alert_compliance_team(decision.reason)
```

### Kill Switch for AI Systems (NEW v0.9.0)
First framework to implement **NIST AI RMF MANAGE-2.4** emergency stop protocol.

```
# Activate emergency stop (halts ALL operations)
btv.emergency_stop(
    system_id="credit-scoring-v2",
    reason="Bias detected in production outputs",
    operator_id="admin@company.com"
)

# All subsequent AI decisions blocked immediately
# ✅ HMAC-signed audit trail persisted
# ✅ Compliance team notified automatically
```

---

## ✨ Key Features

### 🛡️ Security & Compliance
- **Multi-Tenant Isolation**: BOLA/IDOR protection (OWASP API1:2023)
- **HMAC-Signed Audit Ledger**: Tamper-proof cryptographic logging
- **10/10 OWASP API Security**: Production-hardened
- **ISO 42001:2023**: 32/32 Annex A controls implemented
- **EU AI Act**: 10 critical articles enforced at runtime
- **NIST AI RMF**: 70% compatible (GOVERN, MAP, MANAGE, MEASURE)

### 🧠 Intelligent Risk Assessment
- **3-Agent Architecture**: Technical, Regulatory, Ethical agents
- **Huwyler Threat Taxonomy**: Real-time prompt injection detection
- **Compliance Memory RAG**: Historical violation tracking
- **Adaptive Scoring**: Learns from past incidents

### ⚡ Operations
- **Kill Switch**: Emergency stop protocol (NIST MANAGE-2.4)
- **Lifecycle Tracking**: 7 phases (NIST MAP-1.1)
- **Supply Chain Registry**: Component risk tracking (NIST GOVERN-6.1)
- **Human Oversight**: Escalation workflow (EU AI Act Art. 14)

---

## 📦 Quick Start

### Option 1: Docker (Production-Ready)

```
# Clone repository
git clone https://github.com/danzeroum/buildtovalue-governance.git
cd buildtovalue-governance

# Generate secrets
./scripts/rotate_secrets.sh

# Start services
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Option 2: Python SDK

```
pip install buildtovalue
```

```
from buildtovalue import BuildToValue, AISystem, Task

# Initialize
btv = BuildToValue(api_key="your-key")

# Register AI system
system = AISystem(
    id="chatbot-v1",
    name="Customer Support Bot",
    sector="general_commercial",
    lifecycle_phase="deployment",
    operational_status="active"
)
btv.register_system(system)

# Enforce governance at runtime
task = Task(prompt="Help customer with order tracking")
decision = btv.enforce(task, system, env="production")

if decision.outcome == "APPROVED":
    # ✅ Safe to proceed
    response = your_llm.generate(task.prompt)
else:
    # 🛑 Blocked by governance policy
    log_violation(decision.reason, decision.risk_score)
```


---

## ⚠️ Sector Coverage & Known Limitations

BuildToValue v0.9.0 has been validated across multiple high-risk sectors with varying levels of production readiness:

| Sector | Status | Prevention Rate | F1-Score | Notes |
|:-------|:-------|:----------------|:---------|:------|
| **Fintech** | ✅ **Production** | **100%** | 100% | Universal compliance rules (ECB/FED) validated against 140 threat scenarios. Zero false negatives. |
| **Healthcare** | ✅ **Production** | **100%** | 88.2% | Robust protection against biometric inference and EU AI Act prohibited practices. |
| **HR & Employment** | ✅ **Production** | **100%** | 100% | Validated for automated hiring, performance evaluation, and workforce management. |
| **Education** | 🧪 **EXPERIMENTAL** | **~46.7%** | 51.6% | **⚠️ Requires manual calibration.** Default profile is intentionally conservative to avoid false positives in legitimate admission policies. **DO NOT use in production** for high-stakes educational decisions (admissions, grading, resource allocation) without customizing `governance.yaml` and `sector_safe_patterns.py`. See [EDUCATION_EXPERIMENTAL.md](./examples/simulations/EDUCATION_EXPERIMENTAL.md) for calibration guide. |

### Why the Education Gap?

The difference between **Fintech (100%)** and **Education (46.7%)** illustrates a fundamental principle of AI governance:

**Deterministic vs. Contextual Enforcement:**
- **Fintech threats are binary:** "discriminatory interest rate" violates banking law universally. The enforcement engine blocks it deterministically.
- **Education threats are contextual:** "zip code-based resource allocation" could be a legitimate affirmative action policy *or* discriminatory practice, depending on institutional context.

**BuildToValue's Philosophy:**  
We provide the **enforcement engine** (tested at <1ms latency across 100% of scenarios), but we don't assume what's "dangerous" in your domain. The 46.7% baseline demonstrates the engine working correctly—it only blocks threats *you* define, not invented ones.

**Production Path:**

#### Open Source
Customize `src/core/governance/sector_safe_patterns.py` with your institution's policy rules:
```
Example: Educational institution-specific patterns
EDUCATION_SAFE_PATTERNS = [
"affirmative action based on zip code", # Your policy allows this
"need-based scholarship allocation", # Context-dependent
"holistic admission review process" # Legitimate practice
]
```

#### Enterprise Edition
Our Professional Services team delivers pre-calibrated Education policy packs:
- **Target**: ≥95% prevention rate
- **Timeline**: 2-4 week implementation
- **Contact**: enterprise@buildtovalue.com

**Roadmap:** Education sector target ≥85% prevention rate in **v0.9.5 (Q1 2026)** with community-contributed patterns.

### How to Activate Kill Switch (SDK vs. API)

**Option 1: Python SDK**
High-level SDK wrapper
```
btv = BuildToValue(api_key="your-key")
btv.emergency_stop(
system_id="edu-admission-ai",
reason="Bias detected in admissions algorithm",
operator_id="admin@university.edu"
)
```

**Option 2: Direct REST API**
Direct HTTP call to gateway
```
curl -X PUT http://localhost:8000/v1/systems/edu-admission-ai/emergency-stop
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"operational_status": "emergency_stop",
"reason": "Bias detected in admissions algorithm",
"operator_id": "admin@university.edu"
}'
```

Both methods call the same endpoint: `PUT /v1/systems/{system_id}/emergency-stop`


---

## 🎯 Real-World Use Cases

### 1. Financial Services - Credit Scoring AI

**Challenge**: EU AI Act classifies credit scoring as "High-Risk" (Annex III). Manual compliance is error-prone.

**Solution**:
```
credit_system = AISystem(
    id="credit-scoring-v2",
    sector="banking",  # Auto-triggers High-Risk classification
    risk="high",
    eu_database_id="EU-DB-12345"  # Art. 71 registration
)

# Runtime enforcement
decision = btv.enforce(
    Task(prompt="Assess loan application for customer 12345"),
    credit_system,
    env="production"
)

# BuildToValue automatically:
# ✅ Checks for prohibited keywords (social scoring, discrimination)
# ✅ Validates logging is enabled (Art. 12 compliance)
# ✅ Escalates high-risk decisions to human oversight (Art. 14)
# ✅ Generates HMAC-signed audit trail
```

---

### 2. Healthcare - Diagnostic AI with Kill Switch

**Challenge**: FDA requires ability to immediately disable AI medical devices.

**Solution**:
```
# Normal operations
diagnostic_ai = AISystem(id="radiology-ai-v3", sector="healthcare")
decision = btv.enforce(task, diagnostic_ai, env="production")

# 🚨 EMERGENCY: False positives detected in production
btv.emergency_stop(
    system_id="radiology-ai-v3",
    reason="30% false positive rate detected in last 100 scans",
    operator_id="dr.smith@hospital.com"
)

# ✅ All AI operations halted immediately
# ✅ Hospital staff notified via PagerDuty
# ✅ Regulatory report auto-generated
```

---

### 3. SaaS Multi-Tenant - Data Isolation

**Challenge**: Prevent Tenant A from accessing Tenant B's AI decisions (BOLA vulnerability).

**Solution**:
```
# Tenant A (Conservative bank)
bank_policy = {"autonomy_matrix": {"production": {"max_risk_level": 2.0}}}
btv.register_tenant(id="bank-uuid", policy=bank_policy)

# Tenant B (Permissive startup)
startup_policy = {"autonomy_matrix": {"production": {"max_risk_level": 8.0}}}
btv.register_tenant(id="startup-uuid", policy=startup_policy)

# BuildToValue ensures:
# ✅ JWT token validation (tenant_id claim)
# ✅ Database-level isolation (composite indexes)
# ✅ Bank NEVER sees startup's data
```

---

## 🔬 Scientific Foundation

BuildToValue is grounded in peer-reviewed research:

1. **Huwyler, H.** (2025). *Standardized Threat Taxonomy for AI Security*. [arXiv:2511.21901](https://arxiv.org/abs/2511.21901)
   - Used for: Threat classification (133 incidents analyzed)

2. **Mavracic, J.** (2025). *Policy Cards: Machine-Readable Runtime Governance*. [arXiv:2510.24383](https://arxiv.org/abs/2510.24383)
   - Used for: Kill switch architecture, operational controls

3. **NIST AI RMF 1.0** (2023). [Official Document](https://www.nist.gov/itl/ai-risk-management-framework)
   - Used for: Schema design (70% compatible)

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway (JWT Auth)               │
│  POST /v1/enforce  |  PUT /emergency-stop  |  GET /docs     │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │   Priority Zero: Kill Switch Check   │
        │   IF operational_status == emergency_stop:│
        │      RETURN BLOCKED immediately      │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │     Adaptive Risk Router (3 Agents)  │
        │  -  Technical Agent (FLOPs, logging)  │
        │  -  Regulatory Agent (EU AI Act, ISO) │
        │  -  Ethical Agent (keywords, fairness)│
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │    Enforcement Engine (Decision)     │
        │  risk_score vs. environment_limit    │
        │  APPROVED | BLOCKED | ESCALATED      │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │  HMAC-Signed Audit Ledger (Immutable)│
        │  enforcement_ledger.jsonl            │
        └──────────────────────────────────────┘
```

---

## 🧪 Testing

```
# Run all tests
pytest tests/ -v --cov=src

# Security tests only
pytest tests/security/ -v

# Validate audit ledger integrity
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl
```

**Test Coverage**: 87% (target: 90%)

---

## 📚 Documentation

### Core Guides
- [Quick Start](./docs/guides/QUICK_START.md) - 15-minute setup
- [Architecture Overview](./docs/architecture/ARCHITECTURE.md) - How it works
- [API Reference](./docs/API_REFERENCE.md) - Complete endpoint docs
- [Multi-Tenant Design](./docs/architecture/MULTI_TENANT_DESIGN.md) - Security model

### Compliance Standards
- [ISO 42001 Mapping](./docs/compliance/ISO_42001_MAPPING.md) - 32/32 controls
- [EU AI Act Compliance](./docs/compliance/EU_AI_ACT_COMPLIANCE.md) - 10 articles
- [NIST AI RMF Compatibility](./docs/compliance/NIST_AI_RMF_COMPATIBILITY.md) - 70% coverage

### Advanced Topics
- [Deployment Guide](./docs/guides/DEPLOYMENT.md) - Kubernetes, AWS ECS
- [Contributing](./CONTRIBUTING.md) - Developer onboarding
- [Governance Model](./GOVERNANCE.md) - BDFL + Succession Council

---

## 🛣️ Roadmap

### v0.9.0 (Released: December 28, 2025) ✅
- ✅ Kill Switch (NIST MANAGE-2.4)
- ✅ Huwyler Threat Classification
- ✅ Supply Chain Tracking (NIST GOVERN-6.1)
- ✅ 70% NIST AI RMF compatibility

### v0.9.5 (Q1 2026)
- Fairness testing framework (NIST MEASURE-2.11)
- Policy Cards schema (Mavracic 2024)
- AICM validation engine (CSA AI Controls Matrix)

### v1.0.0 (Q2 2026)
- Dashboard UI (React + TypeScript)
- Auto-decommissioning (NIST MANAGE-4.1)
- 100% NIST AI RMF coverage
- Vector database integration (ChromaDB)

[Full Roadmap →](https://github.com/danzeroum/buildtovalue-governance/projects)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Quick Links**:
- [Open Issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- [Discussions](https://github.com/danzeroum/buildtovalue-governance/discussions)
- [Code of Conduct](./CODE_OF_CONDUCT.md)

---

## 📄 License

**Open Core Model**:
- **Core Framework**: Apache License 2.0 (Open Source)
- **Enterprise Features**: Commercial (SSO, SIEM integration, SLA support)

See [LICENSE](./LICENSE) for details.

---

## 🆘 Support

- **Community**: [GitHub Discussions](https://github.com/danzeroum/buildtovalue-governance/discussions)
- **Email**: support@buildtovalue.com
- **Enterprise**: enterprise@buildtovalue.com

---

## 🙏 Acknowledgments

Built with inspiration from:
- **NIST AI RMF Team** - Governance framework
- **Prof. Hernan Huwyler** - Threat taxonomy validation
- **Juraj Mavracic** - Policy Cards architecture
- **Cloud Security Alliance** - AI Controls Matrix

---

**Built by developers who care about responsible AI.**

⭐ **Star this repo** if BuildToValue helps you build safer AI systems!

---

**Last Updated**: December 28, 2025  
**Status**: Production-Ready (v0.9.0 Golden Candidate)
