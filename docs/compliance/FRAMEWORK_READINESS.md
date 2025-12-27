# Framework Readiness & Future Integrations

**BuildToValue Framework v0.9.0**  
**Last Updated:** December 26, 2025

---

## Overview

BuildToValue v0.9.0 is designed with **extensible schema architecture** to support future integration with emerging AI governance frameworks. While we currently implement **NIST AI RMF 1.0 (70% compatible)**, our data model includes fields prepared for:

- Policy Cards (Mavracic 2025)
- AI Controls Matrix (CSA AICM)
- Future regulatory requirements (EU AI Act updates, FDA guidelines)

**Important:** This document describes **architectural readiness**, not active integrations.

---

## ✅ Currently Implemented (v0.9.0)

### NIST AI RMF 1.0
- **Status:** 70% Compatible (Verified)
- **Evidence:** See [NIST_AI_RMF_COMPATIBILITY.md](./NIST_AI_RMF_COMPATIBILITY.md)
- **Certification:** Self-assessed, open-source verification

### EU AI Act (2024/1689)
- **Status:** High-risk system schema compliant
- **Evidence:** `EUComplianceRisk` enum, `eu_database_id` field
- **Certification:** Preparing for official registration (Art. 71)

### Huwyler Threat Taxonomy (2025)
- **Status:** Fully implemented
- **Evidence:** `ThreatVectorClassifier` validates 133 documented incidents
- **Reference:** arXiv:2511.21901v1

---

## ⏸️ Architecture Ready (Future Integration)

### Policy Cards (Mavracic 2025)

**Reference:** [arXiv:2510.24383v1](https://arxiv.org/abs/2510.24383)

**What we prepared:**

src/domain/entities.py
@dataclass
class AISystem:
policy_card_uri: Optional[str] = None # Link to Policy Card JSON
src/domain/entities.py
@dataclass
class AISystem:
policy_card_uri: Optional[str] = None # Link to Policy Card JSON


**Status:** 
- ✅ Schema field exists
- ⏸️ Runtime enforcement not implemented (v1.0 roadmap)
- ⏸️ JSON Schema validator pending

**Why it's ready:**
Policy Cards define machine-readable operational constraints. Our `OperationalStatus` enum + `governance_policy` field provide the foundation for Policy Card runtime enforcement.

**Next steps (v1.0):**
1. Implement Policy Card JSON Schema validator
2. Parse allow/deny rules from Policy Card
3. Integrate with `EnforcementEngine`

---

### AI Controls Matrix (CSA AICM)

**Reference:** [Cloud Security Alliance - AI Controls Matrix v1.0](https://cloudsecurityalliance.org/artifacts/ai-controls-matrix)

**What we prepared:**
@dataclass
class AISystem:
aicm_controls_applicable: List[str] = [] # ["GRC-01", "DSP-03"]
aicm_controls_implemented: List[str] = []

def calculate_aicm_coverage(self) -> float:
    """Returns implementation percentage (0.0-1.0)."""

**Status:**
- ✅ Metadata fields exist
- ✅ Coverage calculation implemented
- ⏸️ Automated control validation pending (v1.0)

**Example:**
system = AISystem(
id="credit-scoring",
aicm_controls_applicable=["GRC-01", "GRC-02", "DSP-01", "DSP-03"],
aicm_controls_implemented=["GRC-01", "DSP-01"]
)

coverage = system.calculate_aicm_coverage() # 0.5 (50%)


**Why it's useful NOW:**
- Document control implementation progress
- Generate compliance reports for auditors
- Track security posture over time

**Next steps (v1.0):**
1. Map AICM controls to enforcement rules
2. Automated validation of control implementation
3. Integration with CSA AICM API (if available)

---

### Third-Party Frameworks (Generic Support)

**What we prepared:**
@dataclass
class AISystem:
governance_policy: Optional[Dict[str, Any]] = None # Flexible JSON


**Use cases:**
- ISO 42001 custom controls
- Sector-specific regulations (FDA, FCA, etc.)
- Internal company policies

**Example:**

system = AISystem(
id="medical-imaging",
governance_policy={
"fda_device_class": "II",
"510k_number": "K123456",
"custom_rules": {
"require_radiologist_review": True,
"max_false_negative_rate": 0.02
}
}
)


---

## ❌ What We DO NOT Claim

### NOT Integrated (v0.9.0)

1. **AI TIPS 2.0 (Trusted AI)**
   - Reason: Proprietary framework, no public API
   - Status: Concepts studied, NOT implemented
   - Clarification: We understand the 8 pillars, but don't claim compliance

2. **MITRE ATLAS**
   - Reason: Focused on adversarial tactics, orthogonal to governance
   - Status: Threat taxonomy uses Huwyler instead (more comprehensive)

3. **MLOps Frameworks (MLflow, Kubeflow, etc.)**
   - Reason: Infrastructure tools, not governance standards
   - Status: Can integrate via APIs (v1.0)

---

## Compliance Claims Policy

**What we CAN say:**
- ✅ "NIST AI RMF 1.0 Compatible (70%)"
- ✅ "EU AI Act High-Risk Schema Compliant"
- ✅ "Huwyler Threat Taxonomy Validated (133 incidents)"
- ✅ "Policy Cards Architecture Ready"
- ✅ "AICM Metadata Layer Implemented"

**What we CANNOT say:**
- ❌ "AI TIPS 2.0 Certified"
- ❌ "ISO 42001 Certified" (requires external audit)
- ❌ "100% NIST Compliant" (we're at 70%)

---

## Roadmap

### v0.9.5 (Q1 2026)
- [ ] Policy Card JSON Schema validator
- [ ] AICM control automated validation
- [ ] Fairness testing framework (NIST MEASURE-2.11)

### v1.0 (Q2 2026)
- [ ] Policy Card runtime enforcement
- [ ] AICM API integration
- [ ] User feedback API (NIST MEASURE-3.3)
- [ ] Decommissioning automation (NIST MANAGE-4.1)

---

## For Auditors

**Question:** "Are you AI TIPS 2.0 compliant?"

**Answer:** 
> BuildToValue v0.9.0 includes metadata fields compatible with AI TIPS concepts (lifecycle phases, control coverage tracking), but we do NOT implement the full AI TIPS 2.0 framework. Our primary compliance target is NIST AI RMF 1.0 (70% compatible, open-source verifiable).

**Question:** "Can you integrate with Policy Cards?"

**Answer:**
> Yes, our schema includes `policy_card_uri` field for future runtime enforcement. Implementation planned for v1.0 (Q2 2026). Current architecture supports Policy Card principles (operational status, kill switch, lifecycle tracking).

---

## References

1. **NIST AI RMF 1.0:** https://doi.org/10.6028/NIST.AI.100-1
2. **Policy Cards (Mavracic 2025):** https://arxiv.org/abs/2510.24383
3. **Huwyler Threat Taxonomy (2025):** https://arxiv.org/abs/2511.21901
4. **CSA AICM:** https://cloudsecurityalliance.org/artifacts/ai-controls-matrix
5. **EU AI Act (2024/1689):** https://eur-lex.europa.eu/eli/reg/2024/1689

---

**Disclaimer:** BuildToValue is an open-source project. Compliance claims are self-assessed and verifiable through our public GitHub repository. For official certifications, engage an accredited third-party auditor.

