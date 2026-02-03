from google.analytics.admin import AnalyticsAdminServiceClient
import os

# CONFIGURATION
# Checking the NEW Property ID provided by user
PROPERTY_ID = '404184799'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def verify_stream_id():
    client = AnalyticsAdminServiceClient()
    
    print(f"Querying Admin API for Property: {PROPERTY_ID}...\n")
    
    try:
        # List Data Streams
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
            
    except Exception as e:
        print(f"Error: {e}")
        print("NOTE: This likely means the Service Account does not have permission to access this Property ID.")

if __name__ == "__main__":
    verify_stream_id()
