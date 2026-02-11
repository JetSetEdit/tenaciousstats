#!/usr/bin/env python3
"""Hit all dashboard API endpoints and report success/data for each section.
Requires server running: python run_vercel_local.py (restart after adding /api/gbp/ratings)."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta

import os
BASE = os.environ.get("API_BASE", "http://localhost:8000")
end = datetime.now()
start = end - timedelta(days=30)
start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")

def get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        q = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{q}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {"error": body or str(e)}
        return e.code, data
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}

def has_data(resp, key="data"):
    if not isinstance(resp, dict):
        return False
    d = resp.get(key)
    if d is None:
        d = resp.get("summary")
    if d is None:
        return False
    if isinstance(d, list):
        return len(d) > 0
    if isinstance(d, dict):
        return True
    return False

def data_summary(body, data_key):
    """Return a short summary of what data is present (count or key fields)."""
    if not isinstance(body, dict):
        return "?"
    d = body.get(data_key)
    if d is None:
        d = body.get("summary")
    if d is None:
        return "no key"
    if isinstance(d, list):
        return f"{len(d)} rows"
    if isinstance(d, dict):
        if data_key == "data" and "sessions" in d:
            return f"sessions={d.get('sessions', '?')}"
        return f"{len(d)} fields"
    return "?"

sections = [
    ("Overview", "/api/analytics/overview", {"start_date": start_str, "end_date": end_str}, "data", "object"),
    ("Traffic Sources", "/api/analytics/sources", {"start_date": start_str, "end_date": end_str, "limit": "10"}, "data", "list"),
    ("Top Pages", "/api/analytics/pages", {"start_date": start_str, "end_date": end_str, "limit": "20"}, "data", "list"),
    ("User Retention", "/api/analytics/retention", {"start_date": start_str, "end_date": end_str}, "data", "list"),
    ("Geographics (cities)", "/api/analytics/cities", {"start_date": start_str, "end_date": end_str, "limit": "10"}, "data", "list"),
    ("Geographics (countries)", "/api/analytics/countries", {"start_date": start_str, "end_date": end_str}, "data", "list"),
    ("Tech/Devices", "/api/analytics/devices", {"start_date": start_str, "end_date": end_str}, "data", "list"),
    ("Events", "/api/analytics/events", {"start_date": start_str, "end_date": end_str, "limit": "20"}, "data", "list"),
    ("Business Profile (ratings)", "/api/gbp/ratings", None, "data", "object"),
    ("Business Profile (reviews)", "/api/gbp/reviews", None, "reviews", "list"),
    ("Business Profile (insights)", "/api/gbp/insights", {"start_date": start_str, "end_date": end_str}, "summary", "object"),
]

print("Checking all dashboard sections at", BASE)
print("Date range:", start_str, "to", end_str)
print("-" * 60)

ok = 0
fail = 0
for name, path, params, data_key, _ in sections:
    code, body = get(path, params or {})
    success = body.get("success") if isinstance(body, dict) else (code == 200)
    has = has_data(body, data_key) if success else False
    # Endpoint works if 200+success, or GBP 500 "No locations found" (config issue, not broken code)
    err = body.get("error")
    if not err and isinstance(body, dict):
        d = body.get("detail")
        err = d if isinstance(d, str) else None
    gbp_no_location = code == 500 and err and "No locations" in str(err)
    endpoint_ok = (code == 200 and success) or (gbp_no_location and "gbp" in path.lower())
    status = "OK" if endpoint_ok else "FAIL"
    data_note = "has data" if has else ("no data (GBP not configured)" if gbp_no_location else "no data")
    if endpoint_ok:
        ok += 1
    else:
        fail += 1
    err_str = f" - {err}" if err and not gbp_no_location else ""
    summary = data_summary(body, data_key) if endpoint_ok and (code == 200 and success) else ""
    summary_str = f" [{summary}]" if summary else ""
    print(f"  {status}  {name}: HTTP {code}, success={success}, {data_note}{summary_str}{err_str}")

print("-" * 60)
print(f"Result: {ok} OK, {fail} FAIL")
if fail > 0:
    exit(1)
exit(0)
