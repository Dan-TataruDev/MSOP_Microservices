# Quick script to kill all processes on service ports
# Use this for a quick cleanup without file deletion

Write-Host "Killing all processes on service ports..." -ForegroundColor Yellow
Write-Host ""

$servicePorts = @(8000, 8001, 8002, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 3000, 5173)

$killedCount = 0

foreach ($port in $servicePorts) {
    $connections = netstat -ano | findstr ":$port"
    if ($connections) {
        Write-Host "Port $port:" -ForegroundColor Cyan
        $connections | ForEach-Object {
            if ($_ -match '\s+(\d+)\s*$') {
                $pid = $matches[1]
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "  → Killing: $($process.ProcessName) (PID: $pid)" -ForegroundColor Red
                    try {
                        Stop-Process -Id $pid -Force -ErrorAction Stop
                        $killedCount++
                    } catch {
                        Write-Host "    ⚠️  Failed to kill PID $pid" -ForegroundColor Yellow
                    }
                }
            }
        }
    }
}

# Also kill common dev server processes
Write-Host ""
Write-Host "Killing Node.js and Python processes..." -ForegroundColor Yellow

$processesToKill = @("node", "python", "uvicorn", "pnpm", "npm")
foreach ($procName in $processesToKill) {
    $procs = Get-Process -Name $procName -ErrorAction SilentlyContinue
    if ($procs) {
        foreach ($proc in $procs) {
            Write-Host "  → Killing: $($proc.ProcessName) (PID: $proc.Id)" -ForegroundColor Red
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            $killedCount++
        }
    }
}

Write-Host ""
Write-Host "✓ Killed $killedCount processes" -ForegroundColor Green
Write-Host ""

# Verify ports are free
Write-Host "Verifying ports are free..." -ForegroundColor Yellow
$stillInUse = @()
foreach ($port in $servicePorts) {
    $connections = netstat -ano | findstr ":$port"
    if ($connections) {
        $stillInUse += $port
    }
}

if ($stillInUse.Count -eq 0) {
    Write-Host "✓ All ports are now free!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ports still in use: $($stillInUse -join ', ')" -ForegroundColor Yellow
    Write-Host "   You may need to manually kill these processes" -ForegroundColor Yellow
}


