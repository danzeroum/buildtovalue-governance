# 🛡️ BuildToValue Product Scope & Licensing Model

BuildToValue operates under an **Open Core** model. This means that the governance engine, fundamental security, and technical compliance are 100% Open Source (Apache 2.0), ensuring transparency and auditability. Management features at scale, collaboration, and corporate integrations are reserved for the Enterprise version.

## Separation Philosophy

- **Open Source (Core):** Everything an Engineer/Architect needs to *execute* real-time governance and ensure technical security.
- **Enterprise:** Everything a Manager/CISO needs to *manage* policies at scale, visualize data, and integrate with existing corporate infrastructure.

---

## 📊 Feature Matrix (v0.9.0)

| Category | Feature | Open Source (Core) | Enterprise |
| :--- | :--- | :---: | :---: |
| **Enforcement** | **Runtime Engine (Interceptor)** | ✅ Yes | ✅ Yes |
| | Multi-Agent Scoring (Technical, Regulatory, Ethical) | ✅ Yes | ✅ Yes |
| | Kill Switch (Emergency Stop API) | ✅ Yes | ✅ Yes |
| | Latency Overhead | < 50ms | < 50ms |
| **Security** | **HMAC-Signed Audit Ledger** | ✅ Yes | ✅ Yes |
| | Multi-Tenant Isolation (TenantID Enforced) | ✅ Yes | ✅ Yes |
| | Threat Taxonomy (Huwyler 2025) | ✅ Yes | ✅ Yes |
| | SSO / SAML / OIDC Integration | ❌ No | ✅ Yes |
| | Granular Role-Based Access Control (RBAC) | Basic (Admin/User) | Advanced |
| **Compliance** | **NIST AI RMF 1.0 Architecture** | ✅ Yes | ✅ Yes |
| | EU AI Act Schema (High-Risk Tracking) | ✅ Yes | ✅ Yes |
| | Supply Chain Registry (Dependencies) | ✅ Yes | ✅ Yes |
| | PDF/Docx Report Generator (Auditor-Ready) | ❌ No (JSON/HTML) | ✅ Yes |
| **Integration** | **Python SDK & CLI Tool** | ✅ Yes | ✅ Yes |
| | Full REST API | ✅ Yes | ✅ Yes |
| | Docker Compose Deployment | ✅ Yes | ✅ Yes |
| | SIEM Connectors (Splunk, Datadog, ELK) | ❌ Pure JSON logs | ✅ Native Connectors |
| | Policy Cards Conversion (Interoperability) | ⚠️ (Schema Ready) | ✅ Automatic |
| **Management** | **Web Dashboard (GUI)** | ❌ No (CLI/API) | ✅ Yes |
| | Visual Policy Editor (No-Code) | ❌ No (YAML) | ✅ Yes |
| | Team Management and Approvals | ❌ No | ✅ Yes |
| | Multi-Workspace (Organizations) | ❌ No | ✅ Yes |
| **Observability** | **Structured Logs (JSON)** | ✅ Yes | ✅ Yes |
| | Prometheus/OpenTelemetry Metrics | ✅ Yes (basic) | ✅ Yes (advanced) |
| | Custom Alerts | ❌ No | ✅ Yes |
| | Distributed Tracing | ❌ No | ✅ Yes |
| **Support** | Response SLA | Community (Best Effort) | 24/7 or 8/5 |
| | Personalized Onboarding | ❌ No | ✅ Yes |
| | Architecture Consulting | ❌ No | ✅ Yes |

---

## 🎯 Design Principles

### 1. Security Is Not a Paywall
**Strategic Decision:** All security features (HMAC, Kill Switch, Threat Taxonomy, Multi-Tenant Isolation) are Open Source.

**Rationale:**
- Community trust requires auditability
- Security as paywall = "security theater"
- Competitive differentiator is management ease, not technical functionality

### 2. Enterprise = Convenience + Management
**What differentiates Enterprise:**
- **Convenience:** Visual dashboard vs CLI/API
- **Management:** Approvals, teams, workflows vs manual configuration
- **Integrations:** Native connectors vs raw JSON logs
- **Support:** Contractual SLA vs community best effort

### 3. Frictionless Migration
**Technical guarantee:**
- Enterprise Edition is an additional layer (extra containers)
- Same database, same API, same Core engine
- Zero-downtime upgrade, rollback without data loss

---

## 🔮 Differentiation Roadmap

### Planned Features for v0.9.5 (Open Source)
- [ ] **Fairness Testing Framework:** API to execute bias tests
- [ ] **Policy Cards JSON Validator:** Validate Policy Cards syntax
- [ ] **Workforce Diversity Tracking:** Fields for team composition
- [ ] **Cost-Benefit Analysis:** Fields for ROI/TCO analysis

### Planned Features for v0.9.5 (Enterprise)
- [ ] **Dashboard Alpha:** Basic web interface (React)
- [ ] **SSO Integration (Okta):** First SSO connector
- [ ] **PDF Compliance Reports:** Report generation for auditors
- [ ] **Slack Notifications:** Real-time violation alerts

### Planned Features for v1.0 (Open Source)
- [ ] **Policy Cards Engine (Read-Only):** Reading and parsing Policy Cards
- [ ] **Environmental Impact Calculator:** Automatic carbon estimation
- [ ] **User Feedback API:** Endpoint to register user feedback
- [ ] **Decommissioning Workflow:** Automated retirement process

### Planned Features for v1.0 (Enterprise)
- [ ] **Policy Cards Engine (Full):** Complex ABAC validation and enforcement
- [ ] **Automated Fairness Testing:** Statistical batteries (AIF360 integration)
- [ ] **Predictive Compliance Scoring:** ML-based risk prediction
- [ ] **Multi-Cloud Terraform Modules:** AWS/Azure/GCP deployment
- [ ] **Advanced RBAC:** Attribute-Based Access Control (ABAC)

---

## 💼 Design Partners Program (Enterprise Beta)

**Status:** Accepting 5 design partners for Q1 2026

**Benefits:**
- ✅ Early access to Dashboard (Q1 2026)
- ✅ Influence on feature roadmap
- ✅ Preferential pricing (50% discount year 1)
- ✅ Consulting credits ($10k USD)
- ✅ Co-marketing (optional case study)

**Requirements:**
- Production environment with high-risk AI (EU AI Act Art. 6)
- Commitment to weekly feedback
- Dedicated technical team (1 person 20% time)

**Contact:** [enterprise@buildtovalue.com](mailto:enterprise@buildtovalue.com)

---

## 🤔 Frequently Asked Questions

### Q: Can I use the Open Source version in production?
**A:** Yes. The Apache 2.0 license allows commercial use without restrictions. The engine is "production-ready" and contains all critical security features (HMAC, Kill Switch, Threat Taxonomy). Companies like [CASE STUDY TBD] use Core in production.

### Q: What happens if I need to migrate to Enterprise?
**A:** Migration is transparent. Enterprise is an additional layer (extra containers: `btv-dashboard`, `btv-sso-proxy`) that connects to the same database and Core engine. No code refactoring is required. Estimated upgrade process: < 4 hours.

### Q: Do you offer support for the Open Source version?
**A:** Yes, through the community:
- GitHub Issues: [github.com/danzeroum/buildtovalue-governance/issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- Discord: [discord.gg/buildtovalue](https://discord.gg/buildtovalue)
- Response time: Best effort (usually 24-72h)

For contractual SLA support, consider Enterprise Edition.

### Q: Why didn't you put the Dashboard in Open Source?
**A:** Strategic decision based on 3 factors:
1. **Maintenance complexity:** Maintaining a React/TypeScript frontend requires significant resources
2. **Competitive differentiation:** Our research showed that CISOs pay for convenience, not technical functionality
3. **Sustainability:** Enterprise revenue funds Core development

**Alternative for developers:** Use the REST API + tools of your choice (Grafana, Retool, etc.)

### Q: Can I create my own Dashboard using the API?
**A:** Yes! The REST API is 100% Open Source and documented. You can create any custom interface. In fact, we'd love to see alternative dashboard contributions from the community.

### Q: How do you avoid "bait and switch" (moving features from Open to Enterprise later)?
**A:** Public commitment in `PRODUCT_SCOPE.md` (this file):
- ✅ **Kill Switch remains Open Source** (committed in v0.9.0)
- ✅ **HMAC Ledger remains Open Source** (committed in v0.9.0)
- ✅ **Threat Taxonomy remains Open Source** (committed in v0.9.0)
- ✅ **NIST/EU AI Act Schema remains Open Source** (committed in v0.9.0)

**Guarantee:** Any change of these components to Enterprise would be an Apache 2.0 license violation (which allows perpetual use of existing versions) and would destroy our credibility.

### Q: Do you plan a SaaS (hosted) version?
**A:** Yes, on the roadmap for Q3 2026. It will be based on the Enterprise Edition with infrastructure management included. Open Source will continue available for self-hosting.

---

## 📜 Compliance with Open Source Best Practices

This model follows recommendations from:
- [Open Source Initiative - Licensing](https://opensource.org/licenses/Apache-2.0)
- [TODO Group - Best Practices for Corporate Open Source](https://todogroup.org/guides/)
- [Linux Foundation - Open Source Licensing Guide](https://www.linuxfoundation.org/resources/open-source-guides)

**Audited on:** December 26, 2025  
**Next review:** March 26, 2026

---

## 📞 Contact

- **Open Source (Community):** [GitHub Issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- **Enterprise Sales:** [enterprise@buildtovalue.com](mailto:enterprise@buildtovalue.com)
- **Security:** [security@buildtovalue.com](mailto:security@buildtovalue.com)
- **General:** [hello@buildtovalue.com](mailto:hello@buildtovalue.com)

---

**Version:** 1.0  
**Last Updated:** December 28, 2025  
**Status:** 🟢 Final (Approved for Public Release)
