# Vercel Deployment Guide

## Architecture

```
Vercel Deployment:
├── api/                    # Serverless functions (FastAPI backend)
│   └── index.py           # Main API handler
├── public/                 # Static frontend
│   └── index.html         # Web dashboard
└── vercel.json            # Vercel configuration
```

## Deployment Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

Or deploy to production:
```bash
vercel --prod
```

## Environment Variables

Set these in Vercel Dashboard (Settings > Environment Variables):

1. **PROPERTY_ID**: `368035934`
2. **GOOGLE_APPLICATION_CREDENTIALS**: (Base64 encoded JSON or use Application Default Credentials)

### Option A: Service Account JSON (Base64)
1. Encode your `credentials.json`:
```bash
# On Mac/Linux
base64 -i credentials.json

# On Windows (PowerShell)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
```

2. Set in Vercel as `GOOGLE_APPLICATION_CREDENTIALS` (base64 string)

3. Update `api/index.py` to decode:
```python
import base64
import json

if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    creds_json = base64.b64decode(os.environ['GOOGLE_APPLICATION_CREDENTIALS']).decode()
    with open('/tmp/credentials.json', 'w') as f:
        f.write(creds_json)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'
```

### Option B: Use Application Default Credentials
- Set up gcloud on Vercel (more complex)
- Or use a service account key stored securely

## Project Structure

```
.
├── api/
│   └── index.py           # FastAPI serverless function
├── public/
│   └── index.html         # Frontend dashboard
├── vercel.json            # Vercel config
├── requirements.txt       # Python dependencies
└── .vercelignore         # Files to exclude
```

## API Endpoints (after deployment)

- `https://your-project.vercel.app/api/` - API root
- `https://your-project.vercel.app/api/health` - Health check
- `https://your-project.vercel.app/api/analytics/overview` - Overview metrics
- `https://your-project.vercel.app/api/analytics/sources` - Traffic sources
- `https://your-project.vercel.app/api/analytics/pages` - Top pages
- etc.

## Frontend

The frontend is a static HTML file that calls the API endpoints. It will be available at:
- `https://your-project.vercel.app/`

## Troubleshooting

1. **API not working**: Check Vercel function logs
2. **Authentication errors**: Verify GOOGLE_APPLICATION_CREDENTIALS is set correctly
3. **CORS issues**: CORS is enabled for all origins (update for production)

## Local Testing

Test locally with Vercel CLI:
```bash
vercel dev
```

This will run the serverless functions locally and serve the static files.










