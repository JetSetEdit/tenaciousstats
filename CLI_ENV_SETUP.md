# Quick Commands to Set Vercel Environment Variables

## Option 1: Interactive (Recommended)
Run these commands one at a time and follow the prompts:

```powershell
# 1. Set PROPERTY_ID
echo "368035934" | vercel env add PROPERTY_ID production preview development

# 2. Set GOOGLE_APPLICATION_CREDENTIALS_B64
Get-Content credentials_base64.txt | vercel env add GOOGLE_APPLICATION_CREDENTIALS_B64 production preview development
```

## Option 2: Using vercel.json (if supported)
You can also set them in vercel.json, but for sensitive data, use the CLI method above.

## Verify Variables
After setting, verify with:
```powershell
vercel env ls
```

## Deploy After Setting Variables
```powershell
vercel --prod
```

## Notes
- When prompted for "value", paste the content
- Select all environments (production, preview, development) when asked
- The base64 string is long - make sure to copy the entire line from credentials_base64.txt










