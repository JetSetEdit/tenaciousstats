# Push env vars from .env.local back to Vercel (production, preview, development)
# Only pushes the variables we manage; skips Vercel-injected ones (VERCEL_*).
# Run from project root: .\vercel_env_push.ps1

$ErrorActionPreference = "Stop"
# Vercel CLI writes version to stderr; avoid script failure from that
$vercelErrorPref = $ErrorActionPreference
$envFile = Join-Path $PSScriptRoot ".env.local"

# Vars we want to push (skip VERCEL_*, etc.)
$varsToPush = @("PROPERTY_ID", "GOOGLE_APPLICATION_CREDENTIALS_B64", "GOOGLE_OAUTH_TOKEN_B64", "GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64")
$environments = @("production", "preview", "development")

if (-not (Test-Path $envFile)) {
    Write-Host ".env.local not found. Pull first: vercel env pull .env.local" -ForegroundColor Red
    exit 1
}

function Get-EnvVars {
    $content = Get-Content $envFile -Raw
    $result = @{}
    $content -split "`n" | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^\s*#' -or [string]::IsNullOrWhiteSpace($line)) { return }
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $val = $matches[2].Trim()
            if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Substring(1, $val.Length - 2).Replace('\"', '"') }
            if ($val.StartsWith("'") -and $val.EndsWith("'")) { $val = $val.Substring(1, $val.Length - 2) }
            $val = $val -replace "`r", ""
            $result[$key] = $val
        }
    }
    return $result
}

$vars = Get-EnvVars
$missing = $varsToPush | Where-Object { -not $vars.ContainsKey($_) }
if ($missing.Count -gt 0) {
    Write-Host "Note: .env.local does not contain: $($missing -join ', '). They will be skipped." -ForegroundColor Gray
}

foreach ($name in $varsToPush) {
    if (-not $vars.ContainsKey($name)) { continue }
    $value = $vars[$name]
    if ([string]::IsNullOrWhiteSpace($value)) { continue }

    Write-Host "Pushing $name..." -ForegroundColor Cyan
    $tmpFile = [IO.Path]::GetTempFileName()
    try {
        [IO.File]::WriteAllText($tmpFile, $value)
        foreach ($env in $environments) {
            cmd /c "vercel env rm $name $env -y 2>nul"
            $ErrorActionPreference = "SilentlyContinue"
            Get-Content $tmpFile -Raw | vercel env add $name $env 2>$null
            $ErrorActionPreference = $vercelErrorPref
            Write-Host "  $env" -ForegroundColor Green
        }
    } finally {
        Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Done. Verify: vercel env ls" -ForegroundColor Green
Write-Host "Redeploy production: vercel --prod" -ForegroundColor White
