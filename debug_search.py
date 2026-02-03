import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    Filter
)
import pandas as pd

PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def main():
    client = BetaAnalyticsDataClient()
    
    print("Checking 'pagePathPlusQueryString' for search-related paths...")
    
    # Filter for paths containing 'search'
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name='pagePathPlusQueryString')],
        metrics=[Metric(name='screenPageViews')],
        date_ranges=[DateRange(start_date='2024-01-01', end_date='today')],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    value="search",
                    match_type=Filter.StringFilter.MatchType.CONTAINS
                )
            )
        ),
        limit=50
    )
    
    response = client.run_report(request=request)

    print(f"Found {len(response.rows)} rows.")
    for row in response.rows:
        print(f"Path: {row.dimension_values[0].value} | Views: {row.metric_values[0].value}")

if __name__ == '__main__':
    main()
