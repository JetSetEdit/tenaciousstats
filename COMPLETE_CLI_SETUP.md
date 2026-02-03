# Complete Vercel CLI Setup Guide

## Step 1: Link or Initialize Project

You have two options:

### Option A: Link to Existing Project
```powershell
vercel link
```
Follow prompts to select an existing project or create a new one.

### Option B: Deploy First (Creates Project)
```powershell
vercel
```
This will create/link the project automatically.

## Step 2: Set Environment Variables

After linking, set the environment variables:

### Set PROPERTY_ID (for all environments)
```powershell
echo "368035934" | vercel env add PROPERTY_ID production
echo "368035934" | vercel env add PROPERTY_ID preview  
echo "368035934" | vercel env add PROPERTY_ID development
```

### Set GOOGLE_APPLICATION_CREDENTIALS_B64 (for all environments)
```powershell
Get-Content credentials_base64.txt | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 production
Get-Content credentials_base64.txt | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 preview
Get-Content credentials_base64.txt | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 development
```

**Note:** The credentials file contains a long base64 string. Make sure the entire line is piped.

## Step 3: Verify Variables
```powershell
vercel env ls
```

## Step 4: Deploy
```powershell
vercel --prod
```

## Alternative: Set Variables via Dashboard

If CLI is giving issues, you can:
1. Deploy first: `vercel --prod`
2. Then go to Vercel Dashboard → Your Project → Settings → Environment Variables
3. Add the variables manually there

## Quick All-in-One Script

After linking, you can run:
```powershell
# Set PROPERTY_ID for all environments
foreach ($env in @("production", "preview", "development")) {
    echo "368035934" | vercel env add PROPERTY_ID $env
}

# Set credentials for all environments  
foreach ($env in @("production", "preview", "development")) {
    Get-Content credentials_base64.txt | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 $env
}
```










