# Tenacious Stats — Handover

**Last updated:** 2026-02-10  
**Machine-readable:** [handover.json](handover.json)

---

## 1. Project summary

- **What it is:** GA4 analytics dashboard + optional Google Business Profile (GBP) + email campaign comparison. Single-page HTML dashboard + FastAPI backend; runs locally or on Vercel/Docker.
- **Live:** https://tenacious-stats-dashboard.vercel.app/ (password-protected).
- **Stack:** Python (FastAPI), GA4 Data API, optional GBP APIs; frontend: vanilla JS, Plotly, Chart.js, html2canvas/html2pdf.

---

## 2. What’s working

| Area | Status | Notes |
|------|--------|------|
| **GA4 analytics** | ✅ Working | All sections return data when `credentials.json` (or `GOOGLE_APPLICATION_CREDENTIALS_B64` on Vercel) is set. |
| **Month-over-month comparison** | ✅ | All GA4 endpoints accept optional `compare_start_date` / `compare_end_date`; responses include `*_compare` metric fields; dashboard shows % change and previous-period columns. |
| **Overview** | ✅ | Sessions, users, page views, engagement rate, bounce rate, avg session duration (+ compare). |
| **Traffic sources** | ✅ | Source/medium and sessions (+ compare). |
| **Top pages** | ✅ | Page path, title, views, users (+ compare). |
| **User retention** | ✅ | New vs returning sessions (+ compare). |
| **Geographics** | ✅ | Cities and countries with sessions (+ compare). |
| **Tech/Devices** | ✅ | Desktop, mobile, tablet (+ compare). |
| **Events** | ✅ | Event names and counts (+ compare). |
| **Business Profile** | ✅ Conditional | Ratings, reviews, insights when OAuth token valid and account has locations; default visibility restored (commit 28fb231). |
| **Email Campaigns** | ✅ | Section loads from static JSON at `public/data/email_campaigns.json`; dashboard and report show comparison chart (opens, clicks, etc.). Local server serves `/data/email_campaigns.json`. |
| **Period comparison tab** | ✅ | Month selectors and metrics comparison. |
| **Monthly report (PDF)** | ✅ | Generate report with charts; Plotly loaded; report CSS allows table/section break across pages (`overflow: visible`, `page-break-inside: auto`). |
| **Local dev** | ✅ | `python run_vercel_local.py` → http://localhost:8000 with **reload=True** (module string `run_vercel_local:app`). Serves /, /version.txt, /keyterms.json, /data/email_campaigns.json. |
| **Vercel production** | ✅ | Dashboard and API work when env vars are set; static mount serves `public/` including `/data/`. |
| **Health / checks** | ✅ | `/api/health`; `python check_google_auth.py`; `python check_all_sections.py`. |
| **Debug/test scripts** | ℹ️ | `debug_api_data.py`, `debug_ga4_dims.py`, `debug_ga4_raw.py`, `debug_ga4_rows.py`, `test_api_compare.py` for API/GA4 comparison testing. |

---

## 3. What’s not working / known issues

| Issue | Status | Mitigation |
|-------|--------|------------|
| **Business Profile — “No locations found”** | ⚠️ Conditional | Works when OAuth token is valid and the signed-in account has a Business Profile location. Stops when token expires or wrong account is used. See [FIX_BUSINESS_PROFILE.md](FIX_BUSINESS_PROFILE.md). |
| **Business Profile — wrong account** | ⚠️ | If the Google account used in `gbp_oauth_login.py` has no location in the API, dashboard shows no GBP data. Sign in with the account that owns the profile at [business.google.com](https://business.google.com). |
| **Business Profile on old server** | ⚠️ | If the server was started before `/api/gbp/ratings` was added, that route returns 404 until the server is restarted. |
| **Dashboard password** | ℹ️ | Hardcoded in `public/index.html` (client-side). Change there if required. |

---

## 4. Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `PROPERTY_ID` | No (default: 368035934) | GA4 property ID. |
| `GOOGLE_APPLICATION_CREDENTIALS_B64` | Yes for GA4 on Vercel | Base64-encoded GA4 service account JSON. |
| `GOOGLE_OAUTH_TOKEN_B64` | For GBP on Vercel | Base64-encoded OAuth token pickle for Business Profile. |
| `GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64` | Alternative for GBP | Base64-encoded GBP service account JSON (must have location access). |

**Local:** GA4 uses `credentials.json` in project root (or gcloud ADC). GBP uses `token.pickle` (from `python gbp_oauth_login.py`) or `gbp-service-account-key.json`.

---

## 5. API endpoints

All analytics endpoints accept optional **compare** params for month-over-month; when present, response rows include `metric_compare` (e.g. `sessions_compare`).

| Method | Path | Query | Purpose |
|--------|------|-------|---------|
| GET | `/api` | — | API info. |
| GET | `/api/health` | — | Health; reports GA4/GBP availability. |
| GET | `/api/analytics/overview` | start_date, end_date, compare_start_date?, compare_end_date? | Executive metrics. |
| GET | `/api/analytics/sources` | start_date, end_date, limit, compare_*? | Traffic sources. |
| GET | `/api/analytics/pages` | start_date, end_date, limit, compare_*? | Top pages. |
| GET | `/api/analytics/retention` | start_date, end_date, compare_*? | New vs returning. |
| GET | `/api/analytics/cities` | start_date, end_date, limit, compare_*? | Top cities. |
| GET | `/api/analytics/countries` | start_date, end_date, compare_*? | Sessions by country. |
| GET | `/api/analytics/devices` | start_date, end_date, compare_*? | Device categories. |
| GET | `/api/analytics/events` | start_date, end_date, limit, compare_*? | Top events. |
| GET | `/api/gbp/ratings` | — | GBP ratings summary. |
| GET | `/api/gbp/reviews` | — | GBP reviews. |
| GET | `/api/gbp/insights` | start_date, end_date (optional) | GBP insights. |

**Static (no API):** `/data/email_campaigns.json` — JSON array of email campaign stats (emailname, opens, clicks, bounces, etc.); used by Email Campaigns section.

---

## 6. How to run and verify

```bash
# Install
pip install -r api/requirements.txt

# Local server (dashboard + API)
python run_vercel_local.py
# → http://localhost:8000

# Verify GA4 + GBP credentials
python check_google_auth.py

# Verify all dashboard sections (API)
python check_all_sections.py
# Optional: API_BASE=http://localhost:8001 python check_all_sections.py
```

---

## 7. Key files

| File | Purpose |
|------|---------|
| `public/index.html` | Dashboard UI, report generation, Plotly charts, comparison UI, Email Campaigns. |
| `api/index.py` | FastAPI app; all analytics routes accept compare_start_date / compare_end_date. |
| `api/gbp.py` | GBP credentials (token.pickle first) and API (insights, reviews, ratings). |
| `utils/ga4_utils.py` | GA4 client; fetch_ga4_data supports compare dates and *_compare metrics. |
| `run_vercel_local.py` | Serves app on port 8000 with reload; routes for /, /version.txt, /keyterms.json, /data/email_campaigns.json. |
| `gbp_oauth_login.py` | Creates/refreshes `token.pickle` for GBP. |
| `check_google_auth.py` | Checks GA4 and GBP (including locations). |
| `check_all_sections.py` | Hits all section APIs and reports OK/FAIL. |
| `public/data/email_campaigns.json` | Static JSON for Email Campaigns comparison. |
| `debug_api_data.py`, `debug_ga4_*.py`, `test_api_compare.py` | Debug/test scripts for API and GA4 comparison. |
| `FIX_BUSINESS_PROFILE.md` | Steps to fix GBP when it “used to work”. |
| `handover.json` | Machine-readable handover (this doc in JSON). |

---

## 8. Handover checklist

- [ ] GA4: `credentials.json` in project root (or B64 on Vercel).
- [ ] GBP: Run `gbp_oauth_login.py` with business owner account; restart server.
- [ ] Confirm at [business.google.com](https://business.google.com) which account owns the profile.
- [ ] After code changes that add API routes, restart `run_vercel_local.py`.
- [ ] Email Campaigns: ensure `public/data/email_campaigns.json` exists; local server serves `/data/email_campaigns.json`.
- [ ] For production PDF/report, Plotly script is loaded in `index.html` (no “Plotly is not defined” if page loaded once).
