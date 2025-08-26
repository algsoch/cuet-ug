# CUET UG Admission Analyzer - Docker Deployment Script for Windows
# Run this script in PowerShell to build and deploy with Docker

param(
    [Parameter(Mandatory=$false)]
    [string]$AppName = "cuet-analyzer",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8000
)

Write-Host "🐳 CUET UG Admission Analyzer - Docker Deployment" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop:" -ForegroundColor Red
    Write-Host "   https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if Dockerfile exists
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Dockerfile not found in current directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dockerfile found" -ForegroundColor Green

Write-Host "" -ForegroundColor White
Write-Host "🏗️ Building Docker image: $AppName" -ForegroundColor Blue
Write-Host "   This may take a few minutes..." -ForegroundColor Yellow

# Build Docker image
try {
    docker build -t $AppName .
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "🚀 Starting application container..." -ForegroundColor Blue

# Stop any existing container with the same name
docker stop $AppName 2>$null
docker rm $AppName 2>$null

# Get current directory for volume mounting
$currentDir = Get-Location

# Run the container
try {
    docker run -d `
        --name $AppName `
        -p "${Port}:8000" `
        -v "${currentDir}/data:/app/data" `
        -v "${currentDir}/outputs:/app/outputs" `
        -v "${currentDir}/uploads:/app/uploads" `
        $AppName
    
    Write-Host "✅ Container started successfully" -ForegroundColor Green
    
    Write-Host "" -ForegroundColor White
    Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    Write-Host "🌐 Application URL: http://localhost:$Port" -ForegroundColor Blue
    Write-Host "📊 Health Check: http://localhost:$Port/api/health" -ForegroundColor Blue
    Write-Host "📚 API Documentation: http://localhost:$Port/docs" -ForegroundColor Blue
    Write-Host "" -ForegroundColor White
    Write-Host "🔧 Docker Commands:" -ForegroundColor Yellow
    Write-Host "   View logs: docker logs $AppName" -ForegroundColor White
    Write-Host "   Stop app: docker stop $AppName" -ForegroundColor White
    Write-Host "   Start app: docker start $AppName" -ForegroundColor White
    Write-Host "   Remove app: docker rm -f $AppName" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    
    # Wait for application to start
    Write-Host "⏳ Waiting for application to start..." -ForegroundColor Blue
    Start-Sleep -Seconds 10
    
    # Check if application is responding
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/api/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Application is responding" -ForegroundColor Green
            
            # Ask if user wants to open browser
            $openBrowser = Read-Host "Would you like to open the application in your browser? (y/n)"
            if ($openBrowser.ToLower() -eq "y" -or $openBrowser.ToLower() -eq "yes") {
                Start-Process "http://localhost:$Port"
            }
        }
    } catch {
        Write-Host "⚠️ Application might still be starting. Please wait a moment and try http://localhost:$Port" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "✅ Docker deployment completed successfully!" -ForegroundColor Green
Write-Host "🐳 Your CUET UG Admission Analyzer is now running in a container!" -ForegroundColor Blue

# Display container status
Write-Host "" -ForegroundColor White
Write-Host "📊 Container Status:" -ForegroundColor Yellow
docker ps -f name=$AppName --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
