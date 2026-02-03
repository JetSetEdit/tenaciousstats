from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

# Configuration
PROPERTY_ID = '368035934'

# Set credentials - check multiple possible locations
CREDENTIALS_PATHS = [
    'credentials.json',  # Current directory
    '../credentials.json',  # Parent directory (when running from api/)
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json'),  # Project root
]

CREDENTIALS_FILE = None
for path in CREDENTIALS_PATHS:
    if os.path.exists(path):
        CREDENTIALS_FILE = os.path.abspath(path)
        break

if CREDENTIALS_FILE:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
    print(f"Using credentials from: {CREDENTIALS_FILE}")
else:
    print("Warning: credentials.json not found. Trying gcloud application-default credentials...")

app = FastAPI(title="Tenacious Stats API", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AnalyticsRequest(BaseModel):
    start_date: str
    end_date: str
    dimensions: List[str] = []
    metrics: List[str]
    limit: int = 10000

class AnalyticsResponse(BaseModel):
    success: bool
    data: List[dict]
    row_count: int

# Helper Functions
def get_client():
    """Returns authenticated GA4 client."""
    try:
        # Try to create client - it will use GOOGLE_APPLICATION_CREDENTIALS if set
        # or fall back to gcloud application-default credentials
        client = BetaAnalyticsDataClient()
        return client
    except Exception as e:
        error_msg = str(e)
        # Provide helpful error message
        if "insufficient authentication scopes" in error_msg.lower() or "access_token_scope_insufficient" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="Authentication error: Service account needs 'Analytics Viewer' role. "
                       "Please add the service account email to Google Analytics property access. "
                       f"Service account: antigravity@tenacious-tapes-videos.iam.gserviceaccount.com"
            )
        raise HTTPException(status_code=500, detail=f"Authentication failed: {error_msg}")

def fetch_analytics_data(start_date: str, end_date: str, dimensions: List[str], metrics: List[str], limit: int = 10000):
    """Fetches data from GA4 API."""
    try:
        client = get_client()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
    
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=dim) for dim in dimensions],
        metrics=[Metric(name=met) for met in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit
    )
    
    try:
        response = client.run_report(request=request)
    except Exception as e:
        error_msg = str(e)
        # Check for common authentication errors
        if "insufficient authentication scopes" in error_msg or "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in error_msg:
            raise HTTPException(
                status_code=403, 
                detail="Authentication error: Service account needs 'Analytics Viewer' role in Google Cloud Console. Please check credentials.json permissions."
            )
        elif "PERMISSION_DENIED" in error_msg:
            raise HTTPException(
                status_code=403,
                detail="Permission denied: Service account needs access to GA4 property. Please grant access in Google Analytics."
            )
        else:
            raise HTTPException(status_code=500, detail=f"API Error: {error_msg}")
    
    data = []
    for row in response.rows:
        item = {}
        for i, dim in enumerate(dimensions):
            item[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            item[met] = row.metric_values[i].value
        data.append(item)
    
    return data

# API Endpoints
@app.get("/")
def root():
    return {"message": "Tenacious Stats API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        client = get_client()
        return {"status": "healthy", "property_id": PROPERTY_ID}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/analytics/data", response_model=AnalyticsResponse)
def get_analytics_data(request: AnalyticsRequest):
    """
    Fetch analytics data from GA4.
    
    Example request:
    {
        "start_date": "2025-12-01",
        "end_date": "2025-12-10",
        "dimensions": ["sessionSourceMedium"],
        "metrics": ["sessions"],
        "limit": 1000
    }
    """
    try:
        data = fetch_analytics_data(
            request.start_date,
            request.end_date,
            request.dimensions,
            request.metrics,
            request.limit
        )
        return AnalyticsResponse(
            success=True,
            data=data,
            row_count=len(data)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

# Convenience endpoints for common queries
@app.get("/analytics/overview")
def get_overview(start_date: str, end_date: str):
    """Get overview metrics."""
    dimensions = []
    metrics = ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
    return {"success": True, "data": data[0] if data else {}}

@app.get("/analytics/sources")
def get_sources(start_date: str, end_date: str, limit: int = 10):
    """Get traffic sources."""
    dimensions = ['sessionSourceMedium']
    metrics = ['sessions']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
    return {"success": True, "data": data}

@app.get("/analytics/pages")
def get_pages(start_date: str, end_date: str, limit: int = 15):
    """Get top pages."""
    dimensions = ['pagePath', 'pageTitle']
    metrics = ['screenPageViews', 'activeUsers']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
    return {"success": True, "data": data}

@app.get("/analytics/retention")
def get_retention(start_date: str, end_date: str):
    """Get user retention data."""
    dimensions = ['newVsReturning']
    metrics = ['sessions']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
    return {"success": True, "data": data}

@app.get("/analytics/cities")
def get_cities(start_date: str, end_date: str, limit: int = 10):
    """Get top cities."""
    dimensions = ['city']
    metrics = ['sessions']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
    return {"success": True, "data": data}

@app.get("/analytics/countries")
def get_countries(start_date: str, end_date: str):
    """Get countries data."""
    dimensions = ['country']
    metrics = ['sessions']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
    return {"success": True, "data": data}

@app.get("/analytics/devices")
def get_devices(start_date: str, end_date: str):
    """Get device categories."""
    dimensions = ['deviceCategory']
    metrics = ['sessions']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
    return {"success": True, "data": data}

@app.get("/analytics/events")
def get_events(start_date: str, end_date: str, limit: int = 20):
    """Get top events."""
    dimensions = ['eventName']
    metrics = ['eventCount']
    data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
    return {"success": True, "data": data}


# --- GBP Integration ---
import gbp

@app.get("/gbp/insights")
def get_gbp_insights(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get Google Business Profile Insights."""
    result = gbp.get_insights(start_date, end_date)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/gbp/reviews")
def get_gbp_reviews():
    """Get Google Business Profile Reviews."""
    result = gbp.get_reviews()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


