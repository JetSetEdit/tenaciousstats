"""
Reusable GA4 data fetching utilities
Save this as utils/ga4_utils.py
"""

import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

# Configuration
PROPERTY_ID = os.environ.get('PROPERTY_ID', '368035934')
_CREDENTIALS_NAME = 'credentials.json'
# Resolve path from project root (parent of utils/) so it works from api/ or CWD
_utils_dir = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(os.path.dirname(_utils_dir), _CREDENTIALS_NAME)


def setup_credentials():
    """Sets up GA4 authentication."""
    # 1. Check for Base64 Env Var (Vercel Production)
    b64_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_B64')
    if b64_creds:
        try:
            import base64
            import tempfile
            
            # Decode to JSON
            creds_json = base64.b64decode(b64_creds).decode('utf-8')
            
            # Write to temp file because Python GA4 library expects a file path env var
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                f.write(creds_json)
                temp_path = f.name
                
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_path
            return "Service Account (Env Var)"
        except Exception as e:
            print(f"Error decoding GA4 credentials from env: {e}")

    # 2. Check for local file
    if os.path.exists(CREDENTIALS_FILE):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
        return "Service Account (credentials.json)"
        
    return "gcloud Application Default Credentials"


def get_ga4_client():
    """Returns authenticated GA4 client."""
    # Ensure credentials are set up (File or Env Var)
    setup_credentials()
    return BetaAnalyticsDataClient()


def fetch_ga4_data(start_date: str, end_date: str, dimensions: list, metrics: list, limit: int = 10000):
    """Fetches data from GA4 API and returns a list of dicts (no pandas needed)."""
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
    
    return data


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
    return fetch_ga4_data(start_date, end_date, dimensions, metrics, limit)
