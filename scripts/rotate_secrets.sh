#!/bin/bash
# Rotação automática de secrets (ISO 42001 B.6.1.2)
# Execução: ./scripts/rotate_secrets.sh

set -euo pipefail

SECRETS_DIR="./secrets"
BACKUP_DIR="./secrets/backup_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "🔐 BuildToValue - Secret Rotation"
echo "ISO 42001 B.6.1.2 Compliance"
echo "=========================================="
echo ""

# Backup dos secrets atuais
if [ -d "$SECRETS_DIR" ]; then
    echo "📦 Creating backup of current secrets..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$SECRETS_DIR"/*.txt "$BACKUP_DIR/" 2>/dev/null || true
    echo "✅ Backup saved to: $BACKUP_DIR"
else
    echo "ℹ️  No existing secrets found. Creating new ones..."
fi

# Cria diretório de secrets
mkdir -p "$SECRETS_DIR"

# Gera novos secrets
echo ""
echo "🔑 Generating new secrets..."
echo ""

echo "  → jwt_secret.txt (256-bit)"
openssl rand -hex 32 > "$SECRETS_DIR/jwt_secret.txt"

echo "  → hmac_key.txt (256-bit)"
openssl rand -hex 32 > "$SECRETS_DIR/hmac_key.txt"

echo "  → db_password.txt"
openssl rand -base64 32 > "$SECRETS_DIR/db_password.txt"

echo "  → api_key.txt"
openssl rand -hex 32 > "$SECRETS_DIR/api_key.txt"

# Permissões restritas (ISO 42001 B.4.2)
chmod 600 "$SECRETS_DIR"/*.txt
chmod 700 "$SECRETS_DIR"

echo ""
echo "✅ Secrets generated successfully!"
echo ""
echo "=========================================="
echo "⚠️  REQUIRED ACTIONS:"
echo "=========================================="
echo ""
echo "1. Update environment variables:"
echo "   export JWT_SECRET=\$(cat $SECRETS_DIR/jwt_secret.txt)"
echo "   export HMAC_KEY=\$(cat $SECRETS_DIR/hmac_key.txt)"
echo ""
echo "2. Restart services:"
echo "   docker-compose restart btv-api"
echo "   # OR"
echo "   systemctl restart buildtovalue"
echo ""
echo "3. Revoke old JWT tokens:"
echo "   curl -X POST http://localhost:8000/v1/auth/revoke-all \\"
echo "     -H 'Authorization: Bearer \$ADMIN_TOKEN'"
echo ""
echo "4. Update secrets in CI/CD:"
echo "   - GitHub Secrets"
echo "   - Docker Secrets"
echo "   - Kubernetes Secrets"
echo ""
echo "=========================================="
echo "📅 Next rotation: $(date -d '+90 days' '+%Y-%m-%d')"
echo "   (90 days from now - ISO 42001 requirement)"
echo "=========================================="
echo ""
