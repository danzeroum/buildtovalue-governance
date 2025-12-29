# 🏛️ BuildToValue Governance Model

**Version:** 1.0  
**Effective Date:** December 26, 2025  
**Last Updated:** December 26, 2025  
**Status:** Active

---

## Table of Contents

1. [Introduction](#introduction)
2. [Model of Authority](#1-model-of-authority-bdfl)
3. [Succession Council](#2-succession-council-bus-factor-protocol)
4. [Contributor Levels](#3-contributor-levels)
5. [Contribution Rules](#4-contribution-rules)
6. [Anti-Burnout Protocol](#5-anti-burnout-protocol-emergency-brake)
7. [Conflict Resolution](#6-conflict-resolution)
8. [Amendment Process](#7-amendment-process)
9. [Legal Framework](#8-legal-framework)

---

## Introduction

BuildToValue is an open-source project licensed under Apache License 2.0, committed to transparent governance while maintaining the focus and quality needed for security-critical AI governance infrastructure.

### Governance Philosophy

**"Benevolent dictator with community input, not dictatorship."**

- **Security decisions require expertise** → BDFL has final authority on crypto/security
- **Feature decisions benefit from community** → Open RFC process for non-security features
- **Sustainability requires protection** → Anti-burnout protocols are not optional

This document serves as:
- 🛡️ **Legal Shield:** Protects the founder and project from liability
- 🔒 **Operational Continuity:** Ensures project survives founder unavailability
- 🤝 **Community Contract:** Sets clear expectations for all participants

---

## 1. Model of Authority (BDFL)

### 1.1 Benevolent Dictator for Life (BDFL)

**Current BDFL:** [Your Name / GitHub Handle]

**Scope of Authority:**

The BDFL has **final decision-making authority** over:

#### Critical Domains (Unilateral Authority)
- ✅ **Security & Cryptography:** HMAC implementation, JWT security, audit ledger design
- ✅ **Compliance Architecture:** NIST AI RMF mapping, EU AI Act schema, ISO 42001 controls
- ✅ **Legal Decisions:** Licensing, trademark usage, contributor agreements
- ✅ **Emergency Response:** Security incidents, emergency patches, kill switch activation
- ✅ **Core Architecture:** Multi-tenant design, enforcement engine, threat taxonomy

**Justification:** These areas require deep expertise and coordinated decision-making. Community input is welcomed, but final decisions rest with BDFL to prevent "design by committee" anti-patterns.

#### Community-Informed Domains (Collaborative Authority)
- 🤝 **Feature Requests:** Dashboard UI, CLI improvements, API enhancements
- 🤝 **Documentation:** Guides, tutorials, examples
- 🤝 **Integrations:** SIEM connectors, third-party plugins
- 🤝 **Testing:** Test coverage improvements, simulation scenarios

**Process:** BDFL reviews community RFCs (Request for Comments) and makes final decision with transparent reasoning.

### 1.2 Decision-Making Framework

| Decision Type | Authority | Community Input | Veto Power |
|---------------|-----------|-----------------|------------|
| **Security Patch** | BDFL | Optional | BDFL |
| **Cryptographic Change** | BDFL | Recommended | BDFL |
| **Feature Addition** | BDFL | Required (RFC) | BDFL |
| **Documentation** | Core Contributors | Optional | BDFL (rare) |
| **Bug Fix** | Any Contributor | Not Required | Core Contributors |

### 1.3 BDFL Responsibilities

The BDFL commits to:
- ✅ Respond to security reports within 48 hours
- ✅ Review community RFCs within 14 days
- ✅ Publish quarterly roadmap updates
- ✅ Maintain transparency in decision-making (public GitHub discussions)
- ✅ Activate Anti-Burnout Protocol when necessary

### 1.4 BDFL Recusal

The BDFL must recuse themselves from decisions where they have **direct financial conflict of interest**:

**Example:** If BDFL's employer submits a PR that benefits only that employer (not the community), the decision goes to Core Contributors vote (simple majority).

**Process:**
1. BDFL declares conflict publicly in PR/issue
2. Core Contributors vote (72-hour window)
3. Decision recorded in `decisions/` directory with rationale

---

## 2. Succession Council (Bus Factor Protocol)

### 2.1 Purpose

**"If I get hit by a bus tomorrow, the project must survive."**

The Succession Council ensures operational continuity if the BDFL becomes unavailable (health, accident, burnout, resignation).

### 2.2 Council Composition

The council consists of **three trusted individuals** with complementary expertise:

| Role | Responsibilities | Current Member | Contact |
|------|------------------|----------------|---------|
| **Technical Lead** | Backend, infrastructure, enforcement engine | [TBD - To be appointed Q1 2026] | technical-lead@buildtovalue.ai |
| **Security Lead** | Cryptography, audit, vulnerability response | [TBD - To be appointed Q1 2026] | security-lead@buildtovalue.ai |
| **Legal Advisor** | OSS licensing, IP, contributor agreements | [TBD - To be appointed Q1 2026] | legal@buildtovalue.ai |

**Appointment Process:**
- BDFL appoints council members publicly via GitHub announcement
- Appointees must accept role in writing (email + GitHub issue comment)
- Council members serve indefinitely until resignation or removal by BDFL

### 2.3 Bus Factor Protocol (Activation Triggers)

The council is activated **automatically** if:

1. ✅ **Extended Unavailability:** BDFL unresponsive for 30+ consecutive days without prior notice
2. ✅ **Health Emergency:** BDFL (or authorized family member) declares incapacitation
3. ✅ **Voluntary Trigger:** BDFL explicitly activates protocol (e.g., sabbatical)
4. ✅ **Security Emergency:** Critical vulnerability + BDFL unreachable for 7+ days

**Verification:**
- Council members attempt contact via 3 channels (email, phone, emergency contact)
- 72-hour waiting period before activation
- Activation announced publicly on GitHub

### 2.4 Council Powers (Temporary Authority)

**When activated, the council CAN:**
- ✅ Merge security patches and critical bug fixes
- ✅ Respond to vulnerability reports
- ✅ Maintain project infrastructure (CI/CD, hosting)
- ✅ Approve non-breaking feature PRs (unanimous vote required)
- ✅ Communicate with community on BDFL's behalf

**The council CANNOT:**
- ❌ Change the Apache 2.0 license
- ❌ Transfer trademark ownership
- ❌ Sell or monetize the project
- ❌ Make architectural changes to security/crypto layers
- ❌ Remove or ban contributors (except spam/abuse)

### 2.5 Succession Process (Permanent Transition)

If BDFL is **permanently unavailable** (death, permanent incapacitation, resignation without successor):

**Step 1: Transition Period (90 days)**
- Council operates under temporary powers
- Community notified via GitHub announcement
- RFCs opened for new governance model

**Step 2: Election (If No Designated Successor)**
- Core Contributors nominate candidates (including themselves)
- Nominees must have 20+ merged PRs in past 12 months
- Community vote (weighted by contributions: 1 merged PR = 1 vote)
- Simple majority wins

**Step 3: Transition**
- New BDFL appointed or governance transitions to Core Contributors Committee model
- Updated GOVERNANCE.md published
- Trademark/infrastructure access transferred

### 2.6 1Password Vault (Emergency Access)

**Vault Contents:**
- GitHub organization admin credentials
- Docker Hub / container registry credentials
- Domain registrar (buildtovalue.ai)
- Email accounts (@buildtovalue.ai)
- Server SSH keys (encrypted)
- HMAC master key (encrypted with council members' PGP keys)

**Access Protocol:**
- Vault shared with council members via 1Password Emergency Access
- 7-day delay for access (allows BDFL to revoke if false alarm)
- Access logged and audited

**Setup Status:** 🔄 To be configured Q1 2026 (after council appointed)

---

## 3. Contributor Levels

### 3.1 Hierarchy

```
┌─────────────────────────────────────────────────┐
│ BDFL (Founder) │
│ Final authority on security/crypto/compliance │
└─────────────────────────────────────────────────┘
│
┌────────────┴────────────┐
│ │
┌───────────────────┐ ┌──────────────────────┐
│ Core Contributors │ │ Succession Council │
│ (2-5 people) │ │ (3 people) │
│ Commit access │ │ Emergency powers │
└───────────────────┘ └──────────────────────┘
│
│
┌───────────────────────────────────────────────┐
│ Verified Contributors │
│ PRs accepted, priority reviews, recognized │
└───────────────────────────────────────────────┘
│
│
┌───────────────────────────────────────────────┐
│ Community Contributors │
│ All others (welcome to contribute!) │
└───────────────────────────────────────────────┘

```


### 3.2 Level Definitions

#### **Level 4: BDFL**
- **Requirements:** Founder of project
- **Permissions:** Full admin access to repository, infrastructure, trademark
- **Responsibilities:** Vision, security decisions, community leadership
- **Term:** Lifetime (or until voluntary resignation)

#### **Level 3: Core Contributors**
- **Requirements:**
  - 10+ merged PRs over 6+ months
  - Demonstrated expertise in core domains (security, enforcement, compliance)
  - Nominated by BDFL or 2+ existing Core Contributors
  - Accepted by BDFL
- **Permissions:**
  - Direct commit access (with required reviews)
  - Can approve PRs from Verified Contributors
  - Can trigger CI/CD deployments
  - Access to private security issues
- **Responsibilities:**
  - Code review within 5 business days
  - Participate in RFC discussions
  - Mentor Verified Contributors
- **Term:** Indefinite (can be revoked by BDFL for inactivity or violation of Code of Conduct)

**Current Core Contributors:**
- [TBD - To be appointed based on contributions]

#### **Level 2: Verified Contributors**
- **Requirements:**
  - 3+ merged PRs
  - Signed Developer Certificate of Origin (DCO) on all commits
  - No Code of Conduct violations
- **Permissions:**
  - Priority review queue (72-hour SLA for review)
  - Listed in CONTRIBUTORS.md
  - Invited to quarterly contributor calls
  - Can vote on non-technical decisions (documentation, branding)
- **Responsibilities:**
  - Follow contribution guidelines
  - Maintain code quality (tests, documentation)
- **Term:** Automatic promotion (no revocation unless CoC violation)

#### **Level 1: Community Contributors**
- **Requirements:** None (open to all)
- **Permissions:**
  - Submit issues and PRs
  - Participate in GitHub Discussions
  - Access to public documentation
- **Responsibilities:**
  - Follow Code of Conduct
  - Search existing issues before creating duplicates
- **Term:** Ongoing

### 3.3 Promotion Process

**Community → Verified:**
- Automatic after 3rd merged PR
- BDFL or Core Contributor adds to CONTRIBUTORS.md
- GitHub team membership granted

**Verified → Core:**
- Nomination via GitHub issue (template: `.github/ISSUE_TEMPLATE/nominate-core.md`)
- BDFL reviews contribution history
- Public announcement if accepted
- Onboarding session (1 hour) covering security protocols

**Demotion/Removal:**
- Only for Code of Conduct violations or extended inactivity (12+ months)
- BDFL decision (or Core Contributors vote if BDFL unavailable)
- Public announcement with reasoning (unless privacy concerns)

---

## 4. Contribution Rules

### 4.1 Developer Certificate of Origin (DCO)

**All commits MUST include a sign-off:**

```
git commit -s -m "feat: add new feature"

This adds:
Signed-off-by: Your Name your.email@example.com
```


**What this means:**
You certify that:
- (a) You wrote the code yourself, OR
- (b) You have the right to submit it under Apache 2.0, OR
- (c) Someone with (a) or (b) provided it to you, and you're passing it on

**Why we require this:**
- Legal protection for the project and all contributors
- Prevents copyright contamination
- Industry standard (Linux Kernel, Kubernetes, etc.)

**Enforcement:**
- DCO bot checks every commit
- PRs without sign-off are auto-rejected
- No exceptions (including BDFL)

### 4.2 Code Review Requirements

**All PRs require:**
- ✅ **Approval from 1+ Core Contributor** (or BDFL)
- ✅ **All CI checks passing** (tests, linting, security scan)
- ✅ **DCO sign-off on all commits**
- ✅ **No merge conflicts**

**BDFL PRs:**
- Even BDFL code requires review (principle: "trust, but verify")
- Self-merge allowed only for:
  - Emergency security patches (with post-merge review within 24h)
  - Typo fixes in documentation
  - Version bumps

### 4.3 Testing Requirements

**All PRs must include:**
- ✅ **Unit tests** for new functions/classes
- ✅ **Integration tests** for API endpoints
- ✅ **Documentation** for public APIs

**Minimum Coverage:**
- New code: 80% coverage required
- Overall project: 85% coverage maintained

**Exemptions:**
- Documentation-only PRs
- Refactoring with no behavior change (but strongly encouraged)

### 4.4 Commit Message Standards

**Format:** [Conventional Commits](https://www.conventionalcommits.org/)


<type>(<scope>): <subject>

<body> <footer> ```

Types:

feat: New feature

fix: Bug fix

docs: Documentation only

style: Code style (formatting, no logic change)

refactor: Code restructuring (no behavior change)

test: Adding/updating tests

chore: Maintenance (dependencies, CI config)

security: Security patches (use ! for breaking)

Example:

text
feat(enforcement): add kill switch endpoint

Implements NIST AI RMF MANAGE-2.4 emergency stop capability.

Closes #123
Signed-off-by: John Doe <john@example.com>
4.5 Breaking Changes
All breaking changes require:

✅ RFC (Request for Comments) process (14-day comment period)

✅ Migration guide in PR description

✅ Deprecation warnings in prior release (if possible)

✅ BDFL approval

Major version bump required (0.9.x → 1.0.0)

5. Anti-Burnout Protocol (Emergency Brake)
5.1 Purpose
"Sustainable open source requires acknowledging human limits."

This protocol protects the BDFL and Core Contributors from burnout by legitimizing rest without guilt.

5.2 Burnout Indicators
Self-Assessment (Weekly):
Rate yourself 1-10 on:

Enjoyment of working on project (1 = dread, 10 = excited)

Energy levels (1 = exhausted, 10 = energized)

Response to issues/PRs (1 = resentment, 10 = helpful)

Burnout Score = Average of above

5.3 Trigger Conditions
Emergency Brake activates automatically if:

✅ Burnout score ≥ 8/10 for 2+ consecutive weeks

✅ BDFL works 4+ weeks without a 3+ day break

✅ Core Contributor reports burnout to BDFL

Voluntary Activation:

BDFL or Core Contributor can activate for themselves anytime

No explanation required (though transparency appreciated)

5.4 Emergency Brake Actions
When activated:

GitHub Banner (within 24 hours):

text
⚠️ MAINTENANCE MODE: Project in rest period (2-4 weeks)
Only SECURITY issues will be addressed.
Thank you for your patience.
Communication Limits:

Issues: Only security vulnerabilities accepted

PRs: Paused (no new reviews)

Discussions: Read-only mode

Email: Auto-responder with security contact only

Workload Reduction:

Delegate urgent security to Succession Council

Postpone all feature work

Cancel meetings/calls

Rest Period:

Minimum: 2 weeks full break

Maximum: 8 weeks (extended by Succession Council if needed)

5.5 Return Protocol
Gradual re-entry:

Week 1: 4 hours/week (read issues, no responses)

Week 2: 8 hours/week (respond to critical issues only)

Week 3: 12 hours/week (resume PR reviews)

Week 4: 20 hours/week (full capacity)

Re-assessment:

If burnout returns, extend rest period

Consider recruiting additional Core Contributors

5.6 Community Support
What the community can do:

✅ Respect maintenance mode (don't pressure for updates)

✅ Help triage issues (label: security vs. feature)

✅ Review each other's PRs (even without merge access)

✅ Improve documentation while BDFL rests

What the community should NOT do:

❌ Email/DM maintainers during maintenance mode (except security)

❌ Post "when will this be fixed?" comments

❌ Fork the project out of impatience (permitted by license, but discouraged)

6. Conflict Resolution
6.1 Technical Disagreements
Process:

Discussion: Open GitHub Discussion thread

RFC: If no consensus after 7 days, create RFC document

Community Input: 14-day comment period

BDFL Decision: Final decision with written rationale

Appeal: Can be re-opened after 6 months with new evidence

Example:

Issue: "Should we support MongoDB in addition to PostgreSQL?"

Discussion: Community debates trade-offs

BDFL Decision: "No, PostgreSQL-only for v1.0 to maintain focus. Revisit in v1.5."

6.2 Interpersonal Conflicts
Code of Conduct Violations:

Report to: conduct@buildtovalue.ai (goes to BDFL + Legal Advisor)

Response: Within 72 hours

Investigation: Private, confidential

Resolution: Warning, temporary ban, or permanent ban

Process:

Complainant files report (template provided)

BDFL + Legal Advisor review

Accused notified and given right to respond

Decision made within 14 days

Both parties notified of outcome

Public summary (anonymized) if appropriate

6.3 Commercial Conflicts
Example: Contributor's employer wants feature that doesn't benefit community

Resolution:

BDFL evaluates: "Does this feature help 80%+ of users?"

If NO: Suggest employer maintains as private fork or funds general feature

If YES but needs resources: Discuss sponsorship/Enterprise partnership

7. Amendment Process
7.1 Proposing Changes
Anyone can propose changes to this document via:

Open GitHub issue with governance label

Describe proposed change and rationale

Community discussion (21-day comment period)

BDFL decision

7.2 Approval Requirements
Change Type	Approval Required
Typo/clarification	BDFL (fast-track)
Process improvement	BDFL + 2 Core Contributors
Authority structure	BDFL + Succession Council unanimous
License change	Impossible (Apache 2.0 is irrevocable)
7.3 Version History
v1.0 (2025-12-26): Initial governance model

[Future versions tracked here]

8. Legal Framework
8.1 Jurisdiction
This governance document is governed by the laws of [Your Jurisdiction] (e.g., State of Delaware, USA).

Note: Actual legal disputes are rare in open source. This clause primarily clarifies which legal system applies if needed.

8.2 Limitation of Liability
All contributors (including BDFL) participate at their own risk.

Per Apache License 2.0 Section 7:

"Unless required by applicable law [...] in no event and under no legal theory [...] shall any Contributor be liable to You for damages."

Translation: Contributors are volunteers. We build secure software, but we're not liable if something breaks in your production system. Use at your own risk.

8.3 Trademark
"BuildToValue" and the BTV logo are trademarks of [Your Legal Entity].

Permitted use:

✅ Describing the software ("powered by BuildToValue")

✅ Linking to official repository

✅ Academic/research citations

Prohibited use:

❌ Implying endorsement ("BuildToValue-certified product")

❌ Creating confusion (naming product "BuildToValue Pro")

❌ Commercial use in product names without permission

Contact trademark@buildtovalue.ai for licensing inquiries.

8.4 Patent Grant
Per Apache License 2.0 Section 3:

"Each Contributor [...] grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable [...] patent license."

Translation: If you contribute code, you also grant patent rights. You can't later sue users for patent infringement based on your contribution.

9. Appendices
Appendix A: Glossary
BDFL: Benevolent Dictator for Life (founder with final authority)

DCO: Developer Certificate of Origin (legal sign-off on commits)

RFC: Request for Comments (formal proposal process)

CoC: Code of Conduct

PR: Pull Request

CI/CD: Continuous Integration / Continuous Deployment

Appendix B: Key Contacts
Role	Email	Response SLA
BDFL	bdfl@buildtovalue.ai	72 hours
Security	security@buildtovalue.ai	48 hours
Code of Conduct	conduct@buildtovalue.ai	72 hours
Legal	legal@buildtovalue.ai	5 business days
General	hello@buildtovalue.ai	Best effort
Appendix C: Templates
Nominate Core Contributor:

.github/ISSUE_TEMPLATE/nominate-core.md

RFC Template:

.github/ISSUE_TEMPLATE/rfc.md

Code of Conduct Report:

.github/ISSUE_TEMPLATE/conduct-report.md (private repo)

10. Acknowledgments
This governance model was inspired by:

Python (Guido van Rossum's BDFL model)

Linux Kernel (Linus Torvalds' model + DCO)

Rust (RFC process + community input)

Django (Core Contributor structure)

Node.js (Technical Steering Committee failover)

Special thanks to:

TODO Group for open source governance best practices

Contributor Covenant for Code of Conduct framework

Open Source Initiative for licensing guidance

Signatures
Adopted by:

Daniel Lau Pereira Soares, BDFL
Date: December 26, 2025
GitHub: @danzeroum

This document is version controlled in Git. The canonical version is always at:
https://github.com/danzeroum/buildtovalue-governance/blob/main/GOVERNANCE.md

Questions? Open a GitHub Discussion:
https://github.com/danzeroum/buildtovalue-governance/discussions

END OF GOVERNANCE DOCUMENT

"Good governance is not about control—it's about clarity."
— BuildToValue Community