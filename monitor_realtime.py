import time
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunRealtimeReportRequest, Metric, Dimension
import os

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def monitor_realtime():
    client = BetaAnalyticsDataClient()
    print("Starting 5-Minute Realtime Monitor...")
    print("Please browse the site on your phone now.")
    
    for i in range(10):  # 10 checks * 30 seconds = 5 minutes
        print(f"Check {i+1}/10...", end=" ")
        
        try:
            request = RunRealtimeReportRequest(
                property=f"properties/{PROPERTY_ID}",
                metrics=[Metric(name="activeUsers")]
            )
            response = client.run_realtime_report(request=request)
            
            users = 0
            if response.rows:
                users = int(response.rows[0].metric_values[0].value)
            
            if users > 0:
                print(f"\nSUCCESS! Found {users} active user(s)!")
                return
            else:
                print("0 users.")
                
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(30)
        
    print("\nMonitor finished. No users detected (API delay or filtering still active).")

if __name__ == "__main__":
    monitor_realtime()
