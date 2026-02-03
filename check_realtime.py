from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric, Dimension
import os

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def run_realtime_check():
    client = BetaAnalyticsDataClient()
    
    print("Querying GA4 Realtime API...")
    
    request = RunRealtimeReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="country")],
        metrics=[Metric(name="activeUsers")]
    )
    
    response = client.run_realtime_report(request=request)
    
    print(f"Realtime Report Result:")
    total_users = 0
    
    if not response.rows:
        print("No active users found in the last 30 minutes (API might have a slight delay or we are blocked).")
    else:
        for row in response.rows:
            country = row.dimension_values[0].value
            users = row.metric_values[0].value
            print(f"- Country: {country}, Active Users: {users}")
            total_users += int(users)
            
    print(f"\nTotal Active Users Right Now: {total_users}")

if __name__ == "__main__":
    run_realtime_check()
