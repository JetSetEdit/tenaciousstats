# Tenacious Stats

GA4 analytics dashboard + API. One HTML dashboard and a FastAPI backend; runs locally or on Vercel/Docker.

## Quick start

```bash
pip install -r api/requirements.txt
python run_vercel_local.py
```

Open **http://localhost:8000** (dashboard and API).

- **Credentials:** Put `credentials.json` (GA4 service account) in the project root. See [SETUP.md](SETUP.md).
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Docker:** [README.DOCKER.md](README.DOCKER.md) / [DOCKER_SETUP.md](DOCKER_SETUP.md)

## Repo layout

| Path | Purpose |
|------|--------|
| `public/` | Dashboard (index.html, keyterms.json, version.txt) |
| `api/` | FastAPI app: GA4 analytics + optional GBP (index.py, gbp.py) |
| `utils/` | GA4 helpers (ga4_utils.py) |
| `run_vercel_local.py` | Serves dashboard + API on port 8000 |
| `vercel.json` | Vercel build/rewrites |
| `Dockerfile`, `docker-compose*.yml` | Docker run |

## Deploy

- **Vercel:** Connect this repo; set `PROPERTY_ID` and `GOOGLE_APPLICATION_CREDENTIALS` (or base64) in project env.
- **Docker:** `docker-compose -f docker-compose.dev.yml up`
