# Tenacious Stats – Architecture

## How to run it properly (quick reference)

1. **Dependencies**
   ```bash
   pip install -r api/requirements.txt
   ```
2. **Credentials (for GA4 + optional GBP)**  
   - GA4: `credentials.json` in project root (or set `GOOGLE_APPLICATION_CREDENTIALS`).  
   - GBP: service account key as used by `api/gbp.py` (see GBP docs).
3. **Start the full stack**
   ```bash
   python run_vercel_local.py
   ```
4. **Open** **http://localhost:8000** (dashboard + API from one process).
5. **Deploy:** Push to linked Git or run `vercel --prod`; set `PROPERTY_ID` and `GOOGLE_APPLICATION_CREDENTIALS_B64` (and GBP if needed) in Vercel.

The dashboard is **`public/index.html`**; the API is **`api/index.py`**. Local requests must use base **`http://localhost:8000/api`** (see `API_BASE` in the frontend).

---

## Primary Stack (Web Dashboard + API)

```
┌─────────────────────┐         HTTP/REST          ┌─────────────────────┐
│  HTML Dashboard    │  <──────────────────────>  │  FastAPI (api/)      │
│  public/index.html │   /api/analytics/*, /api/gbp/*  │  index.py (Vercel)   │
└─────────────────────┘                             └─────────────────────┘
                                                              │
                                                              ▼
                                                     ┌─────────────────────┐
                                                     │  GA4 API / GBP API  │
                                                     └─────────────────────┘
```

- **Single process:** `python run_vercel_local.py` serves both the dashboard and the API on **http://localhost:8000**.
- **Production:** Vercel serves `public/` as static and `api/index.py` as serverless; rewrites send `/api/*` to the API.

## Running Locally

### Full stack (recommended)

```bash
python run_vercel_local.py
```

- Dashboard: **http://localhost:8000**
- API docs: **http://localhost:8000/docs**
- Health: **http://localhost:8000/api/health**

### Alternative: Streamlit frontend + separate backend

```bash
# Terminal 1 – Backend (api/backend.py has retention, countries, devices)
python api/backend.py
# Terminal 2 – Streamlit UI
streamlit run dashboard_frontend.py
```

- Backend: **http://localhost:8000**
- Streamlit: **http://localhost:8501**

## API Endpoints (api/index.py)

All under `/api`:

- `GET /api/health` – Health check
- `GET /api/analytics/overview` – Overview metrics
- `GET /api/analytics/sources` – Traffic sources
- `GET /api/analytics/pages` – Top pages
- `GET /api/analytics/cities` – Top cities
- `GET /api/analytics/events` – Top events
- `GET /api/gbp/insights` – Google Business Profile insights
- `GET /api/gbp/reviews` – GBP reviews

*(api/backend.py also exposes retention, countries, devices; api/index.py does not.)*

## Benefits

1. **Separation of concerns:** UI in `public/`, data and auth in `api/`.
2. **Reusability:** Same API for web dashboard and (optionally) Streamlit.
3. **Deployment:** Same codebase runs locally (run_vercel_local.py) and on Vercel.
