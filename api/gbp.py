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

# Credentials handling (resolve from project root so server finds them)
_api_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_api_dir)
CREDENTIALS_FILE = 'gbp-service-account-key.json'
TOKEN_PICKLE = 'token.pickle'
TOKEN_PICKLE_PATH = os.path.join(_project_root, TOKEN_PICKLE)

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

    # B. Check local file (for localhost) - try project root first
    for pickle_path in [TOKEN_PICKLE_PATH, TOKEN_PICKLE]:
        if os.path.exists(pickle_path):
            try:
                with open(pickle_path, 'rb') as token:
                    creds = pickle.load(token)
                if creds and creds.valid:
                    return creds
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    with open(pickle_path, 'wb') as token:
                        pickle.dump(creds, token)
                    return creds
            except Exception as e:
                print(f"Error loading pickle token from {pickle_path}: {e}")

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


def _aggregate_insights_timeseries(series_list):
    """
    Sum multiDailyMetricTimeSeries into a simple summary for the dashboard.
    Returns { views: { search, maps }, customerActions: { websiteClicks, directionRequests } }.
    """
    summary = {
        "views": {"search": 0, "maps": 0},
        "customerActions": {"websiteClicks": 0, "directionRequests": 0}
    }
    if not series_list:
        return summary
    if not series_list:
        return summary
    
    for item in series_list:
        # Each item corresponds to a location and contains a list of metrics
        metrics_list = item.get("dailyMetricTimeSeries", [])
        for series in metrics_list:
            metric = series.get("dailyMetric") or ""
            total = 0
            for pt in series.get("timeSeries", {}).get("datedValues", []):
                total += int(pt.get("value", 0))
            
            if "SEARCH" in metric:
                summary["views"]["search"] += total
            elif "MAPS" in metric:
                summary["views"]["maps"] += total
            elif metric == "WEBSITE_CLICKS":
                summary["customerActions"]["websiteClicks"] += total
            elif metric == "BUSINESS_DIRECTION_REQUESTS":
                summary["customerActions"]["directionRequests"] += total
    return summary


def get_insights(start_date=None, end_date=None):
    """
    Fetches daily metrics using AuthorizedSession to avoid client library issues with dailyRange.
    """
    from google.auth.transport.requests import AuthorizedSession
    
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
        
        # 2. Get Location (Business Information API) – read_mask is required
        info_service = build('mybusinessbusinessinformation', 'v1', credentials=creds)
        locations = info_service.accounts().locations().list(
            parent=account_name,
            readMask="name",
            pageSize=100
        ).execute()
        locs = locations.get('locations') or []
        if not locs:
            return {
                "error": "No locations found. The Google account has no Business Profile locations. "
                "Use OAuth (token.pickle) from the account that owns the business, claim a business at business.google.com, "
                "or invite this account as a manager. See GBP_README.md."
            }
        location_name = locs[0]['name']  # Format: locations/{locationId}
        
        # 3. Fetch Daily Metrics (Performance API) via AuthorizedSession
        # The client library has issues with the dailyRange object in some versions,
        # so we standardise on a direct HTTP call with flattened parameters.
        
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

        # Prepare manual request
        authed_session = AuthorizedSession(creds)
        url = f"https://businessprofileperformance.googleapis.com/v1/{location_name}:fetchMultiDailyMetricsTimeSeries"
        
        params = {
            "dailyMetrics": metrics,
            "dailyRange.startDate.year": start_date_obj.year,
            "dailyRange.startDate.month": start_date_obj.month,
            "dailyRange.startDate.day": start_date_obj.day,
            "dailyRange.endDate.year": end_date_obj.year,
            "dailyRange.endDate.month": end_date_obj.month,
            "dailyRange.endDate.day": end_date_obj.day
        }
        
        response = authed_session.get(url, params=params)
        
        if response.status_code != 200:
             # Try to parse error
            try:
                err_json = response.json()
                msg = err_json.get("error", {}).get("message", response.text)
            except:
                msg = response.text
            return {"error": f"API Error ({response.status_code}): {msg}"}

        data = response.json()
        series_list = data.get('multiDailyMetricTimeSeries', [])
        summary = _aggregate_insights_timeseries(series_list)
        return {
            "success": True,
            "data": series_list,
            "summary": summary,
            "location": location_name
        }

    except Exception as e:
        return {"error": f"Unexpected Error: {str(e)}"}


def get_ratings():
    """
    Returns ratings summary for the dashboard: averageRating, totalReviews, ratingDistribution.
    Derived from get_reviews().
    """
    result = get_reviews()
    if "error" in result:
        return result
    reviews = result.get("reviews", [])
    total = result.get("totalReviewCount", 0)
    avg = result.get("averageRating", 0)
    dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for r in reviews:
        star = r.get("starRating") or r.get("rating")
        if star is not None:
            key = str(int(star))
            if key in dist:
                dist[key] += 1
    return {
        "success": True,
        "data": {
            "averageRating": float(avg),
            "totalReviews": int(total),
            "ratingDistribution": dist
        }
    }


def get_reviews():
    """Fetches recent reviews using AuthorizedSession v4 endpoint."""
    from google.auth.transport.requests import AuthorizedSession
    creds = get_creds()
    if not creds:
        return {"error": "Credentials not found"}

    try:
        # 1. Get Account
        account_service = build('mybusinessaccountmanagement', 'v1', credentials=creds)
        accounts = account_service.accounts().list().execute()
        if not accounts.get('accounts'):
            return {"error": "No accounts found"}
        account_name = accounts['accounts'][0]['name']
        
        # 2. Get Location
        info_service = build('mybusinessbusinessinformation', 'v1', credentials=creds)
        locations = info_service.accounts().locations().list(
            parent=account_name,
            readMask="name",
            pageSize=100
        ).execute()
        locs = locations.get('locations') or []
        if not locs:
            return {
                "error": "No locations found. See GBP_README.md."
            }
        location_name = locs[0]['name']
        
        # 3. Fetch Reviews (v4 API) via AuthorizedSession
        # Format: accounts/{accountId}/locations/{locationId}
        
        if 'accounts/' in location_name:
             full_location_name = location_name
        else:
             full_location_name = f"{account_name}/{location_name}"

        authed_session = AuthorizedSession(creds)
        url = f"https://mybusiness.googleapis.com/v4/{full_location_name}/reviews"
        
        response = authed_session.get(url)
        
        if response.status_code == 403:
            # User opted not to enable the API for now. 
            # Return empty list to keep dashboard clean instead of showing an error.
            print("GBP Reviews API (v4) not enabled. returning empty list.")
            return {
                "success": True,
                "reviews": [],
                "data": [],
                "averageRating": 0,
                "totalReviewCount": 0
            }
            
        if response.status_code != 200:
             # Try to parse error
            try:
                err_json = response.json()
                msg = err_json.get("error", {}).get("message", response.text)
            except:
                msg = response.text
            return {"error": f"API Error ({response.status_code}): {msg}"}

        data = response.json()
        reviews_list = data.get('reviews', [])
        return {
            "success": True,
            "reviews": reviews_list,
            "data": reviews_list,
            "averageRating": data.get('averageRating', 0),
            "totalReviewCount": data.get('totalReviewCount', 0)
        }

    except Exception as e:
        return {"error": f"Unexpected Error: {str(e)}"}
