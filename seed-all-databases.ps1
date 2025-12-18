# PowerShell script to seed all microservice databases
# This script runs all individual seed scripts in sequence

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MSOP Project - Database Seeding Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$services = @(
    "booking-reservation-service",
    "inventory-resource-service",
    "payment-billing-service",
    "guest-interaction-service",
    "dynamic-pricing-service",
    "housekeeping-maintenance-service",
    "feedback-sentiment-service",
    "marketing-loyalty-service",
    "favorites-collections-service",
    "bi-analytics-service"
)

$results = @{}
$scriptPath = $PSScriptRoot

foreach ($service in $services) {
    $serviceDir = Join-Path $scriptPath $service
    $seedScript = Join-Path $serviceDir "seed_data.py"
    
    if (-not (Test-Path $seedScript)) {
        Write-Host "`n[WARNING] Seed script not found for $service : $seedScript" -ForegroundColor Yellow
        $results[$service] = $false
        continue
    }
    
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "Running seed script for: $service" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    
    try {
        Push-Location $serviceDir
        
        # Prioritize root .venv (unified environment) over service-specific .venv
        $rootVenvPython = Join-Path $scriptPath ".venv\Scripts\python.exe"
        $serviceVenvPython = Join-Path $serviceDir ".venv\Scripts\python.exe"
        
        # Always prefer root .venv if it exists (unified dependencies)
        if (Test-Path $rootVenvPython) {
            Write-Host "[INFO] Using root unified virtual environment" -ForegroundColor Gray
            $pythonCmd = $rootVenvPython
        } elseif (Test-Path $serviceVenvPython) {
            Write-Host "[INFO] Using service virtual environment: $serviceDir\.venv" -ForegroundColor Gray
            Write-Host "[WARNING] Consider using root .venv for unified dependencies" -ForegroundColor Yellow
            $pythonCmd = $serviceVenvPython
        } else {
            # Use system python
            Write-Host "[INFO] Using system Python (no .venv found)" -ForegroundColor Gray
            Write-Host "[WARNING] Dependencies may not be installed. Run .\install-all-dependencies.ps1 first" -ForegroundColor Yellow
            $pythonCmd = "python"
        }
        
        & $pythonCmd seed_data.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Successfully seeded $service" -ForegroundColor Green
            $results[$service] = $true
        } else {
            Write-Host "[ERROR] Error seeding $service (exit code: $LASTEXITCODE)" -ForegroundColor Red
            $results[$service] = $false
        }
        Pop-Location
    } catch {
        Write-Host "[ERROR] Unexpected error seeding $service : $_" -ForegroundColor Red
        $results[$service] = $false
        if ((Get-Location).Path -ne $scriptPath) {
            Pop-Location
        }
    }
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SEEDING SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$successful = ($results.Values | Where-Object { $_ -eq $true }).Count
$failed = ($results.Values | Where-Object { $_ -eq $false }).Count

foreach ($service in $results.Keys) {
    $status = if ($results[$service]) { "[OK] SUCCESS" } else { "[X] FAILED" }
    $color = if ($results[$service]) { "Green" } else { "Red" }
    Write-Host "$status - $service" -ForegroundColor $color
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Total: $($results.Count) services" -ForegroundColor Cyan
Write-Host "Successful: $successful" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "============================================================" -ForegroundColor Cyan

if ($failed -gt 0) {
    Write-Host "`n[WARNING] Some services failed to seed. Please check the errors above." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n[SUCCESS] All databases seeded successfully!" -ForegroundColor Green
    exit 0
}

