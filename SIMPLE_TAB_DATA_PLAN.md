# Jan–Apr tab — developer notes (data wiring)

*Internal reference.* The **Web stats** table on the **Jan–Apr** tab loads live site data via the same backend as the main dashboard.

## Existing endpoints (same as main Dashboard)

All take `start_date` and `end_date` as `YYYY-MM-DD` (GA4 format).

| Simple table row | Data | Endpoint | Notes |
|------------------|------|----------|--------|
| **Sessions** | `sessions` | `GET /api/analytics/overview?start_date=&end_date=` | From `data.sessions` |
| **Users** | `totalUsers` | same | `data.totalUsers` |
| **Engagement** | `engagementRate` | same | Show as % (`* 100`); or keep “trend line” note if you prefer visual-only later |
| **Sources** (badges) | Top sources + % of month sessions | `GET /api/analytics/sources?start_date=&end_date=&limit=10` | Each row: `sessionSourceMedium`, `sessions`. Compute % = row / sum(sessions) × 100. Take top 3 for badges. |
| **Top pages (Jan–Apr)** | **Page \| Views** repeated four times (aligned with main **January \| February \| March \| April** columns; no month abbreviations in the subtable) | `GET /api/analytics/pages` × 4 months, **`limit=100`** | Per month: sort by `screenPageViews` desc. **Row *i*** = rank *i* (1–5) for **each** month side by side: that month’s page title/path + views. Empty rank → **—**. |
| **On a Roll — featured** | Views on that month’s article | `GET /api/analytics/path-views-total?...&match=contains` + slug | **Default:** `GET /api/on-a-roll-slugs` returns `featuredPathContains` + `featuredTitles` from RSS (`<link>` slug + `<title>` ≈ page H1). **Overrides:** `on_a_roll.json` → `featuredPathContains` / `featuredTitles` merged on top. `useRss: false` → JSON only. Optional `rssFeedUrl`. |
| **Blog (legacy API)** | — | `GET /api/analytics/blog-path-views` | Still available; Simple tab no longer uses it. |
| **Australian capitals** | Sessions per city | `GET /api/analytics/cities?start_date=&end_date=&limit=50` | Same eight capitals — **only if sessions &gt; 0**, **sorted high → low** (no “Other” row). |
| **Buy online clicks** | Event count | `GET /api/analytics/events?start_date=&end_date=&limit=50` | Find row where `eventName === 'click_buy_online'` → `eventCount` |

## Phase 1: January only

1. Fix **January** as `start_date=YYYY-01-01`, `end_date=YYYY-01-31` (pick year in UI or config).
2. From the **browser**, call the endpoints above **without** `compare_*` params.
3. Leave **February–April** columns empty (or “—”) until Phase 2.
4. **Phase 2:** repeat the same fetches for each month, or add **one** aggregated endpoint later (optional).

## Gaps / optional backend work

| Need | Options |
|------|--------|
| **On a Roll slugs** | **RSS (default):** `/api/on-a-roll-slugs` reads the WordPress feed; no monthly JSON edit required. **Manual:** set `useRss: false` or add `featuredPathContains` overrides per `YYYY-MM`. |
| **Faster load (optional)** | `GET /api/analytics/simple-month?year=2026&month=1` that runs 4–5 internal queries and returns one JSON shaped for the table. Not required for Jan MVP. |

## What we do *not* need for this table

- **GBP** (`/api/gbp/*`) — not in the Simple mock.
- **Email campaigns** — separate JSON; only if you add a row later.

## Summary

- **You already have** the APIs for sessions, users, engagement, sources, top pages, cities, and events.
- **Start with January:** 5–6 parallel `fetch()` calls from the Simple tab, then render one column.
- **On a Roll — featured** uses `path-views-total` (contains) + `on_a_roll.json` / RSS for monthly slug.

## Scaling to 12 months

- **Layout:** The main table uses `min-width: calc(13rem + var(--simple-month-count) * 5.25rem)` and a horizontal scroll wrapper (`.simple-stats-table-scroll`) so many narrow month columns stay readable.
- **CSS:** `--simple-month-count` is set from `SIMPLE_STATS_MONTH_INDICES.length` on load. Column widths use `--simple-month-block-pct`. Q1 subtable month dividers and band colours use repeating `nth-child` patterns (not hard‑limited to four months).
- **JavaScript:** `SIMPLE_STATS_MONTH_INDICES` drives `Promise.all` and all nested tbody renderers. **You must add matching markup:** one `<col class="simple-col-month">` + `<th>` + `simple-m{k}-*` cells per month (and the same count in subtables / `colspan`s), or generate those rows in JS.
- **Performance:** 12 months × ~6 parallel requests per month is a lot of traffic; consider a combined `/api/analytics/simple-month` (or batched) endpoint later.

## Implemented (Jan–Apr tab)

- **At a glance** (one accordion block): visits, people, engagement, **buy online clicks**, **On a Roll**; then **Where visits came from**, **Popular pages** (top pages grid only), **Geography**. (No separate **Actions** section.)
- **Print / PDF:** `@page janmar-landscape` + `page: janmar-landscape` on `#simple-section` when the Jan–Apr tab is active — **A4 landscape** for that print job (Chromium / Firefox / recent Safari). If the preview stays portrait, choose **Landscape** in the print dialog as a fallback.
- **Load Jan–Apr** button + **year** field.
- Parallel calls per month ×4: `overview`, `sources` (15), `pages` (**100** merge), **`path-views-total`** (featured contains only), `cities` (50), `events` (50).
- **On a Roll — featured:** RSS via `/api/on-a-roll-slugs` + `on_a_roll.json` (optional overrides) + `path-views-total` (contains).
- **Top pages:** 5 rows × **Page + month metric** quadruplet (rank *i* in Jan, Feb, Mar, Apr independently); `limit=100` on the pages API pull.
