# PowerShell script to increment version
$versionFile = "public\version.txt"

if (Test-Path $versionFile) {
    $version = (Get-Content $versionFile).Trim()
    $parts = $version.Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    $patch++
    $newVersion = "$major.$minor.$patch"
} else {
    $newVersion = "1.0.1"
}

Set-Content -Path $versionFile -Value $newVersion
Write-Host "Version incremented to: $newVersion"








