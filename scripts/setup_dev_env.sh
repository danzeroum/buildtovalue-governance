#!/bin/bash
# Setup de ambiente de desenvolvimento
# Execução: ./scripts/setup_dev_env.sh

set -euo pipefail

echo "=========================================="
echo "🚀 BuildToValue - Development Setup"
echo "=========================================="
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
echo "✅ Python $PYTHON_VERSION detected"

# Cria virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Instala dependências
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Cria estrutura de diretórios
echo ""
echo "📁 Creating directory structure..."
mkdir -p data/compliance_memory
mkdir -p logs
mkdir -p secrets
mkdir -p reports

# Gera secrets
echo ""
echo "🔐 Generating development secrets..."
./scripts/rotate_secrets.sh

# Cria .env
echo ""
echo "⚙️  Creating .env file..."
cat > .env << EOF
# BuildToValue Development Environment
ENVIRONMENT=development
JWT_SECRET=$(cat secrets/jwt_secret.txt)
HMAC_KEY=$(cat secrets/hmac_key.txt)
DB_URL=sqlite:///./data/btv_registry.db
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ Development environment ready!"
echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "3. Start development server:"
echo "   uvicorn src.interface.api.gateway:app --reload"
echo ""
echo "4. Access API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "5. Generate admin token:"
echo "   python scripts/generate_token.py --role admin --tenant global_admin"
echo ""
echo "=========================================="
echo ""
