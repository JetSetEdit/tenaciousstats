"""
Reusable GA4 data fetching utilities
Save this as utils/ga4_utils.py
"""

import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
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


def fetch_ga4_data(start_date: str, end_date: str, dimensions: list, metrics: list, limit: int = 10000, compare_start_date: str = None, compare_end_date: str = None):
    """Fetches data from GA4 API and returns a list of dicts (no pandas needed)."""
    client = get_ga4_client()
    
    date_ranges = [DateRange(start_date=start_date, end_date=end_date)]
    if compare_start_date and compare_end_date:
        date_ranges.append(DateRange(start_date=compare_start_date, end_date=compare_end_date))

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=dim) for dim in dimensions],
        metrics=[Metric(name=met) for met in metrics],
        date_ranges=date_ranges,
        limit=limit
    )
    
    response = client.run_report(request=request)
    
    is_compare = len(date_ranges) > 1
    num_metrics = len(metrics)
    num_dimensions = len(dimensions)

    # GA4 often appends a 'date_range' dimension if multiple ranges are requested
    # Let's check if the last dimension value in the first row looks like 'date_range_X'
    has_auto_date_dim = False
    actual_num_dims = len(response.dimension_headers)
    if is_compare and actual_num_dims > num_dimensions:
        has_auto_date_dim = True

    # Dictionary to group rows by dimension values
    # Key: tuple of dimension values, Value: dict of metrics
    grouped_data = {}

    for row in response.rows:
        # Extract dimension values (excluding the auto-added date_range if present)
        row_dims = tuple(row.dimension_values[i].value for i in range(num_dimensions))
        
        # Determine if this row is for the current period or comparison period
        is_current = True
        if has_auto_date_dim:
            date_range_val = row.dimension_values[actual_num_dims - 1].value
            is_current = (date_range_val == 'date_range_0')
        elif num_dimensions == 0:
            is_current = (len(grouped_data) == 0 or row_dims not in grouped_data or "_is_done" not in grouped_data[row_dims])

        if row_dims not in grouped_data:
            grouped_data[row_dims] = {}
            for i, dim in enumerate(dimensions):
                grouped_data[row_dims][dim] = row.dimension_values[i].value

        if is_current:
            for i, met in enumerate(metrics):
                grouped_data[row_dims][met] = row.metric_values[i].value
            if num_dimensions == 0: grouped_data[row_dims]["_is_done"] = True
        else:
            for i, met in enumerate(metrics):
                grouped_data[row_dims][f"{met}_compare"] = row.metric_values[i].value

    return list(grouped_data.values())


def fetch_path_screen_page_views_total(
    start_date: str,
    end_date: str,
    path_value: str,
    match_type: str = "contains",
) -> int:
    """
    Total screenPageViews for pagePath filtered by path_value.

    match_type:
      - "contains": substring match, case-insensitive (good for slugs like oar-f701)
      - "exact": EXACT match on pagePath as stored in GA4 (use e.g. /on-a-roll/ including slashes)
    """
    path_value = (path_value or "").strip()
    if not path_value:
        return 0

    if match_type == "exact":
        mt = Filter.StringFilter.MatchType.EXACT
        case_sensitive = False
    else:
        mt = Filter.StringFilter.MatchType.CONTAINS
        case_sensitive = False

    client = get_ga4_client()
    dim_filter = FilterExpression(
        filter=Filter(
            field_name="pagePath",
            string_filter=Filter.StringFilter(
                match_type=mt,
                value=path_value,
                case_sensitive=case_sensitive,
            ),
        )
    )
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=dim_filter,
        limit=1,
    )
    response = client.run_report(request=request)
    if not response.rows:
        return 0
    try:
        return int(float(response.rows[0].metric_values[0].value))
    except (ValueError, TypeError, IndexError, AttributeError):
        return 0


def fetch_blog_screen_page_views_total(
    start_date: str, end_date: str, path_contains: str = "blog"
) -> int:
    """Blog / editorial URLs: path contains substring (case-insensitive)."""
    return fetch_path_screen_page_views_total(
        start_date, end_date, path_contains, match_type="contains"
    )


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


def fetch_analytics_data(start_date: str, end_date: str, dimensions: list, metrics: list, limit: int = 10000, compare_start_date: str = None, compare_end_date: str = None):
    """Returns list of dicts for API (same signature as fetch_ga4_data)."""
    return fetch_ga4_data(start_date, end_date, dimensions, metrics, limit, compare_start_date, compare_end_date)
