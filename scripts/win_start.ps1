Param()

# Minimal Windows start script for MVP Docker stack
$env:DATA_ROOT = "C:\data\docs"

# Use Windows override files if present
$composeFile = "docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d --build"
Write-Host "Starting with Windows override if present..." -ForegroundColor Green
Invoke-Expression $composeFile

Write-Host "Starting MVP stack with Docker Compose..." -ForegroundColor Green
docker compose up -d --build

Write-Host "Waiting for services to become healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
  $resp = (Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing).Content
  Write-Host "Health check: $resp" -ForegroundColor Green
} catch {
  Write-Host "Health check failed. Check logs." -ForegroundColor Red
}
