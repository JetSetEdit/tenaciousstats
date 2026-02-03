import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import pandas as pd

PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def main():
    client = BetaAnalyticsDataClient()
    
    print("Fetching Top Events...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name='eventName')],
        metrics=[Metric(name='eventCount')],
        date_ranges=[DateRange(start_date='30daysAgo', end_date='today')],
        limit=20
    )
    
    response = client.run_report(request=request)

    print(f"{'Event Name':<30} | {'Count':<10}")
    print("-" * 45)
    for row in response.rows:
        print(f"{row.dimension_values[0].value:<30} | {row.metric_values[0].value:<10}")

if __name__ == '__main__':
    main()
