Param()

# Simple local validation script for Windows MVP stack
Write-Host "Validating MVP stack on Windows..." -ForegroundColor Green

$healthUri = "http://localhost:8000/health"
try {
  $resp = Invoke-WebRequest -Uri $healthUri -UseBasicParsing
  Write-Host "Health: " $resp.Content
} catch {
  Write-Host "Health check failed: $_" -ForegroundColor Red
  exit 1
}

$chatUri = "http://localhost:8000/api/chat"
$payload = '{"user_id":"u1","room_id":"general","message":"Привет"}'
try {
  $r = Invoke-WebRequest -Uri $chatUri -Method POST -ContentType 'application/json' -Body $payload
  Write-Host "Chat response: " $r.Content
} catch {
  Write-Host "Chat request failed: $_" -ForegroundColor Red
  exit 1
}
