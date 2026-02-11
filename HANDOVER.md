# Tenacious Stats — Handover

**Last updated:** 2026-02-10  
**Machine-readable:** [handover.json](handover.json)

---

## 1. Project summary

- **What it is:** GA4 analytics dashboard + optional Google Business Profile (GBP). Single-page HTML dashboard + FastAPI backend; runs locally or on Vercel/Docker.
- **Live:** https://tenacious-stats-dashboard.vercel.app/ (password-protected).
- **Stack:** Python (FastAPI), GA4 Data API, optional GBP APIs; frontend: vanilla JS, Plotly, Chart.js, html2canvas/html2pdf.

---

## 2. What’s working

| Area | Status | Notes |
|------|--------|------|
| **GA4 analytics** | ✅ Working | All sections return data when `credentials.json` (or `GOOGLE_APPLICATION_CREDENTIALS_B64` on Vercel) is set. |
| **Overview** | ✅ | Sessions, users, page views, engagement rate, bounce rate, avg session duration. |
| **Traffic sources** | ✅ | Source/medium and sessions. |
| **Top pages** | ✅ | Page path, title, views, users. |
| **User retention** | ✅ | New vs returning sessions. |
| **Geographics** | ✅ | Cities and countries with sessions. |
| **Tech/Devices** | ✅ | Desktop, mobile, tablet. |
| **Events** | ✅ | Event names and counts. |
| **Period comparison** | ✅ | Month selectors and metrics comparison (tab). |
| **Monthly report (PDF)** | ✅ | Generate report with charts; Plotly loaded in page. |
| **Local dev** | ✅ | `python run_vercel_local.py` → http://localhost:8000; API base and static URLs correct for localhost. |
| **Vercel production** | ✅ | Dashboard and API work when env vars are set. |
| **Health / checks** | ✅ | `/api/health`; `python check_google_auth.py`; `python check_all_sections.py`. |

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

| Method | Path | Query | Purpose |
|--------|------|-------|---------|
| GET | `/api` | — | API info. |
| GET | `/api/health` | — | Health; reports GA4/GBP availability. |
| GET | `/api/analytics/overview` | start_date, end_date | Executive metrics. |
| GET | `/api/analytics/sources` | start_date, end_date, limit | Traffic sources. |
| GET | `/api/analytics/pages` | start_date, end_date, limit | Top pages. |
| GET | `/api/analytics/retention` | start_date, end_date | New vs returning. |
| GET | `/api/analytics/cities` | start_date, end_date, limit | Top cities. |
| GET | `/api/analytics/countries` | start_date, end_date | Sessions by country. |
| GET | `/api/analytics/devices` | start_date, end_date | Device categories. |
| GET | `/api/analytics/events` | start_date, end_date, limit | Top events. |
| GET | `/api/gbp/ratings` | — | GBP ratings summary. |
| GET | `/api/gbp/reviews` | — | GBP reviews. |
| GET | `/api/gbp/insights` | start_date, end_date (optional) | GBP insights. |

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
| `public/index.html` | Dashboard UI, report generation, Plotly charts. |
| `api/index.py` | FastAPI app and all API routes. |
| `api/gbp.py` | GBP credentials and API calls (insights, reviews, ratings). |
| `utils/ga4_utils.py` | GA4 client and credential setup (file + B64 env). |
| `run_vercel_local.py` | Serves app on port 8000. |
| `gbp_oauth_login.py` | Creates/refreshes `token.pickle` for GBP. |
| `check_google_auth.py` | Checks GA4 and GBP (including locations). |
| `check_all_sections.py` | Hits all section APIs and reports OK/FAIL. |
| `FIX_BUSINESS_PROFILE.md` | Steps to fix GBP when it “used to work”. |
| `handover.json` | Machine-readable handover (this doc in JSON). |

---

## 8. Handover checklist

- [ ] GA4: `credentials.json` in project root (or B64 on Vercel).
- [ ] GBP: Run `gbp_oauth_login.py` with business owner account; restart server.
- [ ] Confirm at [business.google.com](https://business.google.com) which account owns the profile.
- [ ] After code changes that add API routes, restart `run_vercel_local.py`.
- [ ] For production PDF/report, Plotly script is loaded in `index.html` (no “Plotly is not defined” if page loaded once).
