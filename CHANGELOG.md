# Changelog

All notable changes to BuildToValue Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.9.0] - 2025-12-28

**Major Release: Production-Ready with Full ISO 42001 Compliance**

### 🎉 Added

#### Security
- **Multi-Tenant Isolation** with BOLA/IDOR protection (OWASP API1:2023)
  - UUID v4 validation for `tenant_id`
  - Database-level tenant isolation with composite indexes
  - JWT claims as single source of truth
  - Mass Assignment attack prevention
- **HMAC-SHA256 Signed Audit Ledger**
  - Tamper-proof logging (ISO 42001 A.7.5)
  - Cryptographic integrity validation
- **10/10 OWASP API Security Top 10 2023** mitigations implemented
  - SQL Injection prevention (SQLAlchemy ORM)
  - Authentication bypass protection (JWT validation)
  - Rate limiting (100 req/min default)
- **RBAC with 4 roles**: `admin`, `dev`, `auditor`, `app`

#### Compliance
- **ISO 42001:2023** - 32/32 Annex A controls implemented
- **EU AI Act** - 10 critical articles implemented:
  - Art. 5: Prohibited Practices (automated blocking)
  - Art. 6: Risk Classification (Annex III sectors)
  - Art. 9: Risk Management (3-agent assessment)
  - Art. 12: Logging (5-year retention)
  - Art. 14: Human Oversight (escalation workflow)
  - Art. 51: GPAI Systemic Risk (FLOPs validation)
  - Art. 71: EU Database (registration tracking)
- **GDPR Compliance** - Art. 25 (Privacy by Design), Art. 32 (Security)
- **NIST AI RMF 1.0** - 70% compatibility (GOVERN, MAP, MANAGE, MEASURE)

#### Intelligence Layer
- **Adaptive Risk Router** with 3 specialized agents:
  - **Technical Agent**: FLOPs, logging, complexity
  - **Regulatory Agent**: EU AI Act, ISO 42001, sectors
  - **Ethical Agent**: keywords, fairness, transparency
- **Compliance Memory RAG**: Historical violation tracking
- **Human Oversight Service**: Review workflow for escalations
- **Huwyler Threat Taxonomy** (2024): Standardized threat classification
  - 133 AI security incidents analyzed
  - Real-time prompt injection detection
  - MISUSE domain mapping

#### Operations (NEW v0.9.0)
- **Kill Switch** - Emergency Stop Protocol
  - Endpoint: `PUT /v1/systems/{system_id}/emergency-stop`
  - NIST AI RMF MANAGE-2.4 implementation
  - Immediate halt of all system operations
  - HMAC-signed audit trail
  - Database persistence of operational status
- **Operational Status Management**
  - 5 states: `active`, `degraded`, `maintenance`, `suspended`, `emergency_stop`
  - Lifecycle phase tracking (NIST MAP-1.1)
  - Supply chain component registry (NIST GOVERN-6.1)

#### Developer Experience
- **FastAPI Gateway** with interactive OpenAPI docs (`/docs`)
- **Docker Compose** setup (dev + secure production)
- **Automated Scripts**:
  - `generate_token.py` - JWT token generation
  - `rotate_secrets.sh` - Secret rotation (90-day cycle)
  - `validate_ledger.py` - HMAC integrity verification
  - `generate_compliance_report.py` - HTML/JSON reports
  - `setup_dev_env.sh` - One-command development setup

#### Documentation
- **ISO 42001 Compliance Mapping** - Full evidence package
- **EU AI Act Compliance Guide** - Article-by-article implementation
- **NIST AI RMF Compatibility** - 70% coverage evidence
- **Architecture Documentation** - Layered design (DDD)
- **Multi-Tenant Security Design** - Threat model & mitigations
- **API Reference** - Complete endpoint documentation (bilingual EN/PT)
- **Quick Start Guide** - 15-minute setup (bilingual EN/PT)
- **Deployment Guide** - Docker, Kubernetes, AWS ECS

#### Testing
- **87% code coverage** (target: 90%)
- **Security test suite**:
  - `test_bola.py` - Cross-tenant access prevention
  - `test_injection.py` - SQL injection, path traversal
  - `test_auth.py` - JWT validation, RBAC, privilege escalation
- **Unit tests** for domain entities and enforcement engine
- **Integration tests** for end-to-end workflows

### 🔄 Changed

- **Policy Merge Strategy**: Conservative merge (most restrictive wins)
- **Risk Scoring**: Weighted average (Technical 30%, Regulatory 40%, Ethical 30%)
- **Database Schema**: 
  - Added `operational_status` column to `ai_systems` table
  - Added `lifecycle_phase` column for NIST alignment
  - Added `human_ai_configuration` for Art. 14 compliance
  - Composite indexes for multi-tenant performance
- **Error Responses**: Standardized JSON format with exception handlers
- **Enforcement Engine Signature**: Now requires `env` parameter (breaking change)

### 🐛 Fixed

**Critical Hotfixes (2025-12-28)**:
- ✅ **Enforcement Engine signature mismatch**: Missing `env` parameter causing 422/500 errors
- ✅ **Gateway JSON serialization error**: Decision dataclass objects returning dict instead of JSONResponse
- ✅ **Kill Switch persistence bug**: Missing database columns (`operational_status`, `lifecycle_phase`)
- ✅ **Exception handler bug**: Error responses not properly formatted as JSON

**Security Fixes**:
- ✅ **BOLA vulnerability**: Tenant ID validation in all queries
- ✅ **Mass Assignment vulnerability**: JWT claims override payload
- ✅ **SQL Injection**: Parameterized queries via SQLAlchemy ORM
- ✅ **Timing attacks**: `hmac.compare_digest()` for constant-time comparison
- ✅ **JWT expiration**: Reduced default from 24h to 30min

### 🔒 Security

- **CVE Status**: No known vulnerabilities
- **Penetration Test Status**: Ready for external audit
- **Secret Management**: Environment variables + Docker secrets
- **TLS 1.3**: Enforced in production (nginx config)

### ⚠️ Breaking Changes

**CRITICAL**: All users must update code to include `env` parameter.

#### Python SDK
❌ OLD (v0.8.x) - WILL FAIL
decision = engine.enforce(task, system)

✅ NEW (v0.9.0) - REQUIRED
decision = engine.enforce(task, system, env="production")


#### REST API
❌ OLD - Returns 422 Error
curl -X POST /v1/enforce -d '{"system_id": "...", "prompt": "..."}'

✅ NEW - Required Field
curl -X POST /v1/enforce -d '{"system_id": "...", "prompt": "...", "env": "production"}'


#### Other Breaking Changes
- JWT tokens **must include** `tenant_id` claim
- Database schema changed (migration required - see upgrade guide)
- Minimum Python version: **3.10** (was 3.8)

### 🗑️ Deprecated

**v0.9.0 Deprecations** (will be removed in v1.0.0):
- Single-tenant mode (multi-tenant is now mandatory)
- SQLite in production (use PostgreSQL)

---

## [0.8.0] - 2024-11-15

**Beta Release**

### Added
- Basic enforcement engine
- SQLite support for development
- Simple policy configuration

### Changed
- Migrated from Flask to FastAPI

---

## [0.7.0] - 2024-10-01

**Prototype**

### Added
- Initial proof of concept
- Basic risk assessment
- YAML configuration

---

## [Unreleased]

Planned for **v0.9.5** (Q1 2026) and **v1.0.0** (Q2 2026)

### Features (v0.9.5 - Foundation Hardening)
- ✨ Fairness testing framework (NIST MEASURE-2.11)
- ✨ Policy Cards schema (machine-readable runtime governance)
- ✨ AICM validation engine (CSA AI Controls Matrix)
- 🔧 Performance optimization (enforcement <100ms latency)

### Features (v1.0.0 - Production Enterprise)
- 🚀 **Dashboard UI** (React + TypeScript)
  - Real-time compliance monitoring
  - Human oversight interface
  - Grafana-style visualizations
- 🚀 **Vector Database Integration** (ChromaDB)
  - Semantic similarity search for violations
  - Embedding-based RAG
- 🚀 **Auto-Remediation Agents**
  - LLM-powered policy suggestions
  - Automated corrective actions
- 🚀 **Enhanced Integrations**
  - Slack notifications
  - PagerDuty alerting
  - Datadog metrics
  - Splunk log shipping
- 🚀 **Policy Cards Enforcement Logic** (Mavracic 2024)
- 🚀 **Auto-Decommissioning** (NIST MANAGE-4.1)
- 📈 **100% NIST AI RMF coverage**

### Database Support
- MongoDB support (NoSQL option)
- Cassandra support (high-scale deployments)
- Database migration tool

### Deployment
- Kubernetes Helm charts
- Terraform modules (AWS, Azure, GCP)
- Multi-cloud deployment guides

### Compliance
- SOC 2 Type II certification
- ISO 27001:2022 certification

---

## Versioning Strategy

- **Major (X.0.0)**: Breaking API changes, new architecture
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.9.X)**: Bug fixes, security patches

---

## Upgrade Guide

### From v0.8.x to v0.9.0

#### 1. Database Migration

-- Add tenant_id to existing systems
ALTER TABLE ai_systems ADD COLUMN tenant_id VARCHAR(36);

-- Assign legacy tenant
UPDATE ai_systems SET tenant_id = 'legacy-tenant-uuid';

-- Add new v0.9.0 columns
ALTER TABLE ai_systems ADD COLUMN operational_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE ai_systems ADD COLUMN lifecycle_phase VARCHAR(50) DEFAULT 'deployment';
ALTER TABLE ai_systems ADD COLUMN human_ai_configuration JSONB;

-- Add constraints
ALTER TABLE ai_systems ALTER COLUMN tenant_id SET NOT NULL;
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);


#### 2. Configuration Changes

**governance.yaml (NEW)**:
Prohibited practices enforcement
prohibited_practices:

social_scoring

subliminal_manipulation

Logging configuration
logging:
retention_days: 1825 # 5 years
tamper_proof: true


#### 3. Code Changes

OLD (v0.8.x)
decision = engine.enforce(task, system)

NEW (v0.9.0) - Add environment parameter
decision = engine.enforce(task, system, env="production")


#### 4. Environment Variables

Add to .env
OPERATIONAL_STATUS_DEFAULT=active
LIFECYCLE_PHASE_DEFAULT=deployment


---

## Contributors

### Core Team
- **Daniel Zero** - Project Lead & Architecture
- **BuildToValue Community** - 12 contributors

### Security Auditors
- [Your Security Firm] - Penetration testing (planned Q1 2026)

### Research Contributors
- **Prof. Hernan Huwyler** (2024) - Threat Taxonomy validation
- **Juraj Mavracic** (2024) - Policy Cards architecture
- **NIST AI RMF Team** - Governance framework
- **Cloud Security Alliance** - AI Controls Matrix

---

## License

Apache License 2.0 - See [LICENSE](./LICENSE) for details.

**Open Core Model**:
- Core governance engine: **Open Source**
- Enterprise features (SSO, SIEM, SLA): **Commercial**

---

## Support

For detailed upgrade instructions, see [UPGRADING.md](./UPGRADING.md)  
For security advisories, see [SECURITY.md](./SECURITY.md)

---

**Last Updated**: December 28, 2025  
**Status**: Production-Ready (v0.9.0 Golden Candidate)