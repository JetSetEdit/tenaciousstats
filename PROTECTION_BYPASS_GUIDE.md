# Protection Bypass Setup Guide

## What is Protection Bypass?

This feature allows you to:
- ✅ Keep deployment protection enabled (secure for regular users)
- ✅ Allow automated services/scripts to access the deployment
- ✅ Use a secret token to bypass protection

## How to Set It Up

### Step 1: Enable in Vercel Dashboard

1. Go to: https://vercel.com/admin-jetseteditas-projects/tenacious-stats-dashboard/settings
2. Navigate to **Deployment Protection**
3. Enable **"Protection Bypass for Automation"**
4. Copy the secret token that's generated

### Step 2: Use the Bypass Secret

The secret will be available as an environment variable: `VERCEL_PROTECTION_BYPASS`

You can use it in two ways:

#### Option A: HTTP Header
```javascript
fetch('https://your-deployment.vercel.app/api/health', {
  headers: {
    'x-vercel-protection-bypass': 'YOUR_SECRET_HERE'
  }
})
```

#### Option B: Query Parameter
```
https://your-deployment.vercel.app/api/health?x-vercel-protection-bypass=YOUR_SECRET_HERE
```

### Step 3: Update Frontend (if needed)

If you want the frontend to work without authentication, you can:

1. **Option 1**: Add the bypass to all API calls in `public/index.html`
2. **Option 2**: Make the frontend public (disable protection for the root path)
3. **Option 3**: Keep protection on, users authenticate once, then use the site

## For Browser Testing

You can test with the bypass parameter:
```
https://your-deployment.vercel.app/?x-vercel-protection-bypass=YOUR_SECRET
```

## Security Note

⚠️ **Important**: 
- Don't commit the bypass secret to git
- Don't expose it in client-side code if you want to keep it secure
- Use it only for server-to-server or trusted automation

## Recommendation

For a public analytics dashboard, you might want to:
1. Keep API endpoints protected (or use bypass for server-side calls)
2. Make the frontend public (disable protection for `/` route)
3. Or use the bypass secret in your frontend if it's meant to be semi-private










