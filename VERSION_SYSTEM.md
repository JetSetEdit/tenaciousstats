# Version System

The dashboard displays a build version in the footer that automatically increments with each deployment.

## Current Version
The current version is stored in `public/version.txt` and follows semantic versioning (major.minor.patch).

## How to Deploy with Version Increment

### Option 1: Use the Deploy Script (Recommended)
```powershell
.\deploy.ps1
```
This script automatically increments the version and deploys to production.

### Option 2: Manual Increment
```powershell
# Increment version
node increment-version.js
# Or use PowerShell:
.\increment-version.ps1

# Then deploy
vercel --prod
```

### Option 3: Use npm (if you prefer)
```bash
npm run prebuild  # Increments version
vercel --prod      # Deploys
```

## Version Display
The version appears in the footer as "Build vX.X.X" in a subtle, non-obtrusive style. It's hidden when printing reports.

## Version Format
- **Major**: Breaking changes (increment manually)
- **Minor**: New features (increment manually)  
- **Patch**: Bug fixes, deployments (auto-increments)

The increment script automatically increments the patch version. For major/minor changes, manually edit `public/version.txt`.








