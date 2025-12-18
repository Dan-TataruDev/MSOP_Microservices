# Check Service Status
# This script checks if services are running and accessible

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Checking Service Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Guest Interaction"; Port=8000; URL="http://localhost:8000/docs"},
    @{Name="Favorites Collections"; Port=8007; URL="http://localhost:8007/docs"}
)

foreach ($svc in $services) {
    Write-Host "Checking $($svc.Name) on port $($svc.Port)..." -ForegroundColor Yellow
    
    # Check if port is listening
    $portCheck = netstat -ano | findstr ":$($svc.Port)"
    
    if ($portCheck) {
        Write-Host "  [✓] Port $($svc.Port) is listening" -ForegroundColor Green
        
        # Try to access the health endpoint
        try {
            $healthUrl = $svc.URL -replace "/docs", "/health"
            $response = Invoke-WebRequest -Uri $healthUrl -Method Get -TimeoutSec 2 -ErrorAction Stop
            Write-Host "  [✓] Health check passed" -ForegroundColor Green
            Write-Host "  [✓] Swagger docs: $($svc.URL)" -ForegroundColor Green
        } catch {
            Write-Host "  [!] Service is running but health check failed" -ForegroundColor Yellow
            Write-Host "      Try accessing: $($svc.URL)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [✗] Port $($svc.Port) is NOT listening" -ForegroundColor Red
        Write-Host "      Service is not running. Start it with:" -ForegroundColor Yellow
        Write-Host "      cd $($svc.Name.ToLower().Replace(' ', '-') + '-service')" -ForegroundColor Gray
        Write-Host "      python -m uvicorn app.main:app --reload --port $($svc.Port)" -ForegroundColor Gray
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Troubleshooting Tips" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure services are started:" -ForegroundColor Yellow
Write-Host "   .\start-all-services.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Check if ports are already in use:" -ForegroundColor Yellow
Write-Host "   netstat -ano | findstr \":8000\"" -ForegroundColor Gray
Write-Host "   netstat -ano | findstr \":8007\"" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Check service logs for errors" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Verify database connections are working" -ForegroundColor Yellow
Write-Host ""

