# BuildToValue v0.9.0 - Secret Rotation (PowerShell)
# Purpose: Automate secret rotation per ISO 42001 B.6.1.2
# Usage: .\scripts\rotate_secrets.ps1
# Frequency: Every 90 days
# Compatibility: PowerShell 5.1+, PowerShell Core 7+

#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SecretsDir = "secrets"
$BackupDir = "secrets\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔐 BuildToValue - Secret Rotation" -ForegroundColor Green
Write-Host "ISO 42001 B.6.1.2 Compliance" -ForegroundColor White
Write-Host "Version: 0.9.0" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

# Check if .NET cryptography is available (always true on Windows)
try {
    Add-Type -AssemblyName System.Security
    Write-Host "✅ .NET Cryptography available" -ForegroundColor Green
} catch {
    Write-Host "❌ .NET Framework not properly configured" -ForegroundColor Red
    exit 1
}

# Check for OpenSSL (optional)
$hasOpenSSL = $false
try {
    $opensslVersion = & openssl version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ OpenSSL detected (will use for secret generation)" -ForegroundColor Green
        $hasOpenSSL = $true
    }
} catch {
    Write-Host "ℹ️  OpenSSL not found (will use .NET cryptography)" -ForegroundColor Cyan
}

Write-Host ""

# ============================================================================
# BACKUP EXISTING SECRETS
# ============================================================================

if (Test-Path $SecretsDir) {
    Write-Host "📦 Creating backup of current secrets..." -ForegroundColor Yellow

    # Create backup directory
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

    # Backup all .txt files
    $secretFiles = Get-ChildItem -Path $SecretsDir -Filter "*.txt" -ErrorAction SilentlyContinue
    if ($secretFiles) {
        foreach ($file in $secretFiles) {
            Copy-Item $file.FullName -Destination $BackupDir
        }
        Write-Host "✅ Backup saved to: $BackupDir" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  No existing secrets found to backup" -ForegroundColor Cyan
    }
} else {
    Write-Host "ℹ️  No existing secrets directory. Creating new one..." -ForegroundColor Cyan
}

Write-Host ""

# ============================================================================
# GENERATE NEW SECRETS
# ============================================================================

# Ensure secrets directory exists
if (-not (Test-Path $SecretsDir)) {
    New-Item -ItemType Directory -Path $SecretsDir -Force | Out-Null
}

Write-Host "🔑 Generating new secrets..." -ForegroundColor Yellow
Write-Host ""

# Function to generate random hex string
function New-RandomHex {
    param([int]$Bytes)

    if ($hasOpenSSL) {
        # Use OpenSSL
        $result = & openssl rand -hex $Bytes 2>&1
        return $result.Trim()
    } else {
        # Use .NET crypto
        $randomBytes = New-Object byte[] $Bytes
        $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::Create()
        $rng.GetBytes($randomBytes)
        return [System.BitConverter]::ToString($randomBytes).Replace("-", "").ToLower()
    }
}

# Function to generate random base64 string
function New-RandomBase64 {
    param([int]$Bytes)

    if ($hasOpenSSL) {
        # Use OpenSSL
        $result = & openssl rand -base64 $Bytes 2>&1
        return $result.Trim()
    } else {
        # Use .NET crypto
        $randomBytes = New-Object byte[] $Bytes
        $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::Create()
        $rng.GetBytes($randomBytes)
        return [Convert]::ToBase64String($randomBytes)
    }
}

# JWT Secret (256-bit for HS256)
Write-Host " → jwt_secret.txt (256-bit for HS256)" -ForegroundColor White
$jwtSecret = New-RandomHex -Bytes 32
$jwtSecret | Out-File -FilePath "$SecretsDir\jwt_secret.txt" -Encoding ASCII -NoNewline

# HMAC Key (256-bit for ledger integrity)
Write-Host " → hmac_key.txt (256-bit for ledger integrity)" -ForegroundColor White
$hmacKey = New-RandomHex -Bytes 32
$hmacKey | Out-File -FilePath "$SecretsDir\hmac_key.txt" -Encoding ASCII -NoNewline

# Database Password (base64 encoded)
Write-Host " → db_password.txt (32 bytes base64)" -ForegroundColor White
$dbPassword = New-RandomBase64 -Bytes 32
$dbPassword | Out-File -FilePath "$SecretsDir\db_password.txt" -Encoding ASCII -NoNewline

# API Key (for M2M authentication)
Write-Host " → api_key.txt (256-bit)" -ForegroundColor White
$apiKey = New-RandomHex -Bytes 32
$apiKey | Out-File -FilePath "$SecretsDir\api_key.txt" -Encoding ASCII -NoNewline

Write-Host ""

# ============================================================================
# SET RESTRICTIVE PERMISSIONS (ISO 42001 B.4.2)
# ============================================================================

Write-Host "🔒 Setting restrictive permissions..." -ForegroundColor Yellow

# Get current user
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Set permissions on secrets directory
$acl = Get-Acl $SecretsDir
$acl.SetAccessRuleProtection($true, $false)  # Disable inheritance

# Add full control for current user only
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $currentUser,
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl $SecretsDir $acl

Write-Host "✅ Permissions set (current user only)" -ForegroundColor Green

# Add .gitkeep to preserve directory structure
$gitkeep = Join-Path $SecretsDir ".gitkeep"
if (-not (Test-Path $gitkeep)) {
    New-Item -ItemType File -Path $gitkeep -Force | Out-Null
}

Write-Host "✅ Secrets generated successfully!" -ForegroundColor Green
Write-Host ""

# ============================================================================
# CALCULATE NEXT ROTATION DATE
# ============================================================================

$nextRotation = (Get-Date).AddDays(90).ToString("yyyy-MM-dd")

# ============================================================================
# POST-ROTATION INSTRUCTIONS
# ============================================================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "⚠️  REQUIRED ACTIONS:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Update environment variables:" -ForegroundColor White
Write-Host "   `$env:JWT_SECRET = Get-Content secrets\jwt_secret.txt" -ForegroundColor Gray
Write-Host "   `$env:HMAC_KEY = Get-Content secrets\hmac_key.txt" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart services:" -ForegroundColor White
Write-Host "   # Docker Compose" -ForegroundColor Gray
Write-Host "   docker-compose restart btv-api" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "   # Windows Service" -ForegroundColor Gray
Write-Host "   Restart-Service BuildToValue" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "   # Development" -ForegroundColor Gray
Write-Host "   # Press Ctrl+C and restart: uvicorn src.interface.api.gateway:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Revoke old JWT tokens:" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri 'http://localhost:8000/v1/auth/revoke-all' ``" -ForegroundColor Gray
Write-Host "       -Method Post ``" -ForegroundColor Gray
Write-Host "       -Headers @{Authorization = `"Bearer `$AdminToken`"}" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Update secrets in infrastructure:" -ForegroundColor White
Write-Host "   ✓ GitHub Secrets (CI/CD)" -ForegroundColor Gray
Write-Host "   ✓ Docker Secrets" -ForegroundColor Gray
Write-Host "   ✓ Kubernetes Secrets" -ForegroundColor Gray
Write-Host "   ✓ Azure Key Vault / AWS Secrets Manager" -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📅 Next rotation: $nextRotation" -ForegroundColor White
Write-Host "   (90 days from now - ISO 42001 requirement)" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Backup location: $BackupDir" -ForegroundColor White
Write-Host "   Keep this backup for 30 days (audit trail)" -ForegroundColor Gray
Write-Host ""
