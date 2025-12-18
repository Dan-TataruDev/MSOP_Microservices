# PowerShell script to initialize all PostgreSQL databases and users
# This can be run manually if the init-postgres.sh script didn't run on container creation

$containerName = "hospitality_postgres"
$postgresUser = "postgres"

Write-Host "Initializing PostgreSQL databases and users..." -ForegroundColor Green

# Function to execute SQL command
function Execute-SQL {
    param([string]$sql)
    docker exec $containerName psql -U $postgresUser -c $sql 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
        return $true
    } else {
        Write-Host " [SKIPPED - may already exist]" -ForegroundColor Yellow
        return $false
    }
}

# Function to create database and user
function Create-DatabaseAndUser {
    param(
        [string]$dbName,
        [string]$userName,
        [string]$password
    )
    
    Write-Host "Creating database: $dbName" -NoNewline
    Execute-SQL "CREATE DATABASE $dbName;" | Out-Null
    
    Write-Host "Creating user: $userName" -NoNewline
    Execute-SQL "CREATE USER $userName WITH PASSWORD '$password';" | Out-Null
    
    Write-Host "Granting privileges on $dbName to $userName" -NoNewline
    Execute-SQL "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $userName;" | Out-Null
    
    Write-Host "Granting schema privileges on $dbName to $userName" -NoNewline
    docker exec $containerName psql -U $postgresUser -d $dbName -c "GRANT ALL ON SCHEMA public TO $userName; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $userName; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $userName;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [WARNING]" -ForegroundColor Yellow
    }
}

# List of all services
$services = @(
    @{db="auth_db"; user="auth_user"; pass="auth_password"},
    @{db="guest_interaction_db"; user="guest_user"; pass="guest_password"},
    @{db="booking_reservation_db"; user="booking_user"; pass="booking_password"},
    @{db="dynamic_pricing_db"; user="pricing_user"; pass="pricing_password"},
    @{db="payment_billing_db"; user="payment_user"; pass="payment_password"},
    @{db="inventory_db"; user="inventory_user"; pass="inventory_password"},
    @{db="feedback_sentiment_db"; user="feedback_user"; pass="feedback_password"},
    @{db="marketing_loyalty_db"; user="marketing_user"; pass="marketing_password"},
    @{db="bi_analytics_db"; user="analytics_user"; pass="analytics_password"},
    @{db="housekeeping_db"; user="housekeeping_user"; pass="housekeeping_password"},
    @{db="favorites_collections_db"; user="favorites_user"; pass="favorites_password"}
)

foreach ($service in $services) {
    Write-Host ""
    Write-Host "Processing: $($service.db)" -ForegroundColor Cyan
    Create-DatabaseAndUser -dbName $service.db -userName $service.user -password $service.pass
}

Write-Host ""
Write-Host "Database initialization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To verify, run: docker exec $containerName psql -U $postgresUser -c '\l'" -ForegroundColor Yellow
