# PowerShell script to install dependencies for all microservices
# Uses the unified requirements file that contains all dependencies

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Installing Dependencies for All Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$scriptPath = $PSScriptRoot
$unifiedRequirements = Join-Path $scriptPath "requirements-unified.txt"
$rootVenvPython = Join-Path $scriptPath ".venv\Scripts\python.exe"

# Check if unified requirements exists, if not, generate it
if (-not (Test-Path $unifiedRequirements)) {
    Write-Host "[INFO] Unified requirements file not found. Generating it..." -ForegroundColor Yellow
    python (Join-Path $scriptPath "merge-requirements.py")
    
    if (-not (Test-Path $unifiedRequirements)) {
        Write-Host "[ERROR] Failed to generate unified requirements file" -ForegroundColor Red
        exit 1
    }
}

# Check if virtual environment exists
if (-not (Test-Path $rootVenvPython)) {
    Write-Host "[INFO] Virtual environment not found. Creating it..." -ForegroundColor Yellow
    python -m venv .venv
    
    if (-not (Test-Path $rootVenvPython)) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Write-Host "[INFO] Using root virtual environment: $rootVenvPython" -ForegroundColor Gray
Write-Host "[INFO] Installing from unified requirements: $unifiedRequirements" -ForegroundColor Gray
Write-Host ""

# Upgrade pip first
Write-Host "[INFO] Upgrading pip..." -ForegroundColor Cyan
& $rootVenvPython -m pip install --upgrade pip -q
Write-Host ""

# Install all dependencies from unified file
Write-Host "[INFO] Installing all dependencies (this may take a few minutes)..." -ForegroundColor Cyan
& $rootVenvPython -m pip install -r $unifiedRequirements

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "[SUCCESS] All dependencies installed successfully!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run the seed scripts:" -ForegroundColor Gray
    Write-Host "  .\seed-all-databases.ps1" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to install some dependencies" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    exit 1
}

