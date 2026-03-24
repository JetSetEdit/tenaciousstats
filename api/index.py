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
try:
    from utils.ga4_utils import (
        get_client,
        fetch_analytics_data,
        fetch_blog_screen_page_views_total,
        fetch_path_screen_page_views_total,
    )
    GA4_AVAILABLE = True
except ImportError:
    GA4_AVAILABLE = False
    print("Warning: GA4 utils not available")

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

try:
    from utils.on_a_roll_rss import fetch_on_a_roll_meta_by_month, DEFAULT_ON_A_ROLL_FEED
    OAR_RSS_AVAILABLE = True
except ImportError:
    OAR_RSS_AVAILABLE = False
    DEFAULT_ON_A_ROLL_FEED = "https://www.tenacioustapes.com.au/category/on-a-roll/feed/"

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

# Root endpoint (API info only - dashboard served by StaticFiles)
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
        "gbp_available": GBP_AVAILABLE
    }


@app.get("/api/on-a-roll-slugs")
def on_a_roll_slugs(feed_url: Optional[str] = None):
    """
    Server-side fetch of WordPress category RSS (avoids browser CORS).
    Returns featuredPathContains (slug per month) and featuredTitles (RSS <title>, same as page H1 on typical WordPress).
    """
    if not OAR_RSS_AVAILABLE:
        return {
            "success": False,
            "data": {"featuredPathContains": {}, "featuredTitles": {}, "feedUrl": ""},
            "error": "on_a_roll_rss module not available",
        }
    url = (feed_url or "").strip() or DEFAULT_ON_A_ROLL_FEED
    try:
        by_slug, by_title = fetch_on_a_roll_meta_by_month(url)
        return {
            "success": True,
            "data": {
                "featuredPathContains": by_slug,
                "featuredTitles": by_title,
                "feedUrl": url,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "data": {"featuredPathContains": {}, "featuredTitles": {}, "feedUrl": url},
            "error": str(e),
        }


# GA4 Analytics Endpoints
if GA4_AVAILABLE:
    @app.get("/api/analytics/overview")
    def get_overview(start_date: str, end_date: str, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get overview metrics."""
        try:
            dimensions = []
            metrics = ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data[0] if data else {}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/sources")
    def get_sources(start_date: str, end_date: str, limit: int = 10, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get traffic sources."""
        try:
            dimensions = ['sessionSourceMedium']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/pages")
    def get_pages(start_date: str, end_date: str, limit: int = 15, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get top pages."""
        try:
            dimensions = ['pagePath', 'pageTitle']
            metrics = ['screenPageViews', 'activeUsers']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/blog-path-views")
    def get_blog_path_views(
        start_date: str,
        end_date: str,
        path_contains: str = "blog",
    ):
        """
        Total screenPageViews for URLs whose pagePath contains path_contains (case-insensitive).
        Uses GA4 dimension filter — not limited to top-N landing pages.
        """
        try:
            total = fetch_blog_screen_page_views_total(
                start_date, end_date, path_contains=path_contains
            )
            return {
                "success": True,
                "data": {
                    "screenPageViews": total,
                    "pathContains": path_contains,
                },
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/path-views-total")
    def get_path_views_total(
        start_date: str,
        end_date: str,
        path: str,
        match: str = "contains",
    ):
        """
        Total screenPageViews for pagePath.
        match=contains: substring (case-insensitive), e.g. oar-f701
        match=exact: exact pagePath in GA4, e.g. /on-a-roll/
        """
        try:
            m = (match or "contains").strip().lower()
            if m not in ("contains", "exact"):
                m = "contains"
            total = fetch_path_screen_page_views_total(
                start_date, end_date, path, match_type=m
            )
            return {
                "success": True,
                "data": {
                    "screenPageViews": total,
                    "path": path,
                    "match": m,
                },
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/cities")
    def get_cities(start_date: str, end_date: str, limit: int = 10, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get top cities."""
        try:
            dimensions = ['city']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/retention")
    def get_retention(start_date: str, end_date: str, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get new vs returning users."""
        try:
            dimensions = ['newVsReturning']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/countries")
    def get_countries(start_date: str, end_date: str, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get sessions by country."""
        try:
            dimensions = ['country']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/devices")
    def get_devices(start_date: str, end_date: str, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get sessions by device category."""
        try:
            dimensions = ['deviceCategory']
            metrics = ['sessions']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/analytics/events")
    def get_events(start_date: str, end_date: str, limit: int = 20, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get top events."""
        try:
            dimensions = ['eventName']
            metrics = ['eventCount']
            data = fetch_analytics_data(start_date, end_date, dimensions, metrics, limit, compare_start_date=compare_start_date, compare_end_date=compare_end_date)
            return {"success": True, "data": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
else:
    # Register same routes when GA4 not available so frontend gets JSON instead of 404
    _GA4_UNAVAILABLE = {"success": False, "data": None, "error": "GA4 not available. Check credentials.json and utils path."}

    @app.get("/api/analytics/overview")
    def get_overview_unavailable(start_date: str, end_date: str, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        return {**_GA4_UNAVAILABLE, "data": {}}

    @app.get("/api/analytics/sources")
    def get_sources_unavailable(start_date: str, end_date: str, limit: int = 10):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/pages")
    def get_pages_unavailable(start_date: str, end_date: str, limit: int = 15):
        return {**_GA4_UNAVAILABLE, "data": []}

    @app.get("/api/analytics/blog-path-views")
    def get_blog_path_views_unavailable(start_date: str, end_date: str, path_contains: str = "blog"):
        return {**_GA4_UNAVAILABLE, "data": {"screenPageViews": 0, "pathContains": path_contains}}

    @app.get("/api/analytics/path-views-total")
    def get_path_views_total_unavailable(start_date: str, end_date: str, path: str, match: str = "contains"):
        return {**_GA4_UNAVAILABLE, "data": {"screenPageViews": 0, "path": path, "match": match}}

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
    def get_gbp_insights(start_date: Optional[str] = None, end_date: Optional[str] = None, compare_start_date: Optional[str] = None, compare_end_date: Optional[str] = None):
        """Get Google Business Profile Insights."""
        try:
            # Current period
            result = gbp.get_insights(start_date, end_date)
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            # Comparison period
            if compare_start_date and compare_end_date:
                comp_result = gbp.get_insights(compare_start_date, compare_end_date)
                if not "error" in comp_result:
                    # Merge summaries
                    curr_summary = result.get("summary", {})
                    comp_summary = comp_result.get("summary", {})
                    
                    # Add _compare fields to summary
                    if "views" in curr_summary and "views" in comp_summary:
                        curr_summary["views"]["search_compare"] = comp_summary["views"].get("search", 0)
                        curr_summary["views"]["maps_compare"] = comp_summary["views"].get("maps", 0)
                    
                    if "customerActions" in curr_summary and "customerActions" in comp_summary:
                        curr_summary["customerActions"]["websiteClicks_compare"] = comp_summary["customerActions"].get("websiteClicks", 0)
                        curr_summary["customerActions"]["directionRequests_compare"] = comp_summary["customerActions"].get("directionRequests", 0)
            
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
        """Get Google Business Profile ratings summary (from reviews)."""
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Mount static files for local development (works with uvicorn --reload)
# This must be AFTER all API routes so they don't get shadowed
import os
_api_dir = os.path.dirname(os.path.abspath(__file__))
_public_dir = os.path.join(os.path.dirname(_api_dir), 'public')
if os.path.exists(_public_dir):
    from fastapi.staticfiles import StaticFiles
    app.mount('/', StaticFiles(directory=_public_dir, html=True), name='public')

