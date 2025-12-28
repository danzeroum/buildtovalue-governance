# 🛠️ BuildToValue Operation Scripts

This directory contains essential tools for the operation, maintenance, and auditing of BuildToValue Governance.

---

## 📋 Available Tools

### 1. Governance and Compliance

#### `generate_compliance_report.py` ⭐
Generates executive compliance reports (HTML/JSON) certifying the effectiveness of blocks against supported regulations.

**Usage:**
Standard report (Fintech Gold Master)
python scripts/generate_compliance_report.py

Custom report with multi-sector data
python scripts/generate_compliance_report.py
--multi-sector reports/multi_sector_results.json
--output reports/audit_q1_2026.html


**Output:**
- Executive HTML report
- Structured JSON for integration with audit tools
- Compatible with ISO 42001 and EU AI Act Art. 72 (Transparency)

**Recommended Frequency:** Quarterly or before external audits

---

#### `validate_ledger.py` 🔐
Verifies the cryptographic integrity (HMAC) of decision logs. Essential for forensic audits.

**Usage:**
Validate default ledger
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

Validate custom ledger
python scripts/validate_ledger.py /path/to/custom_ledger.jsonl


**Alert:** Detects if any log line has been manually altered (tampering).

**When to Execute:**
- Weekly (security routine)
- Before external audits
- After suspected security incidents

**Compliance:** ISO 42001 Art. 9.1 (Monitoring) + EU AI Act Art. 12 (Record-keeping)

---

### 2. Security and Access

#### `rotate_secrets.sh` 🔄
Automates the rotation of secrets (JWT Secrets, HMAC Keys, DB Passwords) as required by ISO 42001 (Control B.6.1.2).

**Usage:**
Linux/Mac
./scripts/rotate_secrets.sh

If needed, grant execution permission first:
chmod +x scripts/rotate_secrets.sh


**What is rotated:**
- `JWT_SECRET_KEY` (user authentication)
- `HMAC_SECRET_KEY` (ledger integrity)
- `DATABASE_PASSWORD` (if applicable)

**Recommended Frequency:** Every 90 days (ISO 42001 requirement)

**⚠️ Warning:** 
- Create backup of `.env` before rotation
- JWT tokens issued before rotation will be invalidated
- Restart the server after rotation

---

#### `generate_token.py` 🎫
JWT token generator for administrative access or system integration (M2M).

**Usage - Admin Bootstrap:**
Create initial admin token (90 days)
python scripts/generate_token.py
--role admin
--tenant global_admin
--days 90


**Usage - M2M Application:**
Token for integrated system (365 days)
python scripts/generate_token.py
--role app
--tenant <tenant_uuid>
--days 365
--user "HR System"


**Usage - Developer:**
Dev token (30 days)
python scripts/generate_token.py
--role dev
--tenant <tenant_uuid>
--user dev@company.com
--days 30


**When to Use:**
- **Initial bootstrap:** Create first admin after installation
- **M2M integration:** External systems need to access API
- **Access recovery:** Admin lost credentials
- **Development testing:** Generate tokens for test environments

---

### 3. Development

#### `setup_dev_env.sh` 🚀
Configures local development environment (venv, dependencies, initial secrets).

**Usage:**
Linux/Mac
./scripts/setup_dev_env.sh

If needed, grant execution permission first:
chmod +x scripts/setup_dev_env.sh


**What is configured:**
- Creates Python virtual environment (.venv)
- Installs dependencies from `requirements.txt`
- Generates initial `.env` with random secrets
- Creates folder structure (logs/, reports/)
- Initializes SQLite database

**When to Use:**
- Onboarding new developers
- CI/CD environment setup
- Complete reset of local environment

---
## 🪟 Platform-Specific Scripts

BuildToValue provides native scripts for all major platforms:

| Platform | Setup Script | Rotate Secrets | Notes |
|----------|--------------|----------------|-------|
| **Linux/macOS** | `setup_dev_env.sh` | `rotate_secrets.sh` | Bash 4.0+ |
| **Windows** | `setup_dev_env.ps1` | `rotate_secrets.ps1` | PowerShell 5.1+ |
| **Cross-platform** | Git Bash, WSL | Git Bash, WSL | Alternative for Windows |

### Running Scripts on Windows

**Option 1: PowerShell (Recommended)**
Setup environment
.\scripts\setup_dev_env.ps1

Rotate secrets
.\scripts\rotate_secrets.ps1

**Option 2: Git Bash**
Setup environment
bash scripts/setup_dev_env.sh

Rotate secrets
bash scripts/rotate_secrets.sh

**Option 3: WSL (Windows Subsystem for Linux)**
Setup environment
./scripts/setup_dev_env.sh

Rotate secrets
./scripts/rotate_secrets.sh

### Execution Policy (PowerShell Only)

If you get "execution policy" errors:

Check current policy
Get-ExecutionPolicy

Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Or run with bypass (one-time)
powershell -ExecutionPolicy Bypass -File .\scripts\setup_dev_env.ps1


---

## 📊 Tools Summary

| Script | Purpose | Frequency | Criticality |
|--------|---------|-----------|-------------|
| `generate_compliance_report.py` | Executive compliance report | Quarterly | ⭐⭐⭐ |
| `validate_ledger.py` | Forensic log audit | Weekly | ⭐⭐⭐ |
| `rotate_secrets.sh` | Credential rotation | 90 days | ⭐⭐⭐ |
| `generate_token.py` | JWT token generation | On demand | ⭐⭐ |
| `setup_dev_env.sh` | Environment setup | Initial | ⭐⭐ |

---

## 🔒 Security Notes

### Execution Permissions (Linux/Mac)
Grant execution permission to shell scripts
chmod +x scripts/*.sh

Verify permissions
ls -la scripts/


### Secrets Protection
- **NEVER** commit `.env` files to Git
- Use `.env.example` as template (without real values)
- Rotate secrets every 90 days per ISO 42001

### Change Audit
View script execution history
git log --oneline -- scripts/

View who executed secret rotation
git log -p scripts/rotate_secrets.sh


---

## 🆘 Troubleshooting

### Script won't execute (Permission Denied)
Solution: Grant execution permission
chmod +x scripts/<script_name>.sh


### JWT token doesn't work
Possible causes:
1. JWT_SECRET_KEY was rotated (old token invalidated)
2. Token expired (check --days in generation)
3. .env not loaded (check python-dotenv)
Solution: Generate new token
python scripts/generate_token.py --role admin --tenant global_admin --days 90


### Invalid ledger detected
If validate_ledger.py detects tampering:
1. DO NOT delete the ledger (it's forensic evidence)
2. Isolate the file: mv logs/enforcement_ledger.jsonl logs/compromised_$(date +%Y%m%d).jsonl
3. Investigate: review git log, server access audit
4. Create new ledger: restart the server (generates new clean ledger)

---

## 📚 References

- **ISO/IEC 42001:2023** - AI Management System (Clause 9.1 - Monitoring)
- **EU AI Act (Regulation 2024/1689)** - Art. 12 (Record-keeping), Art. 72 (Transparency)
- **NIST AI RMF 1.0** - GOVERN-1.3 (Auditability), MEASURE-2.10 (Logging)
- **Huwyler (2025)** - Threat Taxonomy (arXiv:2511.21901v1 [cs.CR])

---

## 🤝 Contributing

To add new scripts to the toolkit:

1. **Name clearly:** `<verb>_<noun>.py` (e.g., `export_audit_trail.py`)
2. **Document at the top:** Purpose, usage, recommended frequency
3. **Add to README:** Keep this file updated
4. **Test in isolation:** Run in dev environment before commit

**Example structure:**
```
#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - <Tool Name>

Purpose: <Brief description>
Usage: python scripts/<script>.py [options]
Frequency: <When to execute>
"""
```
---

**Maintainer:** BuildToValue Core Team  
**Last Updated:** December 28, 2025  
**Version:** 0.9.0 Gold Master  
**License:** See LICENSE in repository root