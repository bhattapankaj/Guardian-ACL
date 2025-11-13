# ACL Guardian - Deployment Helper Script for Windows/PowerShell

Write-Host ""
Write-Host "ACL GUARDIAN - DEPLOYMENT HELPER" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Git
Write-Host "Checking Git Repository..." -ForegroundColor Yellow
if (Test-Path .git) {
    Write-Host "  Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "  Git not initialized - Run: git init" -ForegroundColor Red
}

# Check required files
Write-Host ""
Write-Host "Checking Backend Files..." -ForegroundColor Yellow
if (Test-Path "backend\requirements.txt") { Write-Host "  requirements.txt" -ForegroundColor Green }
if (Test-Path "backend\main.py") { Write-Host "  main.py" -ForegroundColor Green }
if (Test-Path "backend\render.yaml") { Write-Host "  render.yaml" -ForegroundColor Green }

Write-Host ""
Write-Host "Checking Frontend Files..." -ForegroundColor Yellow
if (Test-Path "package.json") { Write-Host "  package.json" -ForegroundColor Green }
if (Test-Path "vercel.json") { Write-Host "  vercel.json" -ForegroundColor Green }

Write-Host ""
Write-Host "Environment Variables Needed:" -ForegroundColor Yellow
Write-Host "  RENDER: FRONTEND_URL, FITBIT_CLIENT_ID, SUPABASE_URL, etc." -ForegroundColor Gray
Write-Host "  VERCEL: NEXT_PUBLIC_API_URL" -ForegroundColor Gray

Write-Host ""
Write-Host "See DEPLOYMENT_GUIDE.md for complete instructions" -ForegroundColor Green
Write-Host ""
