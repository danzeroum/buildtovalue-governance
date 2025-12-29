# 🔒 Security Policy

**BuildToValue Framework v0.9.0**

This document outlines our security practices, vulnerability reporting process, and best practices for secure deployment.

---

## 📋 Supported Versions

We actively maintain security updates for the following versions:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 0.9.x   | ✅ Yes (Current)   | TBD            |
| 0.8.x   | ⚠️ Security Only   | 2026-03-31     |
| < 0.8   | ❌ No              | EOL            |

**Recommendation:** Always use the latest stable release for production deployments.

---

## 🚨 Reporting a Vulnerability

### ⚠️ DO NOT Open Public Issues for Security Vulnerabilities

**Secure Reporting Channel:**
- **Email:** [security@buildtovalue.com](mailto:security@buildtovalue.com)
- **PGP Key:** [Download from keybase.io/buildtovalue](https://keybase.io/buildtovalue)
- **Expected Response Time:** 48 hours (business days)
- **Disclosure Timeline:** 90 days coordinated disclosure

### What to Include in Your Report

1. **Description:** Clear summary of the vulnerability
2. **Impact:** Potential security impact (CVSS score if available)
3. **Reproduction:** Step-by-step instructions to reproduce
4. **Environment:** Version, OS, deployment method (Docker/local)
5. **Proposed Fix:** If you have a suggestion (optional)

### Our Commitment

- ✅ Acknowledge receipt within 48 hours
- ✅ Provide initial assessment within 5 business days
- ✅ Work with you on coordinated disclosure
- ✅ Credit you in security advisories (unless you prefer anonymity)

### Security Advisories

Published at: [github.com/danzeroum/buildtovalue-governance/security/advisories](https://github.com/danzeroum/buildtovalue-governance/security/advisories)

---

## 🛡️ Security Architecture

### Core Security Principles

BuildToValue implements **defense in depth** across multiple layers:

#### 1. Authentication & Authorization
- **JWT Tokens:** RS256 signed with 4096-bit keys
- **Token Expiration:** Default 8 hours (configurable)
- **RBAC:** Role-Based Access Control (4 levels: admin, dev, auditor, app)
- **Tenant Isolation:** Every query validates `tenant_id` from token claims
```
Example: Tenant isolation enforcement
system = registry.get_system(
system_id=requested_id,
requesting_tenant=token.tenant_id # CRITICAL: prevents BOLA
)
```

#### 2. Cryptographic Integrity
- **HMAC-SHA256:** All audit logs digitally signed
- **Key Rotation:** Automated 90-day rotation via `rotate_secrets.sh`
- **Constant-Time Comparison:** `hmac.compare_digest()` prevents timing attacks

```
Example: HMAC signature verification
signature = hmac.new(
key=HMAC_KEY.encode(),
msg=canonical_entry.encode(),
digestmod=hashlib.sha256
).hexdigest()
```


#### 3. Input Validation
- **Pydantic Schemas:** Strict type validation on all API inputs
- **UUID Validation:** Tenant IDs must be valid UUIDv4
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **Path Traversal Protection:** Absolute paths + `..` sanitization

#### 4. Threat Detection (NEW v0.9.0)
- **Huwyler Taxonomy:** 133 real-world incidents validated
- **Pattern Matching:** Keyword-based threat classification
- **Statistical Priors:** Fallback to MISUSE (61% of incidents)

```
Example: Threat classification
result = classifier.classify([
"Prompt injection detected",
"PII leakage in output"
])

{"primary_threat": "misuse", "confidence": 0.85}
```

#### 5. Kill Switch (Emergency Stop)
- **Instant Halt:** Block all operations with `EMERGENCY_STOP` status
- **NIST MANAGE-2.4:** Compliant with AI RMF operational controls
- **Audit Trail:** All emergency stops logged with operator ID

```
Example: Emergency stop enforcement
if system.operational_status == OperationalStatus.EMERGENCY_STOP:
return Decision(
outcome="BLOCKED",
reason="KILL_SWITCH_ACTIVE",
risk_score=10.0
)
```

---

## 🔐 Security Best Practices

### 1. Secrets Management

#### ❌ NEVER Do This
```
DON'T: Hardcode secrets in code
JWT_SECRET = "my-secret-key"
HMAC_KEY = "12345"
```
#### ✅ ALWAYS Do This
```
Generate strong secrets
export JWT_SECRET=$(openssl rand -hex 32)
export HMAC_KEY=$(openssl rand -hex 32)

Store in .env (add to .gitignore)
echo "JWT_SECRET=$JWT_SECRET" >> .env
echo "HMAC_KEY=$HMAC_KEY" >> .env
```
Rotate every 90 days
./scripts/rotate_secrets.sh

### 2. Production Deployment

#### Use Secure Docker Compose
❌ DON'T use default docker-compose.yml (development only)
docker-compose up

✅ DO use secure configuration
docker-compose -f docker-compose.secure.yml up -d

```
**Key differences in `docker-compose.secure.yml`:**
- Read-only root filesystem
- No privileged mode
- Resource limits enforced
- Health checks enabled
- Secrets via Docker secrets (not environment variables)
```

### 3. Environment Configuration

#### Minimum Security Checklist

1. Strong secrets (32+ bytes)
```
2. [ ${#JWT_SECRET} -ge 64 ] && echo "✅ JWT_SECRET OK" || echo "❌ JWT_SECRET TOO SHORT"
```

2. HTTPS only in production
```
export ENFORCE_HTTPS=true
```

3. Rate limiting enabled 
```
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_PER_MINUTE=100
```
4. Production mode
```
export ENV=production
```

5. Disable debug mode
```
export DEBUG=false
```
### 4. Network Security

#### API Gateway Protection
```
Example: Nginx reverse proxy configuration
location /api/ {
```

# Rate limiting
```
limit_req zone=api burst=10 nodelay;
```

# HTTPS redirect
```
if ($scheme != "https") {
    return 301 https://$host$request_uri;
}
```

# Security headers
```
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";

proxy_pass http://btv-gateway:8000;
}
```
### 5. Database Security

#### PostgreSQL Hardening
```
-- Create dedicated user (not root)
CREATE USER btv_app WITH PASSWORD 'strong-password';

-- Grant minimal privileges
GRANT CONNECT ON DATABASE buildtovalue TO btv_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO btv_app;
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM btv_app;

-- Enable SSL connections only
ALTER DATABASE buildtovalue SET ssl = on;
```

### 6. Monitoring & Alerting

#### Critical Events to Monitor
alerts.yml
alerts:

name: "Emergency Stop Activated"
condition: operational_status == "emergency_stop"
severity: CRITICAL
notify: ["security@company.com", "ciso@company.com"]

name: "HMAC Validation Failed"
condition: ledger_integrity < 100%
severity: CRITICAL
notify: ["security@company.com"]

name: "Multiple Failed Authentications"
condition: failed_auth_count > 5 in 5min
severity: HIGH
notify: ["security@company.com"]

name: "Blocked Prompt Spike"
condition: blocked_rate > 50% in 10min
severity: MEDIUM
notify: ["ops@company.com"]

text

---

## 🔍 Security Audit History

### Internal Audits

| Date       | Scope                          | Findings    | Status   |
|------------|--------------------------------|-------------|----------|
| 2025-12-26 | OWASP API Top 10 2023          | 0 HIGH      | ✅ Pass  |
| 2025-12-20 | HMAC Ledger Integrity          | 0 HIGH      | ✅ Pass  |
| 2025-12-15 | Multi-Tenant Isolation (BOLA)  | 0 HIGH      | ✅ Pass  |

### Third-Party Audits

| Provider | Date | Report | Status |
|----------|------|--------|--------|
| TBD      | Q1 2026 | Pending | 🔄 Scheduled |

**Planning:** We are scheduling our first third-party security audit for Q1 2026.

---

## 🚧 Known Security Considerations

### 1. Default HMAC Key Warning (Development)

**Issue:** Development environment uses a default HMAC key for convenience.

**Risk:** If deployed to production without changing, audit logs could be forged.

**Mitigation:**
enforcement.py (line ~50)
if os.getenv("HMAC_KEY") is None:
if os.getenv("ENV") == "production":
raise EnvironmentError("HMAC_KEY must be set in production!")
logger.warning("⚠️ USING DEFAULT HMAC KEY - NOT FOR PRODUCTION USE")

text

**Status:** ✅ Fixed in v0.9.0 (fails fast in production)

### 2. Rate Limiting (Application Layer)

**Issue:** Built-in rate limiting is basic (in-memory, per-process).

**Risk:** Distributed deployments may allow higher request rates than intended.

**Mitigation:**
- Use external rate limiter (Redis-backed) for production
- Deploy Nginx/API Gateway with rate limiting
- See `docs/deployment/RATE_LIMITING.md`

**Status:** ⚠️ Documented (external solution recommended)

### 3. Secret Rotation During Deployment

**Issue:** JWT token rotation invalidates all active sessions.

**Risk:** Users may experience unexpected logouts during secret rotation.

**Mitigation:**
- Rotate secrets during maintenance windows
- Implement grace period (accept both old/new keys for 1 hour)
- See `scripts/rotate_secrets.sh --grace-period`

**Status:** ⚠️ Documented (operational consideration)

---

## 🛠️ Security Tools & Scripts

### Validate Ledger Integrity
Check HMAC signatures
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

Expected output:
✅ 1000 entries validated
✅ 100% integrity
text

### Rotate Secrets
Rotate JWT and HMAC keys
./scripts/rotate_secrets.sh

With grace period (recommended for production)
./scripts/rotate_secrets.sh --grace-period 3600

text

### Security Scan (Static Analysis)
Install tools
pip install bandit safety

Scan for common vulnerabilities
bandit -r src/ -ll

Check dependencies
safety check

text

### Penetration Testing (OWASP ZAP)
Run automated security scan
docker run -t owasp/zap2docker-stable zap-baseline.py
-t http://localhost:8000
-r zap_report.html

text

---

## 📚 Security Resources

### Internal Documentation
- [Multi-Tenant Security Design](./docs/architecture/MULTI_TENANT_DESIGN.md)
- [OWASP API Security Compliance](./docs/security/OWASP_COMPLIANCE.md)
- [Deployment Security Checklist](./docs/deployment/SECURITY_CHECKLIST.md)

### External Standards
- [OWASP API Security Top 10 2023](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Docker Benchmarks](https://www.cisecurity.org/benchmark/docker)
- [SANS Secure Coding](https://www.sans.org/secure-coding/)

### Compliance Frameworks
- [ISO 42001:2023 Annex A.7.5](./docs/compliance/ISO_42001_MAPPING.md) - Data Provenance
- [EU AI Act Art. 15](./docs/compliance/EU_AI_ACT_COMPLIANCE.md) - Accuracy, Robustness, Cybersecurity
- [GDPR Art. 32](https://gdpr.eu/article-32-security-of-processing/) - Security of Processing

---

## 🤝 Security Community

### Bug Bounty Program

**Status:** 🔄 Coming in Q2 2026

**Planned Scope:**
- API endpoints (authentication, enforcement, compliance)
- Multi-tenant isolation (BOLA/IDOR)
- Cryptographic implementations (HMAC, JWT)

**Rewards:** $100 - $5,000 USD (depending on severity)

### Security Champions

We maintain a list of security researchers who have contributed to BuildToValue's security:

- [Add your name by reporting a vulnerability responsibly]

---

## 📞 Contact

- **Security Team:** [security@buildtovalue.com](mailto:security@buildtovalue.com)
- **PGP Key:** [keybase.io/buildtovalue](https://keybase.io/buildtovalue)
- **Security Advisories:** [GitHub Security Tab](https://github.com/danzeroum/buildtovalue-governance/security)

---

## 📜 License & Attribution

This security policy is part of the BuildToValue Framework, licensed under Apache 2.0.

**Open Source Commitment:** All core security features (HMAC Ledger, Kill Switch, Threat Taxonomy, Multi-Tenant Isolation) are 100% Open Source. See [PRODUCT_SCOPE.md](PRODUCT_SCOPE.pt.md) for details.

---

**Version:** 1.0  
**Last Updated:** December 26, 2025  
**Next Review:** March 26, 2026  
**Status:** 🟢 Active