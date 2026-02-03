from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Metric, Dimension, DateRange, OrderBy
import os
import pandas as pd

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def check_post_launch():
    client = BetaAnalyticsDataClient()
    
    # Date Range: Yesterday and Today
    start_date = '2025-12-10'
    end_date = '2025-12-11'
    
    print(f"Checking GA4 Data for {start_date} to {end_date}...\n")
    
    # 1. Daily Overview
    request_daily = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="sessions"), Metric(name="totalUsers"), Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
    )
    response_daily = client.run_report(request=request_daily)
    
    print("--- Daily Traffic ---")
    if not response_daily.rows:
        print("No data found.")
    else:
        for row in response_daily.rows:
            date = row.dimension_values[0].value
            sessions = row.metric_values[0].value
            users = row.metric_values[1].value
            views = row.metric_values[2].value
            print(f"Date: {date} | Sessions: {sessions} | Users: {users} | Pageviews: {views}")

    # 2. Top Events
    request_events = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)]
    )
    response_events = client.run_report(request=request_events)
    
    print("\n--- Top Events Captured ---")
    if not response_events.rows:
        print("No events found.")
    else:
        for row in response_events.rows:
            event = row.dimension_values[0].value
            count = row.metric_values[0].value
            print(f"{event}: {count}")

if __name__ == "__main__":
    check_post_launch()
