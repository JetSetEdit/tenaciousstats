# Markdown docs in this codebase

Quick reference to all `.md` files and what they cover.

## Setup & running

| File | Purpose |
|------|--------|
| **SETUP.md** | GA4 auth, `pip install`, running Streamlit dashboard (`streamlit run dashboard.py` @ :8501) |
| **ENV_SETUP.md** | (Minimal) env setup |
| **QUICK_ENV_SETUP.txt** | Quick env / Vercel env steps (plain text) |
| **CLI_ENV_SETUP.md** | Vercel CLI and env vars (PROPERTY_ID, GOOGLE_APPLICATION_CREDENTIALS_B64) |
| **COMPLETE_CLI_SETUP.md** | Full CLI + env setup for deployment |

## Deployment

| File | Purpose |
|------|--------|
| **VERCEL_DEPLOY.md** | Vercel deploy steps, env vars, `vercel dev` |
| **README.DOCKER.md** | Docker dev: `docker-compose -f docker-compose.dev.yml up`, :8080 / :8000 |
| **DOCKER_SETUP.md** | Full Docker setup, nginx frontend :8080, backend :8000 |
| **DEPLOYED_SITE_AUDIT.md** | Audit: what’s on the live site vs this repo (frontend, API, logo) |

## Protection & access

| File | Purpose |
|------|--------|
| **PROTECTION_BYPASS_SETUP.md** | Vercel Deployment Protection + bypass secret |
| **PROTECTION_BYPASS_GUIDE.md** | How to use bypass (URL param, cookie, fetch) |

## Google Business Profile (GBP)

| File | Purpose |
|------|--------|
| **GBP_IMPLEMENTATION_SUMMARY.md** | GBP API integration, endpoints, local/Vercel |
| **GBP_API_ACCESS_FORM_GUIDE.md** | How to fill the GBP API access form |
| **GBP-API-HANDOVER.md** | Handover notes (feed, RSS, chosen URLs) |

## Project structure & templates

| File | Purpose |
|------|--------|
| **ARCHITECTURE.md** | Primary stack (HTML + api/index.py, run_vercel_local.py), API paths, /api prefix |
| **TEMPLATE_README.md** | Streamlit dashboard template (components, ga4_utils) |
| **VERSION_SYSTEM.md** | Version display (version.txt, footer “Build vX.X.X”) |

## Reports (content / drafts)

| File | Purpose |
|------|--------|
| **Monthly_Report_November_2025.md** | Monthly report content |
| **Report_Dec_01_to_Dec_10_2025.md** | Dec 1–10 report |
| **report_draft.md** | Report draft |
| **analytics_report_draft.md** | Analytics report draft |

## Other

| File | Purpose |
|------|--------|
| **vercel-deployment-download/src/VERCEL_DEPLOY.md** | Copy of Vercel deploy guide in download folder |

---

**Health / API base:** Docs now use **`/api/health`** and **`/api/analytics/*`** where applicable (ARCHITECTURE, README.DOCKER, DOCKER_SETUP, VERCEL_DEPLOY, GBP_IMPLEMENTATION_SUMMARY, PROTECTION_BYPASS_GUIDE).
