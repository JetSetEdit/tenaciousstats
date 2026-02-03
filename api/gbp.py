import os
import datetime
import json
import base64
import pickle
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for GBP
SCOPES = [
    "https://www.googleapis.com/auth/business.manage"
]

# Credentials handling
CREDENTIALS_FILE = 'gbp-service-account-key.json'
TOKEN_PICKLE = 'token.pickle'

def get_creds():
    """Gets credentials from pickle (OAuth) or service account file."""
    # 1. Try OAuth 2.0 Token (Preferred)
    # A. Check environment variable (for Vercel)
    oauth_token_b64 = os.environ.get('GOOGLE_OAUTH_TOKEN_B64')
    if oauth_token_b64:
        try:
            token_bytes = base64.b64decode(oauth_token_b64)
            creds = pickle.loads(token_bytes)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                # Note: We can't save back to env var in Vercel, but we have a valid access token now
                return creds
        except Exception as e:
            print(f"Error loading OAuth token from env var: {e}")

    # B. Check local file (for localhost)
    if os.path.exists(TOKEN_PICKLE):
        try:
            with open(TOKEN_PICKLE, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_PICKLE, 'wb') as token:
                    pickle.dump(creds, token)
                return creds
        except Exception as e:
            print(f"Error loading pickle token: {e}")

    # 2. Try environment variable (Service Account)
    gbp_creds_b64 = os.environ.get('GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64')
    if gbp_creds_b64:
        try:
            creds_json = base64.b64decode(gbp_creds_b64).decode('utf-8')
            creds_dict = json.loads(creds_json)
            return service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
        except Exception as e:
            print(f"Error loading credentials from env var: {e}")
    
    # 3. Fall back to file-based credentials (Service Account)
    final_creds_file = CREDENTIALS_FILE
    if not os.path.exists(final_creds_file):
         root_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), CREDENTIALS_FILE)
         if os.path.exists(root_path):
             final_creds_file = root_path

    if os.path.exists(final_creds_file):
        return service_account.Credentials.from_service_account_file(
            final_creds_file, scopes=SCOPES
        )
    
    return None

def get_account_id(service):
    """Fetches the first account ID associated with the service account."""
    try:
        accounts = service.accounts().list().execute()
        if 'accounts' in accounts:
            return accounts['accounts'][0]['name']
    except Exception as e:
        print(f"Error fetching accounts: {e}")
    return None

def get_location_id(service, account_name):
    """Fetches the first location ID for the account."""
    try:
        locations = service.accounts().locations().list(parent=account_name).execute()
        if 'locations' in locations:
            return locations['locations'][0]['name']
    except Exception as e:
        print(f"Error fetching locations: {e}")
    return None

def get_insights(start_date=None, end_date=None):
    """
    Fetches daily metrics for the location using fetchMultiDailyMetricsTimeSeries.
    """
    creds = get_creds()
    if not creds:
        return {"error": "Credentials not found"}

    try:
        # 1. Get Account (Account Management API)
        account_service = build('mybusinessaccountmanagement', 'v1', credentials=creds)
        accounts = account_service.accounts().list().execute()
        if not accounts.get('accounts'):
            return {"error": "No accounts found (or API not enabled/quota exceeded)"}
        account_name = accounts['accounts'][0]['name']
        
        # 2. Get Location (Business Information API)
        info_service = build('mybusinessbusinessinformation', 'v1', credentials=creds)
        locations = info_service.accounts().locations().list(parent=account_name).execute()
        if not locations.get('locations'):
            return {"error": "No locations found"}
        location_name = locations['locations'][0]['name'] # Format: locations/{locationId}
        
        # 3. Fetch Daily Metrics (Performance API)
        perf_service = build('businessprofileperformance', 'v1', credentials=creds)
        
        # Metrics to fetch
        metrics = [
            "BUSINESS_IMPRESSIONS_DESKTOP_MAPS",
            "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
            "BUSINESS_IMPRESSIONS_MOBILE_MAPS",
            "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
            "BUSINESS_CONVERSATIONS",
            "BUSINESS_DIRECTION_REQUESTS",
            "CALL_CLICKS",
            "WEBSITE_CLICKS",
            "BUSINESS_BOOKINGS",
            "BUSINESS_FOOD_ORDERS",
            "BUSINESS_FOOD_MENU_CLICKS"
        ]
        
        # Default to last 30 days if not specified
        if not start_date or not end_date:
            today = datetime.date.today()
            end_date_obj = today
            start_date_obj = today - datetime.timedelta(days=30)
        else:
            try:
                start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                 # Fallback
                today = datetime.date.today()
                end_date_obj = today
                start_date_obj = today - datetime.timedelta(days=30)

        # Use fetchMultiDailyMetricsTimeSeries
        response = perf_service.locations().fetchMultiDailyMetricsTimeSeries(
            location=location_name, 
            dailyMetrics=metrics, 
            dailyRange={
                "start_date": {
                    "year": start_date_obj.year,
                    "month": start_date_obj.month,
                    "day": start_date_obj.day
                },
                "end_date": {
                    "year": end_date_obj.year,
                    "month": end_date_obj.month,
                    "day": end_date_obj.day
                }
            }
        ).execute()
        
        return {
            "success": True, 
            "data": response.get('multiDailyMetricTimeSeries', []),
            "location": location_name
        }

    except HttpError as e:
        error_content = e.content.decode('utf-8')
        if "quota" in error_content.lower() or "rate_limit_exceeded" in error_content.lower():
            return {
                "error": "Quota Exceeded. Please request GBP API access in Google Cloud Console.",
                "details": error_content
            }
        return {"error": f"API Error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}"}

def get_reviews():
    """Fetches recent reviews."""
    creds = get_creds()
    if not creds:
        return {"error": "Credentials not found"}

    try:
        # 1. Get Account (Account Management API)
        account_service = build('mybusinessaccountmanagement', 'v1', credentials=creds)
        accounts = account_service.accounts().list().execute()
        if not accounts.get('accounts'):
            return {"error": "No accounts found"}
        account_name = accounts['accounts'][0]['name']
        
        # 2. Get Location (Business Information API)
        info_service = build('mybusinessbusinessinformation', 'v1', credentials=creds)
        locations = info_service.accounts().locations().list(parent=account_name).execute()
        if not locations.get('locations'):
            return {"error": "No locations found"}
        location_name = locations['locations'][0]['name']
        
        # 3. Fetch Reviews (Reviews API)
        # Parent format: accounts/{accountId}/locations/{locationId}
        full_location_name = f"{account_name}/{location_name}"
        
        reviews_service = build('mybusinessreviews', 'v1', credentials=creds)
        reviews = reviews_service.accounts().locations().reviews().list(parent=full_location_name).execute()
        
        return {
            "success": True,
            "reviews": reviews.get('reviews', []),
            "averageRating": reviews.get('averageRating', 0),
            "totalReviewCount": reviews.get('totalReviewCount', 0)
        }

    except HttpError as e:
        return {"error": f"API Error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected Error: {e}"}
