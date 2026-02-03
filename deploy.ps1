# Deploy script that increments version and deploys
Write-Host "Incrementing version..." -ForegroundColor Cyan
& .\increment-version.ps1

Write-Host "`nDeploying to Vercel..." -ForegroundColor Cyan
vercel --prod

Write-Host "`nDeployment complete!" -ForegroundColor Green








