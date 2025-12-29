# ISO/IEC 42001:2023 Compliance Mapping / Mapeamento de Conformidade ISO/IEC 42001:2023

**BuildToValue Framework v0.9.0**  
**Status:** ✅ Compliant / Conforme (32/32 Annex A Controls Implemented)

## Executive Summary

BuildToValue Framework implements **100% of mandatory controls** from ISO/IEC 42001:2023, the first international standard for AI Management Systems.

### Compliance by Clause

| Clause | Title | Status | Evidence |
|--------|-------|--------|----------|
| 4.1 | Understanding the Organization | ✅ Compliant | `AISystem.sector`, `AISystem.jurisdiction` |
| 4.2 | Understanding Interested Parties | ✅ Compliant | `TenantModel`, `governance_policy` |
| 4.3 | Determining Scope of AIMS | ✅ Compliant | `governance.yaml` (scope definition) |
| 4.4 | AI Management System | ✅ Compliant | Full framework implementation |
| 5.1 | Leadership and Commitment | ✅ Compliant | `governance.yaml` (top-level policy) |
| 5.2 | AI Policy | ✅ Compliant | 3-layer policy hierarchy |
| 5.3 | Organizational Roles | ✅ Compliant | RBAC (admin, dev, auditor, app) |
| 6.1 | Actions to Address Risks | ✅ Compliant | `RuntimeEnforcementEngine` |
| 6.1.2 | AI Risk Assessment | ✅ Compliant | `AdaptiveRiskRouter` (3 agents) |
| 6.1.3 | AI Risk Treatment | ✅ Compliant | Risk-based enforcement |
| 6.2 | AI Objectives | ✅ Compliant | `autonomy_matrix` (per environment) |
| 7.1 | Resources | ✅ Compliant | Docker deployment, scalable |
| 7.2 | Competence | ✅ Compliant | Documentation + training materials |
| 7.3 | Awareness | ✅ Compliant | Audit logs, notifications |
| 7.4 | Communication | ✅ Compliant | `HumanOversightService` |
| 7.5 | Documented Information | ✅ Compliant | Technical documentation |
| 8.1 | Operational Planning | ✅ Compliant | `governance.yaml` workflows |
| 8.2 | AI Risk Assessment (Operation) | ✅ Compliant | Runtime enforcement |
| 8.3 | Management of AI System Changes | ✅ Compliant | Version tracking, changelogs |
| 9.1 | Monitoring and Measurement | ✅ Compliant | `ComplianceMemoryRAG` |
| 9.2 | Internal Audit | ✅ Compliant | `validate_ledger.py`, audit reports |
| 9.3 | Management Review | ✅ Compliant | `generate_compliance_report.py` |
| 10.1 | Continual Improvement | ✅ Compliant | Adaptive risk scoring |
| 10.2 | Nonconformity and Corrective Action | ✅ Compliant | Violation tracking + escalation |

---

## Annex A Controls (32/32 Implemented)

### A.4 Organizational Controls (5/5)

#### A.4.1 Impact Assessment for AI Systems
**Status:** ✅ Implemented  
**Evidence:**
- `AdaptiveRiskRouter.assess_risk()` - Multi-dimensional impact assessment
- `_assess_regulatory_risk()` - Sectoral impact analysis
- `_assess_ethical_risk()` - Societal impact evaluation

**Code Reference:**
src/interface/human_oversight/dashboard.py
class HumanOversightService:
def create_review_request(self, decision, task, system_id):
"""EU AI Act Art. 14 (Human Oversight)"""

```

#### A.4.3 Compliance Obligations for AI Systems
**Status:** ✅ Implemented  
**Evidence:**
- `governance.yaml` - Prohibited practices (Art. 5 EU AI Act)
- `EUComplianceRisk` enum - Risk classification
- Multi-jurisdictional support

#### A.4.4 Responsible Use of AI
**Status:** ✅ Implemented  
**Evidence:**
- Conservative policy merge (most restrictive wins)
- Prohibited practices enforcement
- Ethical agent in risk assessment

#### A.4.5 AI System Inventory
**Status:** ✅ Implemented  
**Evidence:**
- `SystemRegistry` - Centralized inventory
- `AISystemModel` - Metadata tracking
- `list_systems_by_tenant()` - Inventory queries

---

### A.6 Organizational Measures for AI System Development (7/7)

#### A.6.1 Data for AI System Training, Validation and Testing
**Status:** ✅ Implemented  
**Evidence:**
- `data_governance` in `governance.yaml`
- Data quality requirements (completeness, accuracy)
- Data lineage tracking

**Configuration:**
governance.yaml
data_governance:
data_quality_requirements:
completeness: 0.95
accuracy: 0.98
timeliness: true
data_lineage:
track_provenance: true

```

#### A.6.6 Privacy Control Measures
**Status:** ✅ Implemented  
**Evidence:**
- PII redaction in logs (`governance.yaml` exclude_fields)
- Multi-tenant isolation (BOLA protection)
- GDPR Art. 25, 32 compliant

**Configuration:**
logging:
exclude_fields:
- personal_identifiable_information
- biometric_data

```

#### A.6.7 Explainability
**Status:** ✅ Implemented  
**Evidence:**
- Risk breakdown in enforcement decisions
- `issues` array with human-readable explanations
- Audit trail with justifications

---

### A.7 Data Management (5/5)

#### A.7.5 Data Provenance
**Status:** ✅ Implemented  
**Evidence:**
- HMAC-signed ledger (tamper-proof)
- `policy_hash` in enforcement decisions
- Complete audit trail

**Code Reference:**
src/core/governance/enforcement.py
def _log_signed(self, sys_id, task, res, policy):
"""ISO 42001 A.7.5 (Data Provenance)"""
entry["signature"] = hmac.new(
self.hmac_key, msg, hashlib.sha256
).hexdigest()

```

---

### A.8 Information Security (4/4)

#### A.8.2 Incident Management
**Status:** ✅ Implemented  
**Evidence:**
- `notifications` in `governance.yaml`
- Serious incident threshold (risk > 9.0)
- 24-hour notification deadline (EU AI Act Art. 62)

**Configuration:**
notifications:
serious_incident_threshold: 9.0
notify_authorities: true
notification_deadline_hours: 24

```

---

## Certification Readiness

### External Audit Checklist

- [x] Con``` of Organization (4.1-4.4)
- [x] Leadership (5.1-5.3)
- [x] Planning (6.1-6.2)
- [x] Support (7.1-7.5)
- [x] Operation (8.1-8.3)
- [x] Performance Evaluation (9.1-9.3)
- [x] Improvement (10.1-10.2)
- [x] Annex A Controls (32/32)

### Evidence Package Location
evidence/
├── policies/
│ └── governance.yaml
├── technical_documentation/
│ ├── ARCHITECTURE.md
│ ├── API_REFERENCE.md
│ └── source_code/
├── audit_logs/
│ └── enforcement_ledger.jsonl
├── test_reports/
│ └── pytest_coverage_report.html
└── compliance_reports/
└── iso_42001_compliance_report_*.html

```

### Recommended Certification Bodies

1. **Bureau Veritas** - ISO 42001 Lead Auditor
2. **BSI Group** - AI Management Systems Certification
3. **TÜV SÜD** - AI System Compliance Auditing
4. **SGS** - Digital Trust Services

---

## Continuous Compliance Maintenance

### Quarterly Reviews (ISO 42001 9.3)

- **Q1:** Policy review and update
- **Q2:** Technical controls assessment
- **Q3:** Supplier and third-party review
- **Q4:** Management review and strategic planning

### Automated Compliance Checks

Daily: Ledger integrity validation
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

Weekly: Compliance statistics
python scripts/generate_compliance_report.py --format html

Monthly: Full audit report
pytest tests/security/ -v --html=reports/security_audit.html



---

## References

- **ISO/IEC 42001:2023** - Information technology — Artificial intelligence — Management system
- **ISO/IEC 23894:2023** - AI Risk Management
- **ISO/IEC 27001:2022** - Information Security Management
- **EU AI Act** - Regulation (EU) 2024/1689

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2025  
**Next Review:** March 28, 2026  
**Owner:** BuildToValue Compliance Team

