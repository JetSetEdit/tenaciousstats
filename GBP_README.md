# Google Business Profile (GBP) – What We Know

## Backend (`api/gbp.py`)

### Credentials (in order of use)

1. **OAuth token (Vercel):** `GOOGLE_OAUTH_TOKEN_B64` – base64-encoded pickle of OAuth credentials.
2. **OAuth token (local):** `token.pickle` in project root – OAuth credentials from desktop flow. **Use the Google account that owns your Business Profile** (e.g. `tenacioustapesmedia@gmail.com`). Run `python gbp_oauth_login.py` to create `token.pickle`; sign in with that account when the browser opens.
3. **Service account (env):** `GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64` – base64-encoded service account JSON.
4. **Service account (file):** `gbp-service-account-key.json` in project root or `api/`.

**Scope:** `https://www.googleapis.com/auth/business.manage`

### APIs used

| API | Purpose |
|-----|--------|
| **My Business Account Management** (`mybusinessaccountmanagement`) | List accounts → first account ID. |
| **My Business Business Information** (`mybusinessbusinessinformation`) | List locations for that account → first location. |
| **Business Profile Performance** (`businessprofileperformance`) | `fetchMultiDailyMetricsTimeSeries` for insights (impressions, clicks, directions, calls, etc.). |
| **My Business Reviews** (`mybusinessreviews`) | List reviews for that location. |

### Behaviour

- **`get_insights(start_date, end_date)`**  
  Uses the first account and first location, then calls Performance API for daily metrics (desktop/mobile Maps & Search impressions, conversations, direction requests, call clicks, website clicks, bookings, food orders, etc.). Returns `{ success, data: multiDailyMetricTimeSeries, location }` or `{ error }`.

- **`get_reviews()`**  
  Same account/location; calls Reviews API. Returns `{ success, reviews[], averageRating, totalReviewCount }` or `{ error }`.

### API routes (`api/index.py`)

- **`GET /api/gbp/insights`** – optional query: `start_date`, `end_date`. Calls `gbp.get_insights()`.
- **`GET /api/gbp/reviews`** – no query params. Calls `gbp.get_reviews()`.

If the `gbp` module fails to import, these return **503** “GBP module not available”.

---

## Frontend (dashboard) – aligned

- **Section:** “Business Profile” in the sidebar (checkbox).
- **Calls (correct):**
  - `GET /api/gbp/ratings` – ratings summary (averageRating, totalReviews, ratingDistribution).
  - `GET /api/gbp/reviews` – list of reviews + averageRating, totalReviewCount; response includes `data` and `reviews`.
  - `GET /api/gbp/insights?start_date=&end_date=` – insights; response includes `summary` with `views: { search, maps }` and `customerActions: { websiteClicks, directionRequests }`.

The dashboard uses these paths and response shapes. If GBP credentials are missing or the API returns an error, the section shows a short message and/or error.

---

## API routes (current)

| Route | Purpose |
|-------|--------|
| `GET /api/gbp/ratings` | Ratings summary: `{ success, data: { averageRating, totalReviews, ratingDistribution } }`. Derived from reviews. |
| `GET /api/gbp/reviews` | Reviews list: `{ success, reviews, data, averageRating, totalReviewCount }`. |
| `GET /api/gbp/insights?start_date=&end_date=` | Performance metrics: raw `data` (time series) + `summary`: `{ views: { search, maps }, customerActions: { websiteClicks, directionRequests } }`. |

---

## What’s left: credentials

1. **Credentials**  
   - **OAuth:** `token.pickle` (local) or `GOOGLE_OAUTH_TOKEN_B64` (Vercel) with scope `business.manage`.  
   - **Service account:** `gbp-service-account-key.json` in project root or `GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64`.  
   - **Note:** GBP often requires OAuth or specific Business Profile access for the account; service accounts may need to be granted access to the profile.

2. **Google Cloud**  
   - Enable: My Business Account Management, My Business Business Information, Business Profile Performance, My Business Reviews (exact names may vary in the console).

3. **"No locations found" / Business Profile used to work but stopped**  
   **→ See [FIX_BUSINESS_PROFILE.md](FIX_BUSINESS_PROFILE.md) for step-by-step fix.**  
   Usually the **OAuth token expired** (token.pickle or GOOGLE_OAUTH_TOKEN_B64). The app then falls back to a service account that has account access but **no locations** under that account. Fix: run `python gbp_oauth_login.py` and sign in with the Google account that **owns** the Business Profile (e.g. tenacioustapesmedia@gmail.com). That refreshes `token.pickle` locally; for Vercel, re-encode the new token and update `GOOGLE_OAUTH_TOKEN_B64`.  
   In general: the account in use has no Business Profile locations. (a) Use OAuth from the **same Google account** that owns/manages the business at business.google.com; (b) If using a service account, the Business Profile owner must **invite that account as a manager** (business.google.com → Users and access), or use OAuth instead; (c) Claim a business at business.google.com with that account.

4. **Creating `token.pickle` (OAuth for Business Profile)**  
   - Use the Google account that **owns** your Business Profile (e.g. **tenacioustapesmedia@gmail.com**).  
   - In Google Cloud Console: create an **OAuth 2.0 Client ID** (Desktop application), download the JSON, save as `client_secrets.json` in the project root.  
   - Run: `python gbp_oauth_login.py`. A browser will open; **sign in with tenacioustapesmedia@gmail.com** (or the account that owns the business). The script saves credentials to `token.pickle`.  
   - Restart the app and refresh the dashboard; Business Profile will use that account's locations.

5. **Test**  
   - Run `python check_google_auth.py` to verify GA4 and GBP credentials (uses same logic as the app; gcloud ADC is checked too).  
   - Run `python run_vercel_local.py`, open the dashboard, check “Business Profile”, and click Refresh. With valid credentials you should see ratings, reviews, and insights (or a clear error from the API).
