import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy
)
import pandas as pd

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
START_DATE = '2025-12-01' 
END_DATE = 'today'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def run_report(client, dimensions, metrics, row_limit=10000):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=dim) for dim in dimensions],
        metrics=[Metric(name=met) for met in metrics],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        limit=row_limit
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

def main():
    try:
        client = BetaAnalyticsDataClient()
        print("Authenticated successfully.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # 1. Traffic Overview (Month)
    print("Fetching Traffic Overview...")
    df_traffic = run_report(client, ['yearMonth'], ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate'])
    df_traffic.to_csv('traffic_overview.csv', index=False)

    # 2. Traffic Sources
    print("Fetching Traffic Sources...")
    df_sources = run_report(client, ['sessionSourceMedium'], ['sessions'])
    df_sources.to_csv('traffic_sources.csv', index=False)

    # 3. Top Pages
    print("Fetching Top Pages...")
    df_pages = run_report(client, ['pagePath', 'pageTitle'], ['screenPageViews', 'activeUsers'])
    df_pages.to_csv('top_pages.csv', index=False)

    # 4. Demographics (Country)
    print("Fetching Demographics...")
    df_geo = run_report(client, ['country'], ['sessions'])
    df_geo.to_csv('demographics.csv', index=False)
    
    # 5. Tech (Device)
    print("Fetching Device Tech...")
    df_device = run_report(client, ['deviceCategory'], ['sessions'])
    df_device.to_csv('device_tech.csv', index=False)

    # 6. Site Search
    print("Fetching Site Search...")
    try:
        df_search = run_report(client, ['searchTerm'], ['screenPageViews'])
        df_search.to_csv('site_search.csv', index=False)
    except Exception as e:
        print(f"Could not fetch site search (might not be enabled): {e}")

    # 7. Retention (New vs Returning)
    print("Fetching Retention...")
    df_retention = run_report(client, ['newVsReturning'], ['sessions'])
    df_retention.to_csv('retention.csv', index=False)

    # 8. Cities
    print("Fetching Cities...")
    df_cities = run_report(client, ['city'], ['sessions'])
    df_cities.to_csv('cities.csv', index=False)

    # 9. Top Events (for Leads)
    print("Fetching Events...")
    df_events = run_report(client, ['eventName'], ['eventCount'])
    df_events.to_csv('top_events.csv', index=False)

    print("Data fetching complete. CSV files saved.")

if __name__ == '__main__':
    main()
