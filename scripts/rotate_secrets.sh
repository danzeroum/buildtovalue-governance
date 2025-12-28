#!/bin/bash

# BuildToValue v0.9.0 - Secret Rotation
# Purpose: Automate secret rotation per ISO 42001 B.6.1.2
# Usage: ./scripts/rotate_secrets.sh
# Frequency: Every 90 days
# Compatibility: Linux, macOS, WSL

set -euo pipefail

SECRETS_DIR="./secrets"
BACKUP_DIR="./secrets/backup_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "🔐 BuildToValue - Secret Rotation"
echo "ISO 42001 B.6.1.2 Compliance"
echo "Version: 0.9.0"
echo "=========================================="
echo ""

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

# Check OpenSSL
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL not found. Install it first:"
    echo "   Mac: brew install openssl"
    echo "   Ubuntu/Debian: sudo apt-get install openssl"
    echo "   RHEL/CentOS: sudo yum install openssl"
    exit 1
fi

# ============================================================================
# BACKUP EXISTING SECRETS
# ============================================================================

if [ -d "$SECRETS_DIR" ]; then
    echo "📦 Creating backup of current secrets..."
    mkdir -p "$BACKUP_DIR"

    # Backup all .txt files (if any exist)
    if ls "$SECRETS_DIR"/*.txt 1> /dev/null 2>&1; then
        cp "$SECRETS_DIR"/*.txt "$BACKUP_DIR/" 2>/dev/null || true
        echo "✅ Backup saved to: $BACKUP_DIR"
    else
        echo "ℹ️  No existing secrets found to backup"
    fi
else
    echo "ℹ️  No existing secrets directory. Creating new one..."
fi

echo ""

# ============================================================================
# GENERATE NEW SECRETS
# ============================================================================

# Create secrets directory
mkdir -p "$SECRETS_DIR"

echo "🔑 Generating new secrets..."
echo ""

# JWT Secret (256-bit for HS256)
echo " → jwt_secret.txt (256-bit for HS256)"
openssl rand -hex 32 > "$SECRETS_DIR/jwt_secret.txt"

# HMAC Key (256-bit for ledger integrity)
echo " → hmac_key.txt (256-bit for ledger integrity)"
openssl rand -hex 32 > "$SECRETS_DIR/hmac_key.txt"

# Database Password (base64 encoded)
echo " → db_password.txt (32 bytes base64)"
openssl rand -base64 32 > "$SECRETS_DIR/db_password.txt"

# API Key (for M2M authentication)
echo " → api_key.txt (256-bit)"
openssl rand -hex 32 > "$SECRETS_DIR/api_key.txt"

# ============================================================================
# SET RESTRICTIVE PERMISSIONS (ISO 42001 B.4.2)
# ============================================================================

chmod 600 "$SECRETS_DIR"/*.txt  # Files: owner read/write only
chmod 700 "$SECRETS_DIR"         # Directory: owner rwx only

# Add .gitkeep to preserve directory structure in Git
touch "$SECRETS_DIR/.gitkeep"

echo ""
echo "✅ Secrets generated successfully!"
echo "✅ Permissions set (600 for files, 700 for directory)"
echo ""

# ============================================================================
# CALCULATE NEXT ROTATION DATE (Cross-platform)
# ============================================================================

# macOS uses different date syntax than Linux
if date -v+90d > /dev/null 2>&1; then
    # macOS (BSD date)
    NEXT_ROTATION=$(date -v+90d "+%Y-%m-%d")
else
    # Linux (GNU date)
    NEXT_ROTATION=$(date -d '+90 days' '+%Y-%m-%d')
fi

# ============================================================================
# POST-ROTATION INSTRUCTIONS
# ============================================================================

echo "=========================================="
echo "⚠️  REQUIRED ACTIONS:"
echo "=========================================="
echo ""
echo "1. Update environment variables:"
echo "   export JWT_SECRET=\$(cat $SECRETS_DIR/jwt_secret.txt)"
echo "   export HMAC_KEY=\$(cat $SECRETS_DIR/hmac_key.txt)"
echo ""
echo "2. Restart services:"
echo "   # Docker Compose"
echo "   docker-compose restart btv-api"
echo ""
echo "   # Systemd"
echo "   systemctl restart buildtovalue"
echo ""
echo "   # Development"
echo "   # Press Ctrl+C and restart: uvicorn src.interface.api.gateway:app --reload"
echo ""
echo "3. Revoke old JWT tokens:"
echo "   curl -X POST http://localhost:8000/v1/auth/revoke-all \\"
echo "        -H 'Authorization: Bearer \$ADMIN_TOKEN'"
echo ""
echo "4. Update secrets in infrastructure:"
echo "   ✓ GitHub Secrets (CI/CD)"
echo "   ✓ Docker Secrets"
echo "   ✓ Kubernetes Secrets"
echo "   ✓ Cloud Provider Secrets Manager (AWS/GCP/Azure)"
echo ""
echo "=========================================="
echo "📅 Next rotation: $NEXT_ROTATION"
echo "   (90 days from now - ISO 42001 requirement)"
echo "=========================================="
echo ""
echo "📋 Backup location: $BACKUP_DIR"
echo "   Keep this backup for 30 days (audit trail)"
echo ""
