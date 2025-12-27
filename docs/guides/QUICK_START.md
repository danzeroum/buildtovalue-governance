# Quick Start Guide

**BuildToValue Framework v0.9**  
**Time to Production:** 15 minutes

---

## Prerequisites

- **Python:** 3.10+
- **Docker:** 20.10+ (recommended)
- **Git:** 2.30+

---

## Option 1: Docker (Fastest) 🚀

### Step 1: Clone Repository

🎉 FINALIZAÇÃO COMPLETA - ÚLTIMOS ARQUIVOS DO PACOTE
📂 DOCUMENTAÇÃO (FINAL)
docs/guides/QUICK_START.md
text
# Quick Start Guide

**BuildToValue Framework v0.9**  
**Time to Production:** 15 minutes

---

## Prerequisites

- **Python:** 3.10+
- **Docker:** 20.10+ (recommended)
- **Git:** 2.30+

---

## Option 1: Docker (Fastest) 🚀

### Step 1: Clone Repository

git clone https://github.com/buildtovalue/btv-framework.git
cd btv-framework

text

### Step 2: Generate Secrets

./scripts/rotate_secrets.sh

text

**Output:**
✅ Secrets generated successfully!
→ jwt_secret.txt (256-bit)
→ hmac_key.txt (256-bit)
→ db_password.txt

text

### Step 3: Start Services

docker-compose up -d

text

**Services:**
- `btv-api` - API Gateway (port 8000)
- `btv-db` - PostgreSQL Database (port 5432)
- `btv-docs` - Documentation (port 8080)

### Step 4: Verify Health

curl http://localhost:8000/health

text

**Response:**
{
"status": "healthy",
"version": "0.9.0",
"security": "hardened"
}

text

✅ **BuildToValue is running!**

---

## Option 2: Local Development

### Step 1: Setup Environment

git clone https://github.com/buildtovalue/btv-framework.git
cd btv-framework

Run setup script
./scripts/setup_dev_env.sh

text

This script:
- Creates Python virtual environment
- Installs dependencies
- Generates secrets
- Creates `.env` file

### Step 2: Activate Virtual Environment

source venv/bin/activate # Linux/Mac

OR
venv\Scripts\activate # Windows

text

### Step 3: Start API Server

uvicorn src.interface.api.gateway:app --reload

text

**Output:**
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.

text

### Step 4: Access API Docs

Open browser: `http://localhost:8000/docs`

---

## First Steps

### 1. Generate Admin Token

python scripts/generate_token.py
--role admin
--tenant global_admin
--days 90

text

**Save the token:**
export BTV_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

text

### 2. Register Your Organization (Tenant)

curl -X POST http://localhost:8000/v1/tenants
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"id": "550e8400-e29b-41d4-a716-446655440000",
"name": "My Company Inc.",
"policy": {
"autonomy_matrix": {
"production": {"max_risk_level": 3.0}
}
}
}'

text

**Response:**
{
"status": "registered",
"tenant_id": "550e8400-e29b-41d4-a716-446655440000",
"message": "Tenant 'My Company Inc.' registered successfully"
}

text

### 3. Register Your AI System

curl -X POST http://localhost:8000/v1/systems
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"id": "my-chatbot-v1",
"name": "Customer Support Chatbot",
"version": "1.0.0",
"sector": "general_commercial",
"role": "deployer",
"risk": "minimal",
"logging_enabled": true,
"jurisdiction": "EU"
}'

text

### 4. Test Enforcement

curl -X POST http://localhost:8000/v1/enforce
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"system_id": "my-chatbot-v1",
"prompt": "Help customer with refund request",
"env": "production"
}'

text

**Response (ALLOWED):**
{
"decision": "ALLOWED",
"risk_score": 2.1,
"limit": 3.0,
"issues": [],
"escalation_required": false
}

text

✅ **Your first governance decision!**

---

## Integration with Your AI Application

### Python Example

import requests
import openai

BTV_API = "http://localhost:8000"
BTV_TOKEN = "your-jwt-token"

def call_ai_with_governance(prompt: str, system_id: str):
"""Call OpenAI with BuildToValue governance"""

text
# 1. Check governance
decision = requests.post(
    f"{BTV_API}/v1/enforce",
    headers={"Authorization": f"Bearer {BTV_TOKEN}"},
    json={
        "system_id": system_id,
        "prompt": prompt,
        "env": "production"
    }
).json()

# 2. If blocked, return error
if decision["decision"] == "BLOCKED":
    return {
        "error": "Blocked by governance",
        "reasons": decision["issues"],
        "review_id": decision.get("review_id")
    }

# 3. If allowed, call AI
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

return {
    "decision": "ALLOWED",
    "risk_score": decision["risk_score"],
    "ai_response": response.choices.message.content
}
Usage
result = call_ai_with_governance(
prompt="Help me understand my credit score",
system_id="my-chatbot-v1"
)
print(result)

text

---

## Next Steps

### Learn More

- **Architecture:** [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
- **API Reference:** [API_REFERENCE.md](../API_REFERENCE.md)
- **Compliance:** [ISO_42001_MAPPING.md](../compliance/ISO_42001_MAPPING.md)
- **Security:** [MULTI_TENANT_DESIGN.md](../architecture/MULTI_TENANT_DESIGN.md)

### Production Deployment

- **Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Docker Compose (Secure):** `docker-compose.secure.yml`
- **Kubernetes:** Coming in v8.0

### Run Tests

Security tests
pytest tests/security/ -v

All tests
pytest tests/ --cov=src --cov-report=html

text

### Generate Compliance Report

python scripts/generate_compliance_report.py --format html --output reports/

text

Open `reports/compliance_report_*.html` in browser.

---

## Troubleshooting

### Port Already in Use

Check what's using port 8000
lsof -i :8000

Kill the process
kill -9 <PID>

text

### Database Connection Error

Check if PostgreSQL is running
docker ps | grep btv-db

Restart database
docker-compose restart btv-db

text

### JWT Token Expired

Generate new token
python scripts/generate_token.py --role admin --tenant global_admin

text

### Import Errors

Ensure PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

text

---

## Support

- **Issues:** https://github.com/buildtovalue/btv-framework/issues
- **Discussions:** https://github.com/buildtovalue/btv-framework/discussions
- **Discord:** https://discord.gg/buildtovalue
- **Email:** support@buildtovalue.com

---

**Happy Governing! 🛡️**