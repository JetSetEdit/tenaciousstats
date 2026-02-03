from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, Metric, Dimension, DateRange, FilterExpression, Filter
import os

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def check_nan_search():
    client = BetaAnalyticsDataClient()
    
    print("Checking for 'nan' search terms (Dec 10 - Dec 11)...")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="searchTerm")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date="2025-12-10", end_date="2025-12-11")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="view_search_results")
            )
        )
    )
    
    response = client.run_report(request=request)
    
    found_nan = False
    if not response.rows:
        print("No search results found at all.")
    else:
        for row in response.rows:
            term = row.dimension_values[0].value
            count = row.metric_values[0].value
            print(f"Term: '{term}' - Count: {count}")
            if "nan" in term.lower():
                found_nan = True

    if found_nan:
        print("\nALERT: 'nan' bug is STILL ACTIVE.")
    else:
        print("\nGood News: No 'nan' searches found in the last 24 hours.")

if __name__ == "__main__":
    check_nan_search()
