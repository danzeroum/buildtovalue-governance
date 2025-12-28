# BuildToValue v0.9.0 - Development Environment Setup (PowerShell)
# Purpose: Automated setup for local development on Windows
# Usage: .\scripts\setup_dev_env.ps1
# Compatibility: PowerShell 5.1+, PowerShell Core 7+

#Requires -Version 5.1

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 BuildToValue - Development Setup" -ForegroundColor Green
Write-Host "Version: 0.9.0" -ForegroundColor White
Write-Host "Platform: Windows PowerShell" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

Write-Host "🔍 Running pre-flight checks..." -ForegroundColor Yellow
Write-Host ""

# Check Python
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 not found. Install Python 3.10+ first." -ForegroundColor Red
    Write-Host "   Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check pip
try {
    $pipVersion = & python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ pip detected" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ pip not found" -ForegroundColor Red
    exit 1
}

# Check OpenSSL (optional, will use .NET crypto as fallback)
$hasOpenSSL = $false
try {
    $opensslVersion = & openssl version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ OpenSSL detected" -ForegroundColor Green
        $hasOpenSSL = $true
    }
} catch {
    Write-Host "⚠️  OpenSSL not found (will use .NET cryptography)" -ForegroundColor Yellow
}

# Check Git
try {
    $gitVersion = & git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git detected" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Git not found (optional, but recommended)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# VIRTUAL ENVIRONMENT
# ============================================================================

Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow

# Use .venv (with dot) to match project conventions
if (Test-Path ".venv") {
    Write-Host "⚠️  .venv already exists (skipping creation)" -ForegroundColor Yellow
} else {
    & python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created (.venv\)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
$activateScript = ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    # Check execution policy
    $executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
    if ($executionPolicy -eq "Restricted") {
        Write-Host "⚠️  Execution policy is Restricted. Attempting to bypass..." -ForegroundColor Yellow
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    }

    & $activateScript
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Activation script not found: $activateScript" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# DEPENDENCIES
# ============================================================================

Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow

# Upgrade pip
& python -m pip install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

# Core dependencies
if (Test-Path "requirements.txt") {
    & python -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Core dependencies installed (requirements.txt)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install core dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Dev dependencies (optional)
if (Test-Path "requirements-dev.txt") {
    & python -m pip install -r requirements-dev.txt --quiet
    Write-Host "✅ Dev dependencies installed (requirements-dev.txt)" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements-dev.txt not found (skipping dev tools)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# DIRECTORY STRUCTURE
# ============================================================================

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow

# Core directories
$directories = @(
    "data\compliance_memory",
    "logs",
    "secrets",
    "reports"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Add .gitkeep to empty directories
@("data", "logs", "secrets", "reports") | ForEach-Object {
    $gitkeep = Join-Path $_ ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        New-Item -ItemType File -Path $gitkeep -Force | Out-Null
    }
}

Write-Host "✅ Directory structure created" -ForegroundColor Green
Write-Host ""

# ============================================================================
# SECRETS GENERATION
# ============================================================================

Write-Host "🔐 Generating development secrets..." -ForegroundColor Yellow

# Check if rotate_secrets.ps1 exists
$rotateScript = "scripts\rotate_secrets.ps1"
if (Test-Path $rotateScript) {
    # Run secret rotation script
    & $rotateScript
} else {
    Write-Host "⚠️  scripts\rotate_secrets.ps1 not found" -ForegroundColor Yellow
    Write-Host "   Generating secrets manually..." -ForegroundColor Yellow

    # Ensure secrets directory exists
    if (-not (Test-Path "secrets")) {
        New-Item -ItemType Directory -Path "secrets" -Force | Out-Null
    }

    # Generate secrets using .NET cryptography
    Add-Type -AssemblyName System.Security

    # JWT Secret (256-bit / 32 bytes)
    $jwtBytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($jwtBytes)
    $jwtSecret = [System.BitConverter]::ToString($jwtBytes).Replace("-", "").ToLower()
    $jwtSecret | Out-File -FilePath "secrets\jwt_secret.txt" -Encoding ASCII -NoNewline

    # HMAC Key (256-bit / 32 bytes)
    $hmacBytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($hmacBytes)
    $hmacKey = [System.BitConverter]::ToString($hmacBytes).Replace("-", "").ToLower()
    $hmacKey | Out-File -FilePath "secrets\hmac_key.txt" -Encoding ASCII -NoNewline

    # Database Password (32 bytes base64)
    $dbBytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($dbBytes)
    $dbPassword = [Convert]::ToBase64String($dbBytes)
    $dbPassword | Out-File -FilePath "secrets\db_password.txt" -Encoding ASCII -NoNewline

    # Set restrictive permissions (equivalent to chmod 600)
    $acl = Get-Acl "secrets"
    $acl.SetAccessRuleProtection($true, $false)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
        "FullControl",
        "Allow"
    )
    $acl.SetAccessRule($rule)
    Set-Acl "secrets" $acl

    Write-Host "✅ Secrets generated" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# ENVIRONMENT FILE
# ============================================================================

Write-Host "⚙️  Creating .env file..." -ForegroundColor Yellow

# Only create if doesn't exist
if (Test-Path ".env") {
    Write-Host "⚠️  .env already exists (keeping existing configuration)" -ForegroundColor Yellow
} else {
    $jwtSecret = Get-Content "secrets\jwt_secret.txt" -Raw
    $hmacKey = Get-Content "secrets\hmac_key.txt" -Raw

    $envContent = @"
# BuildToValue v0.9.0 - Development Environment
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")

ENVIRONMENT=development
JWT_SECRET=$jwtSecret
HMAC_KEY=$hmacKey
DB_URL=sqlite:///./data/btv_registry.db
LOG_LEVEL=INFO

# Optional: Uncomment to enable
# ENABLE_SWAGGER=true
# CORS_ORIGINS=http://localhost:3000
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env file created" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# DATABASE INITIALIZATION (Optional)
# ============================================================================

Write-Host "🗄️  Database initialization..." -ForegroundColor Yellow
if (Test-Path "src\core\database\init_db.py") {
    & python src\core\database\init_db.py
    Write-Host "✅ Database initialized" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No init_db.py found (database will be created on first run)" -ForegroundColor Cyan
}

Write-Host ""

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Development environment ready!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Activate virtual environment:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run tests:" -ForegroundColor White
Write-Host "   pytest tests\ -v --cov=src" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start development server:" -ForegroundColor White
Write-Host "   uvicorn src.interface.api.gateway:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access API docs:" -ForegroundColor White
Write-Host "   http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Generate admin token:" -ForegroundColor White
Write-Host "   python scripts\generate_token.py --role admin --tenant global_admin --days 90" -ForegroundColor Gray
Write-Host ""
Write-Host "6. View test coverage:" -ForegroundColor White
Write-Host "   pytest tests\ --cov=src --cov-report=html" -ForegroundColor Gray
Write-Host "   start htmlcov\index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📚 Documentation: docs\DEVELOPMENT.md" -ForegroundColor White
Write-Host "🐛 Issues: github.com/danzeroum/buildtovalue-governance/issues" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
