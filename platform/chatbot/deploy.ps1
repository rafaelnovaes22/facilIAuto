# Deploy script for FacilIAuto WhatsApp Chatbot (Windows)
# Usage: .\deploy.ps1 [environment]
# Example: .\deploy.ps1 production

param(
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

# Configuration
$ComposeFile = "docker-compose.prod.yml"

Write-Host "========================================" -ForegroundColor Green
Write-Host "FacilIAuto WhatsApp Chatbot Deployment" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    Write-Host "Please copy .env.production to .env and configure it" -ForegroundColor Yellow
    Write-Host "Copy-Item .env.production .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ .env file found" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✓ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop first" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✓ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker Compose is not installed" -ForegroundColor Red
    Write-Host "Please install Docker Compose first" -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host "`nCreating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

# Pull latest images
Write-Host "`nPulling latest images..." -ForegroundColor Yellow
docker-compose -f $ComposeFile pull

# Build images
Write-Host "`nBuilding images..." -ForegroundColor Yellow
docker-compose -f $ComposeFile build

# Stop existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker-compose -f $ComposeFile down

# Start PostgreSQL first
Write-Host "`nStarting PostgreSQL..." -ForegroundColor Yellow
docker-compose -f $ComposeFile up -d postgres

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        docker-compose -f $ComposeFile exec -T postgres pg_isready -U faciliauto 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            break
        }
    } catch {}
    
    Write-Host "Waiting for PostgreSQL..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    $attempt++
}

if ($attempt -eq $maxAttempts) {
    Write-Host "❌ PostgreSQL failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green

# Run database migrations
Write-Host "`nRunning database migrations..." -ForegroundColor Yellow
docker-compose -f $ComposeFile run --rm chatbot-api alembic upgrade head

Write-Host "✓ Migrations completed" -ForegroundColor Green

# Start Redis
Write-Host "`nStarting Redis..." -ForegroundColor Yellow
docker-compose -f $ComposeFile up -d redis

# Wait for Redis to be ready
Write-Host "Waiting for Redis to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        docker-compose -f $ComposeFile exec -T redis redis-cli ping 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            break
        }
    } catch {}
    
    Write-Host "Waiting for Redis..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    $attempt++
}

if ($attempt -eq $maxAttempts) {
    Write-Host "❌ Redis failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Redis is ready" -ForegroundColor Green

# Start all services
Write-Host "`nStarting all services..." -ForegroundColor Yellow
docker-compose -f $ComposeFile up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "`nChecking service health..." -ForegroundColor Yellow

# Check API health
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ API health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ API health check failed" -ForegroundColor Red
}

# Check Celery worker
$workerStatus = docker-compose -f $ComposeFile ps celery-worker
if ($workerStatus -match "Up") {
    Write-Host "✓ Celery worker is running" -ForegroundColor Green
} else {
    Write-Host "❌ Celery worker is not running" -ForegroundColor Red
}

# Check Redis
try {
    docker-compose -f $ComposeFile exec -T redis redis-cli ping 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis is not running" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Redis is not running" -ForegroundColor Red
}

# Check PostgreSQL
try {
    docker-compose -f $ComposeFile exec -T postgres pg_isready -U faciliauto 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL is not running" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ PostgreSQL is not running" -ForegroundColor Red
}

# Show running containers
Write-Host "`nRunning containers:" -ForegroundColor Yellow
docker-compose -f $ComposeFile ps

# Show logs
Write-Host "`nRecent logs:" -ForegroundColor Yellow
docker-compose -f $ComposeFile logs --tail=20

# Final instructions
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure webhook in Meta Business Manager:"
Write-Host "   URL: https://your-domain.com/webhook/whatsapp"
Write-Host "   Verify Token: (from your .env file)"
Write-Host ""
Write-Host "2. Monitor services:"
Write-Host "   - API: http://localhost:8000/health"
Write-Host "   - Flower: http://localhost:5555"
Write-Host "   - Logs: docker-compose -f $ComposeFile logs -f"
Write-Host ""
Write-Host "3. Test by sending a WhatsApp message to your business number"
Write-Host ""
Write-Host "Happy chatting! 🚀`n" -ForegroundColor Green
