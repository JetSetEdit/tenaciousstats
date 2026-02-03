from google.analytics.admin import AnalyticsAdminServiceClient
import os

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def verify_stream_id():
    client = AnalyticsAdminServiceClient()
    
    print(f"Querying Admin API for Property: {PROPERTY_ID}...\n")
    
    # List Data Streams
    # The parent resource format is "properties/[YOUR_PROPERTY_ID]"
    request = client.list_data_streams(parent=f"properties/{PROPERTY_ID}")
    
    found = False
    for stream in request:
        print(f"Stream Name: {stream.display_name}")
        print(f"Stream Type: {stream.type_.name}")
        
        if stream.web_stream_data:
            print(f"Measurement ID: {stream.web_stream_data.measurement_id}")
            print(f"Stream ID: {stream.name}")
            found = True
            
    if not found:
        print("No Web Data Streams found for this property.")

if __name__ == "__main__":
    verify_stream_id()
