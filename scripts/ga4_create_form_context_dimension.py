#!/usr/bin/env python3
"""
Create GA4 event-scoped custom dimension for the `form_context` event parameter.

This matches gtag on the site (generate_lead with form_context: contact | product_enquire)
and the Data API dimension `customEvent:form_context` used by the dashboard.

Credentials (same as utils/ga4_utils.py):
  - GOOGLE_APPLICATION_CREDENTIALS_B64, or
  - credentials.json in the project root

Prerequisites:
  - Google Analytics Admin API enabled for the GCP project tied to the service account.
  - Service account added to the GA4 property with at least Editor access.

Usage:
  python scripts/ga4_create_form_context_dimension.py
  set PROPERTY_ID=123456789 && python scripts/ga4_create_form_context_dimension.py
"""

from __future__ import annotations

import os
import sys

# Project root (parent of scripts/)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import CustomDimension
from google.api_core import exceptions as gexc

from utils.ga4_utils import PROPERTY_ID, setup_credentials

PARAM_NAME = "form_context"
DISPLAY_NAME = "Form context"
DESCRIPTION = "CF7 generate_lead: contact page vs product enquire."


def main() -> int:
    setup_credentials()
    parent = f"properties/{PROPERTY_ID}"
    client = AnalyticsAdminServiceClient()

    for dim in client.list_custom_dimensions(parent=parent):
        if getattr(dim, "parameter_name", None) == PARAM_NAME:
            print(f"OK: Custom dimension already exists for parameter '{PARAM_NAME}'.")
            print(f"    resource: {dim.name}")
            print(f"    display_name: {dim.display_name}")
            return 0

    cd = CustomDimension(
        parameter_name=PARAM_NAME,
        display_name=DISPLAY_NAME,
        description=DESCRIPTION[:150],
        scope=CustomDimension.DimensionScope.EVENT,
    )
    try:
        created = client.create_custom_dimension(parent=parent, custom_dimension=cd)
        print(f"Created event-scoped custom dimension for '{PARAM_NAME}'.")
        print(f"  resource: {created.name}")
        print(f"  Data API dimension: customEvent:{PARAM_NAME}")
        print("  Allow up to 24–48h for reporting; new hits register sooner.")
        return 0
    except gexc.AlreadyExists:
        print(f"Custom dimension for '{PARAM_NAME}' already exists (race or UI create).")
        return 0
    except gexc.PermissionDenied as e:
        print(
            "Permission denied. Add this service account to GA4: Admin > Property access management > Editor (or Admin).",
            file=sys.stderr,
        )
        print(e, file=sys.stderr)
        return 1
    except gexc.NotFound as e:
        print(f"Property not found or no access: {parent}", file=sys.stderr)
        print(e, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if "ADMIN_API" in str(e).upper() or "disabled" in str(e).lower():
            print("Enable 'Google Analytics Admin API' in Google Cloud Console for this project.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
