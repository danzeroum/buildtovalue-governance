#!/bin/bash

# BuildToValue v0.9.0 - Development Environment Setup
# Purpose: Automated setup for local development
# Usage: ./scripts/setup_dev_env.sh
# Compatibility: Linux, macOS, WSL

set -euo pipefail

echo "=========================================="
echo "🚀 BuildToValue - Development Setup"
echo "Version: 0.9.0"
echo "=========================================="
echo ""

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

echo "🔍 Running pre-flight checks..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.10+ first."
    echo "   https://www.python.org/downloads/"
    exit 1
fi

# Cross-platform Python version check (works on Mac + Linux)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION detected"

# Check OpenSSL (needed for secret generation)
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL not found. Install it first:"
    echo "   Mac: brew install openssl"
    echo "   Ubuntu/Debian: sudo apt-get install openssl"
    echo "   RHEL/CentOS: sudo yum install openssl"
    exit 1
fi
echo "✅ OpenSSL detected"

# Check Git (optional but recommended)
if command -v git &> /dev/null; then
    echo "✅ Git detected"
else
    echo "⚠️  Git not found (optional, but recommended for version control)"
fi

echo ""

# ============================================================================
# VIRTUAL ENVIRONMENT
# ============================================================================

echo "📦 Creating virtual environment..."
# Use .venv (with dot) to match .gitignore convention
python3 -m venv .venv

# Activate (works on both Linux and macOS)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated (.venv/)"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo ""

# ============================================================================
# DEPENDENCIES
# ============================================================================

echo "📥 Installing dependencies..."
pip install --upgrade pip --quiet

# Core dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✅ Core dependencies installed (requirements.txt)"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Dev dependencies (optional)
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt --quiet
    echo "✅ Dev dependencies installed (requirements-dev.txt)"
else
    echo "⚠️  requirements-dev.txt not found (skipping dev tools)"
fi

echo ""

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

echo "📁 Creating directory structure..."

# Core directories
mkdir -p data/compliance_memory
mkdir -p logs
mkdir -p secrets
mkdir -p reports

# Add .gitkeep to empty directories
touch data/.gitkeep
touch logs/.gitkeep
touch secrets/.gitkeep
touch reports/.gitkeep

echo "✅ Directory structure created"
echo ""

# ============================================================================
# SECRETS GENERATION
# ============================================================================

echo "🔐 Generating development secrets..."

# Check if rotate_secrets.sh exists and is executable
if [ -f "scripts/rotate_secrets.sh" ]; then
    # Make executable if not already
    chmod +x scripts/rotate_secrets.sh

    # Run secret rotation
    ./scripts/rotate_secrets.sh
else
    echo "⚠️  scripts/rotate_secrets.sh not found"
    echo "   Generating secrets manually..."

    mkdir -p secrets
    openssl rand -hex 32 > secrets/jwt_secret.txt
    openssl rand -hex 32 > secrets/hmac_key.txt
    openssl rand -base64 32 > secrets/db_password.txt
    chmod 600 secrets/*.txt

    echo "✅ Secrets generated"
fi

echo ""

# ============================================================================
# ENVIRONMENT FILE
# ============================================================================

echo "⚙️  Creating .env file..."

# Only create if doesn't exist (don't overwrite existing config)
if [ -f ".env" ]; then
    echo "⚠️  .env already exists (keeping existing configuration)"
else
    cat > .env << EOF
# BuildToValue v0.9.0 - Development Environment
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

ENVIRONMENT=development
JWT_SECRET=$(cat secrets/jwt_secret.txt)
HMAC_KEY=$(cat secrets/hmac_key.txt)
DB_URL=sqlite:///./data/btv_registry.db
LOG_LEVEL=INFO

# Optional: Uncomment to enable
# ENABLE_SWAGGER=true
# CORS_ORIGINS=http://localhost:3000
EOF
    echo "✅ .env file created"
fi

echo ""

# ============================================================================
# DATABASE INITIALIZATION (Optional)
# ============================================================================

echo "🗄️  Database initialization..."
if [ -f "src/core/database/init_db.py" ]; then
    python src/core/database/init_db.py
    echo "✅ Database initialized"
else
    echo "ℹ️  No init_db.py found (database will be created on first run)"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "=========================================="
echo "✅ Development environment ready!"
echo "=========================================="
echo ""
echo "📋 Next steps:"
echo "=========================================="
echo ""
echo "1. Activate virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Run tests:"
echo "   pytest tests/ -v --cov=src"
echo ""
echo "3. Start development server:"
echo "   uvicorn src.interface.api.gateway:app --reload"
echo ""
echo "4. Access API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Generate admin token:"
echo "   python scripts/generate_token.py --role admin --tenant global_admin --days 90"
echo ""
echo "6. View test coverage:"
echo "   pytest tests/ --cov=src --cov-report=html"
echo "   open htmlcov/index.html  # Mac"
echo "   start htmlcov/index.html  # Windows"
echo ""
echo "=========================================="
echo "📚 Documentation: docs/DEVELOPMENT.md"
echo "🐛 Issues: github.com/danzeroum/buildtovalue-governance/issues"
echo "=========================================="
echo ""
