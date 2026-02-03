# Tenacious Stats – Setup

## Prerequisites

- **Python 3.8+**
- **GA4** property with API access
- **Credentials:** service account JSON (see below)

## Install

```bash
pip install -r api/requirements.txt
```

## Credentials (GA4)

1. [Google Cloud Console](https://console.cloud.google.com/) → your project
2. Enable **Google Analytics Data API**
3. **IAM & Admin** → **Service Accounts** → create or use existing → create JSON key
4. Save as `credentials.json` in the **project root**
5. Grant the service account access to your GA4 property (e.g. Viewer)

Optional: use gcloud for dev instead of a file:

```bash
gcloud auth application-default login
```

## Run

```bash
python run_vercel_local.py
```

- **Dashboard:** http://localhost:8000  
- **API:** http://localhost:8000/api  
- **Health:** http://localhost:8000/api/health  

## Config

- **Property ID:** set in code (`api/index.py`, `utils/ga4_utils.py`) or via env `PROPERTY_ID` (default: 368035934)
- **Credentials path:** `credentials.json` in project root (or `GOOGLE_APPLICATION_CREDENTIALS`)

## Check Google auth (GA4 + GBP)

From project root:

```bash
python check_google_auth.py
```

Uses the same credential resolution as the app: `credentials.json` and gcloud ADC for GA4; `token.pickle`, `gbp-service-account-key.json`, or env vars for GBP. Reports whether each is OK or what’s missing.

## Troubleshooting

- **GA4 not available:** Ensure `credentials.json` is in the project root and the service account has access to the GA4 property.
- **404 on /api/analytics/***: Restart the server; ensure you open http://localhost:8000 (not a static file server on another port).
- **Docker:** See [README.DOCKER.md](README.DOCKER.md) / [DOCKER_SETUP.md](DOCKER_SETUP.md).
