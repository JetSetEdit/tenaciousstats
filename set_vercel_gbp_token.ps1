# Upload GBP OAuth token to Vercel (GOOGLE_OAUTH_TOKEN_B64)
# Prereqs: token.pickle in project root (from: python gbp_oauth_login.py)
# Run from project root: .\set_vercel_gbp_token.ps1

$ErrorActionPreference = "Stop"
$tokenPath = Join-Path $PSScriptRoot "token.pickle"

if (-not (Test-Path $tokenPath)) {
    Write-Host "token.pickle not found. Create it first:" -ForegroundColor Red
    Write-Host "  python gbp_oauth_login.py" -ForegroundColor White
    Write-Host "Sign in with the Google account that owns your Business Profile, then run this script again." -ForegroundColor Gray
    exit 1
}

Write-Host "Reading token.pickle and encoding to base64..." -ForegroundColor Cyan
$bytes = [IO.File]::ReadAllBytes($tokenPath)
$b64 = [Convert]::ToBase64String($bytes)

Write-Host "Adding GOOGLE_OAUTH_TOKEN_B64 to Vercel (production, preview, development)..." -ForegroundColor Yellow
# Vercel CLI: add env var; pipe value to avoid prompt
$b64 | vercel env add GOOGLE_OAUTH_TOKEN_B64 production
$b64 | vercel env add GOOGLE_OAUTH_TOKEN_B64 preview
$b64 | vercel env add GOOGLE_OAUTH_TOKEN_B64 development

Write-Host "Done. Verify: vercel env ls" -ForegroundColor Green
Write-Host "Redeploy for production: vercel --prod" -ForegroundColor White
