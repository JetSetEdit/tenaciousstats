import os
from google.analytics.admin import AnalyticsAdminServiceClient

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def list_conversion_events():
    client = AnalyticsAdminServiceClient()
    parent = f"properties/{PROPERTY_ID}"
    
    print(f"Listing Conversion Events for Property {PROPERTY_ID}...")
    try:
        results = client.list_conversion_events(parent=parent)
        for event in results:
            print(f"- {event.event_name} (Custom: {event.custom}, Deletable: {event.deletable})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_conversion_events()
