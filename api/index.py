"""
Vercel Serverless Function - Main API Handler
Handles both GA4 Analytics and Google Business Profile requests
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import GA4 utilities
ga4_error = None
try:
    from utils.ga4_utils import get_client, fetch_analytics_data
    GA4_AVAILABLE = True
except ImportError as e:
    GA4_AVAILABLE = False
    ga4_error = str(e)
    print(f"Warning: GA4 utils not available: {e}")

# Import GBP module (from same directory)
try:
    # Try relative import first
    try:
        from . import gbp
    except ImportError:
        # Fall back to absolute import
        import gbp
    GBP_AVAILABLE = True
except ImportError as e:
    GBP_AVAILABLE = False
    print(f"Warning: GBP module not available: {e}")

# FastAPI app
app = FastAPI(title="Tenacious Stats API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PROPERTY_ID = os.environ.get('PROPERTY_ID', '368035934')

# Request/Response Models
class AnalyticsRequest(BaseModel):
    start_date: str
    end_date: str
    dimensions: List[str] = []
    metrics: List[str]
    limit: int = 10000



# Root endpoint (API only)
@app.get("/api")
def root():
    return {
        "message": "Tenacious Stats API",
        "version": "1.0.0",
        "ga4_available": GA4_AVAILABLE,
        "gbp_available": GBP_AVAILABLE
    }

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "property_id": PROPERTY_ID,
        "ga4_available": GA4_AVAILABLE,
        "ga4_error": ga4_error,
        "gbp_available": GBP_AVAILABLE
    }

# GA4 Analytics Endpoints
if GA4_AVAILABLE:
    @app.get("/api/analytics/overview")
    def get_overview(start_date: str, end_date: str):
        """Get overview metrics."""
        try:
            dimensions = []
            metrics = ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
            return {"success": True, "data": data[0] if data else {}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/sources")
    def get_sources(start_date: str, end_date: str, limit: int = 10):
        """Get traffic sources."""
        try:
            dimensions = ['sessionSourceMedium']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/pages")
    def get_pages(start_date: str, end_date: str, limit: int = 15):
        """Get top pages."""
        try:
            dimensions = ['pagePath', 'pageTitle']
            metrics = ['screenPageViews', 'activeUsers']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/cities")
    def get_cities(start_date: str, end_date: str, limit: int = 10):
        """Get top cities."""
        try:
            dimensions = ['city']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/retention")
    def get_retention(start_date: str, end_date: str):
        """Get new vs returning users."""
        try:
            dimensions = ['newVsReturning']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/countries")
    def get_countries(start_date: str, end_date: str):
        """Get sessions by country."""
        try:
            dimensions = ['country']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/devices")
    def get_devices(start_date: str, end_date: str):
        """Get sessions by device category."""
        try:
            dimensions = ['deviceCategory']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/events")
    def get_events(start_date: str, end_date: str, limit: int = 20):
        """Get top events."""
        try:
            dimensions = ['eventName']
            metrics = ['eventCount']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
else:
    # Register same routes when GA4 not available so frontend gets JSON instead of 404
    _GA4_UNAVAILABLE = {"success": False, "data": None, "error": "GA4 not available. Check credentials.json and utils path."}

    @app.get("/api/analytics/overview")
    def get_overview_unavailable(start_date: str, end_date: str):
        return {**_GA4_UNAVAILABLE, "data": {}}

    @app.get("/api/analytics/sources")
    def get_sources_unavailable(start_date: str, end_date: str, limit: int = 10):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/pages")
    def get_pages_unavailable(start_date: str, end_date: str, limit: int = 15):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/cities")
    def get_cities_unavailable(start_date: str, end_date: str, limit: int = 10):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/retention")
    def get_retention_unavailable(start_date: str, end_date: str):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/countries")
    def get_countries_unavailable(start_date: str, end_date: str):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/devices")
    def get_devices_unavailable(start_date: str, end_date: str):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/events")
    def get_events_unavailable(start_date: str, end_date: str, limit: int = 20):
        return {**_GA4_UNAVAILABLE, "data": []}

# Google Business Profile Endpoints
if GBP_AVAILABLE:
    @app.get("/api/gbp/insights")
    def get_gbp_insights(start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Get Google Business Profile Insights."""
        try:
            result = gbp.get_insights(start_date, end_date)
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GBP Error: {str(e)}")

    @app.get("/api/gbp/reviews")
    def get_gbp_reviews():
        """Get Google Business Profile Reviews."""
        try:
            result = gbp.get_reviews()
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GBP Error: {str(e)}")

    @app.get("/api/gbp/ratings")
    def get_gbp_ratings():
        """Get Google Business Profile ratings summary (for dashboard)."""
        try:
            result = gbp.get_ratings()
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GBP Error: {str(e)}")
else:
    @app.get("/api/gbp/insights")
    def get_gbp_insights_unavailable():
        raise HTTPException(status_code=503, detail="GBP module not available")

    @app.get("/api/gbp/reviews")
    def get_gbp_reviews_unavailable():
        raise HTTPException(status_code=503, detail="GBP module not available")

    @app.get("/api/gbp/ratings")
    def get_gbp_ratings_unavailable():
        raise HTTPException(status_code=503, detail="GBP module not available")

# Vercel serverless function handler
# Vercel will automatically detect the FastAPI app
# For local development
if __name__ == "__main__":
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    
    # Mount public directory for static files (only for local dev)
    # This allows localhost:8000/ to serve public/index.html
    if os.path.exists("public"):
        app.mount("/", StaticFiles(directory="public", html=True), name="public")
        print("Serving static files from 'public' directory")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Mount static files if public directory exists (Local Development)
# We mount this LAST so it doesn't shadow the API routes defined above.
try:
    if os.path.exists('public'):
        from fastapi.staticfiles import StaticFiles
        app.mount('/', StaticFiles(directory='public', html=True), name='public')
        print('Mounted public directory at / (after API routes)')
except ImportError:
    print('Could not import StaticFiles - static serving unavailable')

