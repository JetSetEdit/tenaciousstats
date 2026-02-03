# Set Environment Variables using Vercel CLI
# This script sets up the required environment variables for the Tenacious Stats dashboard

Write-Host "Setting up Vercel environment variables..." -ForegroundColor Cyan

# Read the base64 encoded credentials
$credentialsB64 = Get-Content "credentials_base64.txt" -Raw
$credentialsB64 = $credentialsB64.Trim()

# Set PROPERTY_ID
Write-Host "`nSetting PROPERTY_ID..." -ForegroundColor Yellow
vercel env add PROPERTY_ID production preview development <<< "368035934"

# Set GOOGLE_APPLICATION_CREDENTIALS_B64
Write-Host "`nSetting GOOGLE_APPLICATION_CREDENTIALS_B64..." -ForegroundColor Yellow
Write-Host "Note: You'll need to paste the base64 string when prompted" -ForegroundColor Gray
Write-Host "The value is in credentials_base64.txt" -ForegroundColor Gray

# For Windows PowerShell, we need to pipe the value
$credentialsB64 | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 production preview development

Write-Host "`n✅ Environment variables set!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Verify variables: vercel env ls" -ForegroundColor White
Write-Host "2. Deploy: vercel --prod" -ForegroundColor White










