# NPM Global Packages Migration Script
# This script migrates global npm packages to a new location on a different drive.
# RUN Set-ExecutionPolicy RemoteSigned before executing this script.

Write-Host "==== NPM GLOBAL PACKAGES MIGRATION SCRIPT ====" -ForegroundColor Cyan

# CONFIG
$newPrefix = "F:\npm-global"
$backupDir = "$env:USERPROFILE\npm-global-backup"
$packageListFile = "$backupDir\global-packages.txt"

# Step 1: Get current prefix
$currentPrefix = npm config get prefix
Write-Host "Current npm prefix: $currentPrefix"
Write-Host "New npm prefix: $newPrefix"

# Step 2: Create backup directory
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# Step 3: Backup existing global node_modules
if (Test-Path "$currentPrefix\node_modules") {
    Write-Host "Backing up existing global packages..."
    Copy-Item "$currentPrefix\node_modules" $backupDir -Recurse -Force
}

# Step 4: Export list of global packages (excluding npm itself)
Write-Host "Exporting global package list..."
npm list -g --depth=0 --json |
    ConvertFrom-Json |
    Select-Object -ExpandProperty dependencies |
    Get-Member -MemberType NoteProperty |
    Select-Object -ExpandProperty Name |
    Where-Object { $_ -ne "npm" } |
    Set-Content $packageListFile

Write-Host "Saved package list to: $packageListFile"

# Step 5: Create new prefix folder
if (!(Test-Path $newPrefix)) {
    New-Item -ItemType Directory -Path $newPrefix | Out-Null
}

# Step 6: Set npm prefix to new drive
Write-Host "Updating npm prefix..."
npm config set prefix $newPrefix

# Step 7: Update PATH (User level)
$binPath = "$newPrefix\bin"
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")

if ($userPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$binPath", "User")
    Write-Host "PATH updated."
}

# Step 8: Reinstall global packages safely
Write-Host "Reinstalling global packages..."
if (Test-Path $packageListFile) {
    Get-Content $packageListFile | ForEach-Object {
        Write-Host "Installing $_ ..."
        npm install -g $_
    }
}

# Step 9: Verify
Write-Host "`n==== VERIFICATION ===="
npm config get prefix
npm list -g --depth=0

Write-Host "`n✅ Migration completed successfully!"
Write-Host "⚠️ Restart your terminal or PC to apply PATH changes."
Write-Host "💾 Backup location: $backupDir"



# ROLLBACK INSTRUCTIONS:
# 1. Run this script again to reset npm prefix to the old location.
# 2. If you backed up the node_modules folder, copy it back to the old prefix location.

# $backupDir = "$env:USERPROFILE\npm-global-backup"
# $oldPrefix = "C:\Program Files\nodejs"

# npm config set prefix $oldPrefix

# if (Test-Path "$backupDir\node_modules") {
#     Copy-Item "$backupDir\node_modules" "$oldPrefix" -Recurse -Force
# }

# Write-Host "Rollback completed."
