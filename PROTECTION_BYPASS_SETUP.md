# Protection Bypass Setup - Quick Guide

## ✅ Yes, use Protection Bypass for Automation!

This is the **best approach** because:
- ✅ Keeps your deployment secure (protected from public access)
- ✅ Allows automation/scripts to access it
- ✅ The secret is available as an environment variable

## Setup Steps

### 1. Enable in Vercel Dashboard

1. Go to: https://vercel.com/admin-jetseteditas-projects/tenacious-stats-dashboard/settings
2. Scroll to **"Deployment Protection"** section
3. Enable **"Protection Bypass for Automation"**
4. **Copy the secret token** that appears

### 2. Add Secret as Environment Variable

The secret will automatically be available as `VERCEL_PROTECTION_BYPASS` in your deployments.

You can also add it manually:
```powershell
# Get the secret from Vercel dashboard, then:
echo "YOUR_SECRET_HERE" | vercel env add VERCEL_PROTECTION_BYPASS production preview development
```

### 3. Use the Bypass

The frontend (`public/index.html`) has been updated to automatically use the bypass secret in two ways:

**Option A: URL Parameter** (for testing)
```
https://your-deployment.vercel.app/?x-vercel-protection-bypass=YOUR_SECRET
```

**Option B: HTTP Header** (automatic in code)
The frontend will automatically add the header if the secret is available.

### 4. Test It

After enabling and getting the secret, you can test with the current deployment URL (see **Deployments** below) or:
```
https://your-deployment.vercel.app/?x-vercel-protection-bypass=YOUR_SECRET
```

## Deployments (for reference)

| Deployed   | Deployment URL |
|-----------|----------------|
| 12 Dec 2025 | `tenacious-stats-dashboard-33ezfj9nh-admin-jetseteditas-projects.vercel.app` |
| (earlier) | `tenacious-stats-dashboard-737a0t0op-admin-jetseteditas-projects.vercel.app` |

Use the latest URL with the bypass param when testing:  
`https://tenacious-stats-dashboard-33ezfj9nh-admin-jetseteditas-projects.vercel.app/?x-vercel-protection-bypass=YOUR_SECRET`

## How It Works

The frontend code now:
1. Checks for bypass secret in URL parameter
2. Automatically adds it to all API requests (as header or query param)
3. Works seamlessly once the secret is set

## Security

- The secret is long and random (secure)
- Only people with the secret can bypass protection
- Regular users still see the login screen
- Perfect for automation and trusted access










