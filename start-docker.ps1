# Start Docker containers for Tenacious Stats Dashboard

Write-Host "Checking Docker Desktop..." -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker ps 2>&1 | Select-String -Pattern "CONTAINER|error" -Quiet

if ($dockerRunning -or (docker ps 2>&1 | Select-String -Pattern "CONTAINER")) {
    Write-Host "Docker is running!" -ForegroundColor Green
} else {
    Write-Host "Docker Desktop is not running. Please:" -ForegroundColor Yellow
    Write-Host "1. Start Docker Desktop from the Start Menu" -ForegroundColor Yellow
    Write-Host "2. Wait for the whale icon in system tray to be steady" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Attempting to start Docker Desktop..." -ForegroundColor Cyan
    
    # Try common Docker Desktop paths
    $dockerPaths = @(
        "C:\Program Files\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
    )
    
    $started = $false
    foreach ($path in $dockerPaths) {
        if (Test-Path $path) {
            Start-Process $path
            Write-Host "Started Docker Desktop from: $path" -ForegroundColor Green
            $started = $true
            break
        }
    }
    
    if (-not $started) {
        Write-Host "Could not find Docker Desktop. Please start it manually." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Waiting for Docker Desktop to start (this may take 30-60 seconds)..." -ForegroundColor Yellow
    $timeout = 60
    $elapsed = 0
    while ($elapsed -lt $timeout) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        $dockerCheck = docker ps 2>&1
        if ($dockerCheck -notmatch "error|cannot find") {
            Write-Host "Docker is ready!" -ForegroundColor Green
            break
        }
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
    Write-Host ""
}

# Check for credentials.json
if (-not (Test-Path "credentials.json")) {
    Write-Host "WARNING: credentials.json not found!" -ForegroundColor Yellow
    Write-Host "The backend will not be able to connect to Google Analytics." -ForegroundColor Yellow
    Write-Host "Please ensure credentials.json exists in the project root." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Start containers
Write-Host "Starting Docker containers..." -ForegroundColor Cyan
Write-Host "Frontend will be at: http://localhost:8080" -ForegroundColor Green
Write-Host "Backend will be at: http://localhost:8000" -ForegroundColor Green
Write-Host ""

docker-compose -f docker-compose.dev.yml up








