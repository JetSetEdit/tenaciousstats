#!/usr/bin/env python3
"""
Check Google auth for GA4 and GBP using the same credential resolution as the app.
Run from project root: python check_google_auth.py
Uses: credentials.json (GA4), token.pickle / gbp-service-account-key.json / env (GBP).
Optional: gcloud auth application-default login (for ADC).
"""

import os
import sys
import subprocess

# Project root
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)


def run_cmd(cmd, capture=True):
    try:
        out = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            timeout=10,
            cwd=ROOT,
        )
        return out.returncode == 0, (out.stdout or "").strip(), (out.stderr or "").strip()
    except Exception as e:
        return False, "", str(e)


def check_gcloud():
    """Check if gcloud CLI is installed and default credentials."""
    ok, out, err = run_cmd("gcloud auth list 2>&1")
    if not ok and "not found" in (out + err).lower():
        return "gcloud not installed or not in PATH", None
    ok_adc, out_adc, _ = run_cmd("gcloud auth application-default print-access-token 2>&1")
    if ok_adc and out_adc:
        return "gcloud ADC: token present", out_adc[:20] + "..."
    return "gcloud ADC: not logged in (run: gcloud auth application-default login)", None


def check_ga4():
    """Check GA4: credentials load and optional quick API call (same logic as utils/ga4_utils)."""
    creds_path = os.path.join(ROOT, "credentials.json")
    if os.path.exists(creds_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(creds_path)
        source = "credentials.json"
    else:
        source = "Application Default Credentials (gcloud or GOOGLE_APPLICATION_CREDENTIALS)"
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
        client = BetaAnalyticsDataClient()
        # Quick run_report to verify access (property 368035934); may take a few seconds
        request = RunReportRequest(
            property="properties/368035934",
            dimensions=[],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="2025-01-01", end_date="2025-01-02")],
        )
        import threading
        result = [None]
        exc = [None]
        def run():
            try:
                result[0] = client.run_report(request=request)
            except Exception as e:
                exc[0] = e
        t = threading.Thread(target=run, daemon=True)
        t.start()
        t.join(timeout=12)
        if exc[0]:
            raise exc[0]
        if result[0] is not None:
            return True, f"GA4 OK (source: {source})"
        return False, f"GA4: report timed out (source: {source})"
    except ImportError as e:
        return False, f"GA4: missing dependency ({e})"
    except Exception as e:
        msg = str(e).split("\n")[0]
        return False, f"GA4: {msg} (source: {source})"


def check_gbp():
    """Check GBP using same logic as api/gbp (token.pickle, gbp key, or env)."""
    try:
        import api.gbp as gbp
    except ImportError:
        return False, "GBP: cannot import api.gbp (run from project root)"
    creds = gbp.get_creds()
    if not creds:
        return False, "GBP: no credentials (token.pickle, gbp-service-account-key.json, or GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64)"
    try:
        from googleapiclient.discovery import build
        account_service = build("mybusinessaccountmanagement", "v1", credentials=creds)
        accounts = account_service.accounts().list().execute()
        if accounts.get("accounts"):
            names = [a.get("accountName", a.get("name", "")) for a in accounts["accounts"][:3]]
            return True, f"GBP OK ({len(accounts['accounts'])} account(s), e.g. {names[0][:50]}...)"
        return False, "GBP: credentials valid but no accounts returned (check API access / quota)"
    except Exception as e:
        msg = str(e).split("\n")[0]
        return False, f"GBP: {msg}"


def main():
    print("=== Google Auth Check (Tenacious Stats) ===\n")
    # 1. gcloud CLI
    gcloud_status, token_preview = check_gcloud()
    print(f"[gcloud] {gcloud_status}")
    if token_preview:
        print(f"        token: {token_preview}")
    print()
    # 2. GA4
    ga4_ok, ga4_msg = check_ga4()
    print(f"[GA4]   {'OK' if ga4_ok else 'FAIL'} - {ga4_msg}")
    print()
    # 3. GBP
    gbp_ok, gbp_msg = check_gbp()
    print(f"[GBP]   {'OK' if gbp_ok else 'FAIL'} - {gbp_msg}")
    print()
    print("---")
    if ga4_ok and gbp_ok:
        print("All checks passed. Dashboard GA4 + GBP should work.")
    elif ga4_ok:
        print("GA4 ready. Fix GBP credentials for Business Profile section.")
    elif gbp_ok:
        print("GBP ready. Fix GA4 credentials (credentials.json or gcloud ADC) for analytics.")
    else:
        print("Fix GA4 and/or GBP credentials. See SETUP.md and GBP_README.md.")
    return 0 if (ga4_ok or gbp_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
