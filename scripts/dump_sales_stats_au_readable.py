"""
Dump Sales-stats-equivalent GA4 data to a UTF-8 text file.

Run from project root:
  python scripts/dump_sales_stats_au_readable.py              # Australia only (default)
  python scripts/dump_sales_stats_au_readable.py --all-locations   # no country filter
"""
from __future__ import annotations

import argparse
import calendar
import os
import sys
from typing import Any

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from fastapi.testclient import TestClient
from api.index import app

YEAR = 2026
MONTHS = [1, 2, 3, 4]


def month_range(y: int, m: int) -> tuple[str, str]:
    _, last = calendar.monthrange(y, m)
    return f"{y}-{m:02d}-01", f"{y}-{m:02d}-{last:02d}"


def prev_ym(y: int, m: int) -> tuple[int, int]:
    if m <= 1:
        return y - 1, 12
    return y, m - 1


def resolve_oar_slug(paths: dict, titles: dict, year: int, month_num: int) -> tuple[str, str]:
    y, m = year, month_num
    for _ in range(24):
        key = f"{y}-{m:02d}"
        slug = (paths or {}).get(key) or ""
        slug = str(slug).strip()
        if slug:
            title = str((titles or {}).get(key) or "").strip()
            return slug, title
        y, m = prev_ym(y, m)
    return "", ""


def fnum(x: Any) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump Sales-stats-equivalent GA4 data.")
    parser.add_argument(
        "--all-locations",
        action="store_true",
        help="All locations (do not pass au_only; matches Sales stats with Australia only OFF).",
    )
    args = parser.parse_args()
    au_only = not args.all_locations
    scope_params = {"au_only": "true"} if au_only else {}
    scope_tag = "au_only=true" if au_only else "all_locations (au_only off)"
    out_name = "sales_stats_au_jan_apr_2026_readable.txt" if au_only else "sales_stats_all_jan_apr_2026_readable.txt"
    out_path = os.path.join(_root, out_name)

    c = TestClient(app)

    oar = c.get("/api/on-a-roll-slugs").json()
    oar_data = (oar.get("data") or {}) if oar.get("success") else {}
    paths = oar_data.get("featuredPathContains") or {}
    titles = oar_data.get("featuredTitles") or {}

    lines: list[str] = []
    title_scope = "Australia only (GA4)" if au_only else "All locations (GA4, no country filter)"
    lines.append(f"Tenacious Stats — Sales stats dump ({title_scope})")
    lines.append(f"Year {YEAR}, months: {', '.join(calendar.month_name[m] for m in MONTHS)}")
    tab_note = "Australia only ON" if au_only else "Australia only OFF"
    lines.append(f"Generated via API (same endpoints as Sales stats tab; {tab_note}).")
    lines.append("")

    for m in MONTHS:
        sd, ed = month_range(YEAR, m)
        slug, title = resolve_oar_slug(paths, titles, YEAR, m)
        params = {"start_date": sd, "end_date": ed, **scope_params}

        ov = c.get("/api/analytics/overview", params=params).json()
        src = c.get("/api/analytics/sources", params={**params, "limit": 15}).json()
        pgs = c.get("/api/analytics/pages", params={**params, "limit": 100}).json()
        cts = c.get("/api/analytics/cities", params={**params, "limit": 50}).json()
        evs = c.get("/api/analytics/events", params={**params, "limit": 50}).json()

        path_views = {}
        if slug:
            pv = c.get(
                "/api/analytics/path-views-total",
                params={**params, "path": slug, "match": "contains"},
            ).json()
            path_views = pv

        name = calendar.month_name[m]
        lines.append("=" * 72)
        lines.append(f"{name} {YEAR}  ({sd} .. {ed})  [{scope_tag}]")
        lines.append("=" * 72)

        if ov.get("success") and ov.get("data"):
            d = ov["data"]
            er = fnum(d.get("engagementRate"))
            er_pct = er * 100 if 0 <= er <= 1 else er
            lines.append("At a glance:")
            lines.append(f"  Sessions:        {int(fnum(d.get('sessions'))):,}")
            lines.append(f"  Users:           {int(fnum(d.get('totalUsers'))):,}")
            lines.append(f"  Page views:      {int(fnum(d.get('screenPageViews'))):,}")
            lines.append(f"  Engagement rate: {er_pct:.1f}%")
            lines.append("")
        else:
            lines.append(f"Overview error: {ov}")
            lines.append("")

        lines.append(f"On a Roll (RSS slug for month, path-views contains '{slug or '(none)'}'):")
        if slug:
            lines.append(f"  Title: {title or '—'}")
            if path_views.get("success"):
                lines.append(f"  Screen page views (contains): {path_views.get('data', {}).get('screenPageViews', '—')}")
            else:
                lines.append(f"  path-views response: {path_views}")
        else:
            lines.append("  (no slug from RSS for this month after lookback)")
        lines.append("")

        buy = 0
        if evs.get("success") and evs.get("data"):
            for row in evs["data"]:
                if (row.get("eventName") or "") == "click_buy_online":
                    buy = int(fnum(row.get("eventCount")))
                    break
        lines.append(f"Buy online clicks (event click_buy_online): {buy}")
        lines.append("")

        if src.get("success") and src.get("data"):
            total = sum(fnum(r.get("sessions")) for r in src["data"])
            lines.append("Top channels (share of month sessions in this top-15 list):")
            for r in src["data"][:8]:
                s = fnum(r.get("sessions"))
                pct = (100.0 * s / total) if total else 0.0
                ch = r.get("sessionSourceMedium") or "(not set)"
                lines.append(f"  {s:,.0f}  ({pct:4.1f}%)  {ch}")
            lines.append("")

        if pgs.get("success") and pgs.get("data"):
            lines.append("Top pages by screen views (up to 10):")
            for i, r in enumerate(pgs["data"][:10], 1):
                v = int(fnum(r.get("screenPageViews")))
                pt = (r.get("pageTitle") or "")[:60]
                pp = r.get("pagePath") or ""
                lines.append(f"  {i:2}. {v:5d}  {pt}  |  {pp}")
            lines.append("")

        capitals = [
            "Sydney",
            "Melbourne",
            "Brisbane",
            "Adelaide",
            "Perth",
            "Hobart",
            "Canberra",
            "Darwin",
        ]
        if cts.get("success") and cts.get("data"):
            by_city = {r.get("city"): int(fnum(r.get("sessions"))) for r in cts["data"]}
            lines.append("Australian capitals (sessions, if present in city breakdown):")
            for city in capitals:
                lines.append(f"  {city}: {by_city.get(city, 0):,}")
            lines.append("")

    text = "\n".join(lines) + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
