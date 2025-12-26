# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 7.3.x   | :white_check_mark: |
| 7.2.x   | :x:                |
| < 7.0   | :x:                |

## Reporting a Vulnerability

**⚠️ DO NOT open public issues for security vulnerabilities.**

### Responsible Disclosure Process

1. **Email**: Send details to security@buildtovalue.ai (PGP key available)
2. **Acknowledgment**: We'll respond within 48 hours
3. **Investigation**: 7-14 days for validation and patch development
4. **Disclosure**: Coordinated disclosure after patch release

### What to Include

- Type of vulnerability (SQL Injection, BOLA, etc.)
- Steps to reproduce
- Proof of Concept (if available)
- Potential impact assessment

### Security Bounty Program

We reward responsible disclosures:

| Severity | Bounty |
|----------|--------|
| Critical (RCE, Auth Bypass) | $500-$2000 |
| High (BOLA, SQL Injection) | $200-$500 |
| Medium (XSS, CSRF) | $50-$200 |
| Low (Information Disclosure) | $20-$50 |

### Hall of Fame

- [Your Name Here] - First security researcher to contribute!

## Security Features

BuildToValue implements defense-in-depth:

- **Authentication**: JWT with short expiration (30 min default)
- **Authorization**: RBAC with 4 roles (admin, dev, auditor, app)
- **Data Isolation**: Multi-tenant UUID validation
- **Audit Trail**: HMAC-signed ledger (tamper-proof)
- **Input Validation**: Pydantic schemas with whitelist approach
- **SQL Injection Prevention**: SQLAlchemy ORM (no raw queries)
- **Secrets Management**: Environment variables + Docker secrets
- **Rate Limiting**: Built-in DoS protection

## Compliance

BuildToValue is designed for high-security environments:

- ✅ ISO/IEC 42001:2023 (AI Management System)
- ✅ ISO/IEC 27001:2022 (Information Security)
- ✅ EU AI Act (Art. 5, 12, 14, 15)
- ✅ GDPR (Art. 25, 32)

[View compliance mapping →](docs/compliance/ISO_42001_MAPPING.md)
