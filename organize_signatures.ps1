# PowerShell script to organize items into groups of 10
# Source folder
$sourceFolder = "C:\Users\CustomerService\Documents\Signatures"

# Check if source folder exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "Error: Source folder does not exist: $sourceFolder" -ForegroundColor Red
    exit 1
}

# Get all items in the source folder (files and folders)
$items = Get-ChildItem -Path $sourceFolder -File

# Check if there are any items
if ($items.Count -eq 0) {
    Write-Host "No items found in $sourceFolder" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($items.Count) items to organize" -ForegroundColor Green

# Group items into batches of 10
$groupSize = 10
$groupNumber = 1
$currentGroup = @()

foreach ($item in $items) {
    $currentGroup += $item
    
    # When we have 10 items or this is the last item
    if ($currentGroup.Count -eq $groupSize -or $item -eq $items[-1]) {
        # Create group folder name
        $groupFolderName = "Group$groupNumber"
        $groupFolderPath = Join-Path $sourceFolder $groupFolderName
        
        # Create the group folder if it doesn't exist
        if (-not (Test-Path $groupFolderPath)) {
            New-Item -ItemType Directory -Path $groupFolderPath | Out-Null
            Write-Host "Created folder: $groupFolderName" -ForegroundColor Cyan
        }
        
        # Move items to the group folder
        foreach ($groupItem in $currentGroup) {
            $destinationPath = Join-Path $groupFolderPath $groupItem.Name
            Move-Item -Path $groupItem.FullName -Destination $destinationPath -Force
            Write-Host "  Moved: $($groupItem.Name)" -ForegroundColor Gray
        }
        
        Write-Host "Group $groupNumber complete: $($currentGroup.Count) items" -ForegroundColor Green
        Write-Host ""
        
        # Reset for next group
        $currentGroup = @()
        $groupNumber++
    }
}

Write-Host "Organization complete! Created $($groupNumber - 1) group folders." -ForegroundColor Green









