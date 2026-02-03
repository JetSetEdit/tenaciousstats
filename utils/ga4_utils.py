"""
Reusable GA4 data fetching utilities
Save this as utils/ga4_utils.py
"""

import os
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

# Configuration
PROPERTY_ID = '368035934'
_CREDENTIALS_NAME = 'credentials.json'
# Resolve path from project root (parent of utils/) so it works from api/ or CWD
_utils_dir = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(os.path.dirname(_utils_dir), _CREDENTIALS_NAME)


def setup_credentials():
    """Sets up GA4 authentication."""
    if os.path.exists(CREDENTIALS_FILE):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
        return "Service Account (credentials.json)"
    return "gcloud Application Default Credentials"

def get_ga4_client():
    """Returns authenticated GA4 client."""
    if os.path.exists(CREDENTIALS_FILE):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(CREDENTIALS_FILE)
    return BetaAnalyticsDataClient()

def fetch_ga4_data(start_date: str, end_date: str, dimensions: list, metrics: list, limit: int = 10000):
    """Fetches data from GA4 API and returns a Pandas DataFrame."""
    client = get_ga4_client()
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=dim) for dim in dimensions],
        metrics=[Metric(name=met) for met in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit
    )
    
    response = client.run_report(request=request)
    
    data = []
    for row in response.rows:
        item = {}
        for i, dim in enumerate(dimensions):
            item[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            item[met] = row.metric_values[i].value
        data.append(item)
    
    return pd.DataFrame(data)

def format_metric(value):
    """Formats large numbers for display."""
    try:
        val = float(value)
        if val >= 1_000_000:
            return f"{val/1_000_000:.1f}M"
        if val >= 1_000:
            return f"{val/1_000:.1f}K"
        return f"{val:,.0f}"
    except (ValueError, TypeError):
        return value


# Aliases expected by api/index.py (Vercel/run_vercel_local)
get_client = get_ga4_client


def fetch_analytics_data(start_date: str, end_date: str, dimensions: list, metrics: list, limit: int = 10000):
    """Returns list of dicts for API (same signature as fetch_ga4_data)."""
    df = fetch_ga4_data(start_date, end_date, dimensions, metrics, limit)
    return df.to_dict("records") if not df.empty else []










