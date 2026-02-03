#!/usr/bin/env python3
"""
Simple GBP API Test Script
Quickly checks if Google Business Profile API returns data
"""

import sys
import os
from datetime import datetime, timedelta

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

try:
    import gbp
    print("[OK] GBP module imported successfully\n")
except ImportError as e:
    print(f"[ERROR] Failed to import GBP module: {e}")
    sys.exit(1)

def test_credentials():
    """Test if credentials are available"""
    print("=" * 60)
    print("1. Testing Credentials")
    print("=" * 60)
    
    creds = gbp.get_creds()
    if creds:
        print("[OK] Credentials found")
        print(f"   Service account: {creds.service_account_email}")
        return True
    else:
        print("[ERROR] No credentials found")
        print("   Check:")
        print("   - gbp-service-account-key.json exists in project root")
        print("   - OR GOOGLE_BUSINESS_PROFILE_CREDENTIALS_B64 env var is set")
        return False

def test_insights():
    """Test fetching insights"""
    print("\n" + "=" * 60)
    print("2. Testing Insights API")
    print("=" * 60)
    
    # Last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"   Date range: {start_date} to {end_date}")
    print("   Fetching insights...")
    
    try:
        result = gbp.get_insights(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if "error" in result:
            print(f"[ERROR] Error: {result['error']}")
            if "details" in result:
                print(f"   Details: {result['details'][:200]}...")
            return False
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            print(f"[OK] Success! Received {len(data)} metric series")
            
            # Show summary
            total_values = 0
            for item in data:
                metric_name = item.get('dailyMetric', 'Unknown')
                time_series = item.get('dailyMetricTimeSeries', [])
                for series in time_series:
                    values = series.get('datedValues', [])
                    total_values += len(values)
                    if values:
                        print(f"   [*] {metric_name}: {len(values)} data points")
            
            print(f"\n   Total data points: {total_values}")
            if total_values > 0:
                print("   [OK] Insights data is available!")
                return True
            else:
                print("   [WARN] No data points found (might be normal if no activity)")
                return False
        else:
            print("[ERROR] No data returned")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reviews():
    """Test fetching reviews"""
    print("\n" + "=" * 60)
    print("3. Testing Reviews API")
    print("=" * 60)
    
    print("   Fetching reviews...")
    
    try:
        result = gbp.get_reviews()
        
        if "error" in result:
            print(f"[ERROR] Error: {result['error']}")
            return False
        
        if result.get("success"):
            reviews = result.get("reviews", [])
            avg_rating = result.get("averageRating", 0)
            total_count = result.get("totalReviewCount", 0)
            
            print(f"[OK] Success!")
            print(f"   Average Rating: {avg_rating} stars")
            print(f"   Total Reviews: {total_count}")
            print(f"   Recent Reviews Returned: {len(reviews)}")
            
            if reviews:
                print("\n   Recent Reviews:")
                for i, review in enumerate(reviews[:5], 1):  # Show first 5
                    reviewer = review.get('reviewer', {}).get('displayName', 'Anonymous')
                    rating = review.get('starRating', 'UNSPECIFIED')
                    comment = review.get('comment', '')[:50]  # First 50 chars
                    print(f"   {i}. {reviewer} - {rating} - {comment}...")
            
            if total_count > 0 or len(reviews) > 0:
                print("\n   [OK] Reviews data is available!")
                return True
            else:
                print("\n   [WARN] No reviews found")
                return False
        else:
            print("[ERROR] No data returned")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "GBP API Quick Test" + "\n")
    
    # Test credentials
    if not test_credentials():
        print("\n[ERROR] Cannot proceed without credentials")
        sys.exit(1)
    
    # Test insights
    insights_ok = test_insights()
    
    # Test reviews
    reviews_ok = test_reviews()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if insights_ok:
        print("[OK] Insights: Working")
    else:
        print("[ERROR] Insights: Failed")
    
    if reviews_ok:
        print("[OK] Reviews: Working")
    else:
        print("[ERROR] Reviews: Failed")
    
    if insights_ok or reviews_ok:
        print("\n[SUCCESS] At least one endpoint is returning data!")
        sys.exit(0)
    else:
        print("\n[WARN] No data returned from any endpoint")
        print("   Check:")
        print("   - Service account has access to Business Profile")
        print("   - Required APIs are enabled in Google Cloud Console")
        print("   - Business Profile has data for the date range")
        sys.exit(1)

if __name__ == "__main__":
    main()

