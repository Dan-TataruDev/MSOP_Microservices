# PowerShell script to create all PostgreSQL databases and users
# Run this if the init script didn't run (e.g., container was created before init script existed)

Write-Host "Creating all PostgreSQL databases and users..." -ForegroundColor Green

$databases = @(
    @{Name="guest_interaction_db"; User="guest_user"; Password="guest_password"},
    @{Name="booking_reservation_db"; User="booking_user"; Password="booking_password"},
    @{Name="dynamic_pricing_db"; User="pricing_user"; Password="pricing_password"},
    @{Name="payment_billing_db"; User="payment_user"; Password="payment_password"},
    @{Name="inventory_db"; User="inventory_user"; Password="inventory_password"},
    @{Name="feedback_sentiment_db"; User="feedback_user"; Password="feedback_password"},
    @{Name="marketing_loyalty_db"; User="marketing_user"; Password="marketing_password"},
    @{Name="bi_analytics_db"; User="analytics_user"; Password="analytics_password"},
    @{Name="housekeeping_db"; User="housekeeping_user"; Password="housekeeping_password"},
    @{Name="favorites_collections_db"; User="favorites_user"; Password="favorites_password"}
)

foreach ($db in $databases) {
    Write-Host "Creating database: $($db.Name) with user: $($db.User)..." -ForegroundColor Yellow
    
    # Create database (ignore error if exists)
    docker exec hospitality_postgres psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='$($db.Name)'" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        docker exec hospitality_postgres psql -U postgres -c "CREATE DATABASE $($db.Name);"
    } else {
        Write-Host "  Database $($db.Name) already exists, skipping..." -ForegroundColor Gray
    }
    
    # Create user (ignore error if exists)
    docker exec hospitality_postgres psql -U postgres -c "SELECT 1 FROM pg_user WHERE usename='$($db.User)'" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        docker exec hospitality_postgres psql -U postgres -c "CREATE USER $($db.User) WITH PASSWORD '$($db.Password)';"
    } else {
        Write-Host "  User $($db.User) already exists, skipping..." -ForegroundColor Gray
    }
    
    # Grant privileges
    docker exec hospitality_postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $($db.Name) TO $($db.User);"
    
    # Grant schema privileges
    docker exec hospitality_postgres psql -U postgres -d $($db.Name) -c "GRANT ALL ON SCHEMA public TO $($db.User); ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $($db.User); ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $($db.User);"
    
    Write-Host "  ✓ $($db.Name) setup complete" -ForegroundColor Green
}

Write-Host "`nAll databases created successfully!" -ForegroundColor Green

