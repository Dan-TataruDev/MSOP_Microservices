# Start All Backend Services
# Run this script from the MSOP_Project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting All Backend Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot

# Define services with their ports
$services = @(
    @{Name="Auth Service"; Port=8001; Path="auth-service"},
    @{Name="Guest Interaction"; Port=8000; Path="guest-interaction-service"},
    @{Name="Booking Reservation"; Port=8002; Path="booking-reservation-service"},
    @{Name="Dynamic Pricing"; Port=8004; Path="dynamic-pricing-service"},
    @{Name="Payment Billing"; Port=8005; Path="payment-billing-service"},
    @{Name="Inventory Resource"; Port=8006; Path="inventory-resource-service"},
    @{Name="Favorites Collections"; Port=8007; Path="favorites-collections-service"},
    @{Name="Feedback Sentiment"; Port=8008; Path="feedback-sentiment-service"},
    @{Name="Marketing Loyalty"; Port=8009; Path="marketing-loyalty-service"},
    @{Name="BI Analytics"; Port=8010; Path="bi-analytics-service"},
    @{Name="Housekeeping Maintenance"; Port=8011; Path="housekeeping-maintenance-service"}
)

foreach ($svc in $services) {
    $servicePath = Join-Path $rootDir $svc.Path
    
    if (Test-Path $servicePath) {
        Write-Host "[+] Starting $($svc.Name) on port $($svc.Port)..." -ForegroundColor Green
        
        $cmd = "cd '$servicePath'; Write-Host 'Starting $($svc.Name)...' -ForegroundColor Yellow; python -m uvicorn app.main:app --reload --port $($svc.Port)"
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
        
        Start-Sleep -Milliseconds 500
    } else {
        Write-Host "[-] Service path not found: $servicePath" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services starting!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  Auth Service:           http://localhost:8001/docs"
Write-Host "  Guest Interaction:      http://localhost:8000/docs"
Write-Host "  Booking Reservation:    http://localhost:8002/docs"
Write-Host "  Dynamic Pricing:        http://localhost:8004/docs"
Write-Host "  Payment Billing:        http://localhost:8005/docs"
Write-Host "  Inventory Resource:     http://localhost:8006/docs"
Write-Host "  Favorites Collections:  http://localhost:8007/docs"
Write-Host "  Feedback Sentiment:     http://localhost:8008/docs"
Write-Host "  Marketing Loyalty:      http://localhost:8009/docs"
Write-Host "  BI Analytics:           http://localhost:8010/docs"
Write-Host "  Housekeeping:           http://localhost:8011/docs"
Write-Host ""
Write-Host "To start the frontend:" -ForegroundColor Yellow
Write-Host "  cd frontend"
Write-Host "  pnpm install"
Write-Host "  pnpm dev"
Write-Host ""
Write-Host "Frontend will be at: http://localhost:5173" -ForegroundColor Green
