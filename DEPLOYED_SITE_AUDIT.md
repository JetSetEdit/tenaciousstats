# Audit: Codebase vs Deployed Site

**Deployed site:** https://tenacious-stats-dashboard.vercel.app/

This document compares what the deployed site shows vs what exists in this codebase.

---

## What the deployed site has

- **Password protection** (Vercel Deployment Protection screen)
- **Tenacious Tapes Logo** in header
- **Header:** Tenacious Stats Dashboard · Analytics for Tenacious Tapes - Adhesive Tapes for every application
- **Nav:** Dashboard | Glossary
- **Date range:** Start Date, End Date
- **Tabs:** Overview | Traffic Sources | Top Pages | User Retention | Geographics | Tech/Devices | Events | Business Profile
- **Buttons:** Refresh Data · Generate Monthly Report
- **Configuration** section
- **Full Analytics Glossary** with Print Glossary, term tables (Executive Summary, Traffic Sources, Top Pages, Retention, Geography & Devices, Events)
- **Footer:** Tenacious Tapes, contact info, **Build v1.0.0**

---

## What exists in this codebase

### Frontend (`public/index.html`)

| Deployed feature | In codebase? | Notes |
|------------------|--------------|--------|
| Password protection | No | Handled by Vercel (not in repo) |
| Tenacious Tapes Logo | No | No logo image or component in repo |
| Subtitle "Adhesive Tapes for every application" | No | Header only has "Analytics for Tenacious Tapes" |
| Dashboard / Glossary nav | No | No nav between Dashboard and Glossary |
| Tab: Overview | Partial | Only "Traffic Overview" section, no tab bar |
| Tab: Traffic Sources | No | Not in public/index.html |
| Tab: Top Pages | No | Not in public/index.html |
| Tab: User Retention | No | Not in public/index.html |
| Tab: Geographics | No | Not in public/index.html |
| Tab: Tech/Devices | No | Not in public/index.html |
| Tab: Events | No | Not in public/index.html |
| Tab: Business Profile | Yes | GBP section with Insights/Reviews |
| "Refresh Data" button | No | Has "Load Data" only |
| "Generate Monthly Report" button | No | Not present |
| Glossary page | No | keyterms.json exists but no Glossary UI in index.html |
| Print Glossary | No | No print/glossary UI |
| Footer with Build version | No | No version in footer |

**Conclusion:** The local `public/index.html` is a **simplified** dashboard (Traffic Overview + GBP only). It does **not** contain the full UI shown on the deployed site.

### API (`api/index.py`)

| Deployed section | Endpoint needed | In api/index.py? |
|------------------|-----------------|-------------------|
| Overview | `/api/analytics/overview` | Yes |
| Traffic Sources | `/api/analytics/sources` | Yes |
| Top Pages | `/api/analytics/pages` | Yes |
| User Retention | e.g. `/api/analytics/retention` (newVsReturning) | **No** |
| Geographics (countries) | e.g. `/api/analytics/countries` | **No** (only `cities`) |
| Geographics (cities) | `/api/analytics/cities` | Yes |
| Tech/Devices | e.g. `/api/analytics/devices` (deviceCategory) | **No** |
| Events | `/api/analytics/events` | Yes |
| Business Profile | `/api/gbp/insights`, `/api/gbp/reviews` | Yes |

**Note:** `api/backend.py` has retention, country, and device logic, but **api/index.py** (used by Vercel) does not expose those endpoints.

### Other assets

| Asset | Present? |
|-------|----------|
| `public/keyterms.json` | Yes (glossary data) |
| `public/version.txt` | Yes (value 1.0.14 locally; deployed shows v1.0.0) |
| Logo image | No |

---

## Summary

**The codebase does NOT currently contain everything needed to produce the deployed site.**

1. **Frontend:** `public/index.html` is a reduced version. Missing: Dashboard/Glossary nav, all section tabs (Traffic Sources, Top Pages, Retention, Geographics, Tech/Devices, Events), Glossary page, Refresh Data, Generate Monthly Report, logo, version footer.
2. **API:** Missing endpoints for **retention** (newVsReturning), **countries**, and **devices** (deviceCategory) in `api/index.py`.
3. **Logo:** Not in repo (deployed site shows "Tenacious Tapes Logo").
4. **Password:** Vercel Deployment Protection only; no code in repo.

The deployed site was likely built from a different or older version of the dashboard (e.g. another branch, or a build that included the full UI). The `vercel-deployment-download` folder contains a very large `index.html` (200k+ chars, likely minified/bundled) that may be the deployed build output, not the source.

---

## Recommendations

1. **Restore or rebuild the full dashboard UI** in `public/index.html`: tabs, Glossary page (using `keyterms.json`), Refresh Data, Generate Monthly Report, logo reference, version footer.
2. **Add missing API endpoints** in `api/index.py`: retention (newVsReturning), countries, devices (deviceCategory). Logic can be copied from `api/backend.py` or `utils/ga4_utils.py`.
3. **Add logo:** Use the Tenacious Tapes logo URL or asset (e.g. `https://www.tenacioustapes.com.au/wp-content/uploads/2025/12/tenacious-tapes-logo-scaled.png`) in the header.
4. **Wire version:** Have the footer read `version.txt` (or build version) and display "Build vX.X.X".
