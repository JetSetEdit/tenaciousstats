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

PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def main():
    client = BetaAnalyticsDataClient()
    
    print("Checking for specific custom events (Last 30 Days)...")
    
    # List of custom events we are interested in
    custom_events = [
        'generate_lead',
        'file_download',
        'click_phone', 
        'click_email',
        'click_buy_online'
    ]
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name='eventName')],
        metrics=[Metric(name='eventCount')],
        date_ranges=[DateRange(start_date='30daysAgo', end_date='today')],
        # We can filter or just fetch all and filter in python if the list is short. 
        # Let's fetch top 100 events to be safe.
        limit=100
    )
    
    try:
        response = client.run_report(request=request)
        
        found_events = {}
        for row in response.rows:
            event_name = row.dimension_values[0].value
            count = row.metric_values[0].value
            if event_name in custom_events:
                found_events[event_name] = count
                
        print(f"\nResults:")
        print(f"{'Event Name':<20} | {'Count':<10}")
        print("-" * 35)
        
        has_data = False
        for event in custom_events:
            count = found_events.get(event, '0')
            if int(count) > 0:
                has_data = True
            print(f"{event:<20} | {count:<10}")
            
        if has_data:
            print("\nSUCCESS: We are seeing data for at least some custom events.")
        else:
            print("\nWARNING: No data found for these specific custom events in the last 30 days.")
            
    except Exception as e:
        print(f"Error fetching report: {e}")

if __name__ == '__main__':
    main()
