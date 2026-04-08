# Sealrite WSM Stats

Welcome — this repo is the **Sealrite WSM** analytics hub: a single-page dashboard backed by a small Python API. Use it to review **Google Analytics 4** traffic, optional **Google Business Profile** metrics, and static **email campaign** data in one place.

**Customize branding** (logo, colours, titles, footer, client password) in [`public/dashboard-config.js`](public/dashboard-config.js). **Wire up data** with `PROPERTY_ID` and Google credentials (see [SETUP.md](SETUP.md)); nothing secret lives in that JS file except the lightweight dashboard gate.

This project was split out from the Tenacious Stats stack so Sealrite can evolve and deploy on its own while keeping the same architecture.

---

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
| `public/` | Dashboard (`index.html`, `dashboard-config.js` branding, `keyterms.json`, `version.txt`) |
| `api/` | FastAPI app: GA4 analytics + optional GBP (index.py, gbp.py) |
| `utils/` | GA4 helpers (ga4_utils.py) |
| `run_vercel_local.py` | Serves dashboard + API on port 8000 |
| `vercel.json` | Vercel build/rewrites |
| `Dockerfile`, `docker-compose*.yml` | Docker run |

## Deploy

- **Vercel:** Connect this repo; set `PROPERTY_ID` and `GOOGLE_APPLICATION_CREDENTIALS` (or base64) in project env.
- **Docker:** `docker-compose -f docker-compose.dev.yml up`
