# Cleanup All Services and Free Disk Space
# This script kills all running services and cleans up temporary files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup All Services & Free Space" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define service ports from start-all-services.ps1
$servicePorts = @(8000, 8001, 8002, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011)

Write-Host "[1/4] Stopping all service processes..." -ForegroundColor Yellow

# Kill processes on specific ports
foreach ($port in $servicePorts) {
    $connections = netstat -ano | findstr ":$port"
    if ($connections) {
        Write-Host "  Checking port $port..." -ForegroundColor Gray
        $connections | ForEach-Object {
            if ($_ -match '\s+(\d+)\s*$') {
                $pid = $matches[1]
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "    Killing process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Red
                    try {
                        Stop-Process -Id $pid -Force -ErrorAction Stop
                    } catch {
                        Write-Host "    Warning: Could not kill process $pid" -ForegroundColor Yellow
                    }
                }
            }
        }
    }
}

# Kill all Node.js processes (frontend dev servers)
Write-Host ""
Write-Host "[2/4] Stopping Node.js processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        Write-Host "  Killing Node.js process: PID $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "  No Node.js processes found" -ForegroundColor Green
}

# Kill all Python processes (backend services)
Write-Host ""
Write-Host "[3/4] Stopping Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Write-Host "  Killing Python process: PID $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "  No Python processes found" -ForegroundColor Green
}

# Kill uvicorn processes specifically
$uvicornProcesses = Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    foreach ($proc in $uvicornProcesses) {
        Write-Host "  Killing uvicorn process: PID $($proc.Id)" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "[4/4] Cleaning up temporary files and caches..." -ForegroundColor Yellow

# Clean Python cache files
Write-Host "  Cleaning Python __pycache__ directories..." -ForegroundColor Gray
Get-ChildItem -Path $PSScriptRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | 
    ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        if ($size -gt 0) {
            Write-Host "    Removing: $($_.FullName) ($([math]::Round($size, 2)) MB)" -ForegroundColor Gray
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

# Clean .pyc files
Write-Host "  Cleaning .pyc files..." -ForegroundColor Gray
Get-ChildItem -Path $PSScriptRoot -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | 
    ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }

# Clean node_modules (optional - uncomment if you want to remove them)
# Write-Host "  Cleaning node_modules..." -ForegroundColor Gray
# Get-ChildItem -Path $PSScriptRoot -Recurse -Directory -Filter "node_modules" -ErrorAction SilentlyContinue | 
#     ForEach-Object {
#         $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | 
#             Measure-Object -Property Length -Sum).Sum / 1MB
#         if ($size -gt 0) {
#             Write-Host "    Removing: $($_.FullName) ($([math]::Round($size, 2)) MB)" -ForegroundColor Gray
#             Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
#         }
#     }

# Clean .venv directories (Python virtual environments)
Write-Host "  Cleaning Python virtual environments..." -ForegroundColor Gray
Get-ChildItem -Path $PSScriptRoot -Recurse -Directory -Filter ".venv" -ErrorAction SilentlyContinue | 
    ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        if ($size -gt 0) {
            Write-Host "    Removing: $($_.FullName) ($([math]::Round($size, 2)) MB)" -ForegroundColor Gray
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

# Clean frontend build artifacts
Write-Host "  Cleaning frontend build artifacts..." -ForegroundColor Gray
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (Test-Path $frontendPath) {
    $distDirs = @("dist", ".vite", "node_modules/.vite")
    foreach ($dir in $distDirs) {
        $fullPath = Join-Path $frontendPath $dir
        if (Test-Path $fullPath) {
            $size = (Get-ChildItem $fullPath -Recurse -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB
            if ($size -gt 0) {
                Write-Host "    Removing: $fullPath ($([math]::Round($size, 2)) MB)" -ForegroundColor Gray
                Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Clean SQLite databases (optional - be careful!)
# Write-Host "  Cleaning SQLite databases..." -ForegroundColor Gray
# Get-ChildItem -Path $PSScriptRoot -Recurse -Filter "*.db" -ErrorAction SilentlyContinue | 
#     ForEach-Object {
#         Write-Host "    Found: $($_.FullName)" -ForegroundColor Gray
#         # Uncomment next line to delete databases (CAREFUL!)
#         # Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
#     }

# Clean temporary files
Write-Host "  Cleaning temporary files..." -ForegroundColor Gray
$tempPatterns = @("*.tmp", "*.log", "*.cache")
foreach ($pattern in $tempPatterns) {
    Get-ChildItem -Path $PSScriptRoot -Recurse -Filter $pattern -ErrorAction SilentlyContinue | 
        ForEach-Object {
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        }
}

# Clean Windows temp files (system-wide)
Write-Host ""
Write-Host "  Cleaning Windows temporary files..." -ForegroundColor Gray
$tempPaths = @(
    "$env:TEMP\*",
    "$env:LOCALAPPDATA\Temp\*"
)
foreach ($tempPath in $tempPaths) {
    if (Test-Path $tempPath) {
        $items = Get-ChildItem $tempPath -ErrorAction SilentlyContinue | 
            Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
        $count = ($items | Measure-Object).Count
        if ($count -gt 0) {
            Write-Host "    Removing $count old files from $tempPath" -ForegroundColor Gray
            $items | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
        }
    }
}

# Show disk space
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Show remaining processes on ports
Write-Host "Checking remaining processes on service ports..." -ForegroundColor Yellow
foreach ($port in $servicePorts) {
    $connections = netstat -ano | findstr ":$port"
    if ($connections) {
        Write-Host "  WARNING: Port $port is still in use!" -ForegroundColor Yellow
    } else {
        Write-Host "  OK: Port $port is free" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Disk Space Information:" -ForegroundColor Cyan
$drive = (Get-Location).Drive
$driveInfo = Get-PSDrive $drive.Name
$freeSpaceGB = [math]::Round($driveInfo.Free / 1GB, 2)
$usedSpaceGB = [math]::Round(($driveInfo.Used / 1GB), 2)
Write-Host ("  Free Space: " + $freeSpaceGB + " GB") -ForegroundColor Green
Write-Host ("  Used Space: " + $usedSpaceGB + " GB") -ForegroundColor Yellow
Write-Host ""


