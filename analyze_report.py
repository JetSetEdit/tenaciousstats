import pandas as pd
import os

def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame()

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def main():
    # 1. Traffic Overview
    df_traffic = load_csv('traffic_overview.csv')
    if not df_traffic.empty:
        total_sessions = df_traffic['sessions'].sum()
        total_users = df_traffic['totalUsers'].sum() # Note: Users are distinct per month, summing them is an approximation of total unique visitors over time but technically incorrect for "total unique users" ever. However, for a summary, it's often accepted or we can just report average monthly users. Let's report Total Sessions and Total Pageviews, and Average Monthly Users.
        total_views = df_traffic['screenPageViews'].sum()
        
        # Sort by date
        df_traffic = df_traffic.sort_values('yearMonth')
        
        # MoM Growth (Last month vs previous)
        if len(df_traffic) >= 2:
            last_month = df_traffic.iloc[-1]
            prev_month = df_traffic.iloc[-2]
            sessions_growth = ((last_month['sessions'] - prev_month['sessions']) / prev_month['sessions']) * 100
            views_growth = ((last_month['screenPageViews'] - prev_month['screenPageViews']) / prev_month['screenPageViews']) * 100
            growth_str = f"**Growth (Last Month):** Sessions {sessions_growth:+.1f}%, Pageviews {views_growth:+.1f}%"
        else:
            growth_str = "Not enough data for growth comparison."

        # Engagement
        avg_bounce = df_traffic['bounceRate'].mean() * 100 if 'bounceRate' in df_traffic.columns else 0
        avg_duration = df_traffic['averageSessionDuration'].mean() if 'averageSessionDuration' in df_traffic.columns else 0
        
    else:
        total_sessions = total_users = total_views = 0
        growth_str = "No traffic data available."
        avg_bounce = avg_duration = 0

    # 2. Traffic Sources
    df_sources = load_csv('traffic_sources.csv')
    if not df_sources.empty:
        total_source_sessions = df_sources['sessions'].sum()
        df_sources['percentage'] = (df_sources['sessions'] / total_source_sessions) * 100
        top_sources = df_sources.sort_values('sessions', ascending=False).head(5)
    else:
        top_sources = pd.DataFrame()

    # 3. Top Pages
    df_pages = load_csv('top_pages.csv')
    if not df_pages.empty:
        top_10_pages = df_pages.sort_values('screenPageViews', ascending=False).head(10)
        
        # Product Pages (filter by /product/)
        product_pages = df_pages[df_pages['pagePath'].str.contains('/product/', case=False) | df_pages['pagePath'].str.contains('/product-category/', case=False)]
        top_products = product_pages.sort_values('screenPageViews', ascending=False).head(5)
    else:
        top_10_pages = pd.DataFrame()
        top_products = pd.DataFrame()

    # 4. Site Search
    df_search = load_csv('site_search.csv')
    if not df_search.empty:
        top_search = df_search.sort_values('screenPageViews', ascending=False).head(5) # screenPageViews for search terms usually means number of times results were viewed
    else:
        top_search = pd.DataFrame()

    # 5. Demographics & Tech
    df_geo = load_csv('demographics.csv')
    if not df_geo.empty:
        top_countries = df_geo.sort_values('sessions', ascending=False).head(5)
        total_geo_sessions = df_geo['sessions'].sum()
        top_countries['percentage'] = (top_countries['sessions'] / total_geo_sessions) * 100
    else:
        top_countries = pd.DataFrame()

    df_device = load_csv('device_tech.csv')
    if not df_device.empty:
        total_device_sessions = df_device['sessions'].sum()
        df_device['percentage'] = (df_device['sessions'] / total_device_sessions) * 100
    else:
        df_device = pd.DataFrame()

    # 6. Retention
    df_retention = load_csv('retention.csv')
    new_users_pct = 0
    returning_users_pct = 0
    if not df_retention.empty:
        total_retention = df_retention['sessions'].sum()
        for _, row in df_retention.iterrows():
            pct = (row['sessions'] / total_retention) * 100
            if row['newVsReturning'] == 'new':
                new_users_pct = pct
            elif row['newVsReturning'] == 'returning':
                returning_users_pct = pct

    # 7. Cities
    df_cities = load_csv('cities.csv')
    if not df_cities.empty:
        top_cities = df_cities.sort_values('sessions', ascending=False).head(5)
        total_city_sessions = df_cities['sessions'].sum()
        top_cities['percentage'] = (top_cities['sessions'] / total_city_sessions) * 100
    else:
        top_cities = pd.DataFrame()
    
    # Contact Page Views (Lead Proxy)
    contact_views = 0
    if not df_pages.empty and 'pagePath' in df_pages.columns:
        # Drop NaNs or fill them to avoid boolean masking error
        df_pages['pagePath'] = df_pages['pagePath'].fillna('')
        contact_page = df_pages[df_pages['pagePath'].str.contains('contact', case=False)]
        contact_views = contact_page['screenPageViews'].sum()

    # Lead Events (Actual Form Submits)
    df_events = load_csv('top_events.csv')
    lead_count = 0
    if not df_events.empty:
        lead_events = df_events[df_events['eventName'] == 'generate_lead']
        if not lead_events.empty:
            lead_count = int(lead_events['eventCount'].sum())


    # --- GENERATE REPORT ---
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S AEDT")
    
    print("# Website Analytics Executive Summary: Tenacious Tapes")
    print(f"**Period:** Dec 1, 2025 to {datetime.date.today().strftime('%b %d, %Y')}")
    print(f"**Data Generated At:** {now}\n")

    print("## 1. Traffic Overview")
    print(f"- **Total Sessions:** {format_number(total_sessions)}")
    print(f"- **Total Page Views:** {format_number(total_views)}")
    print(f"- **Avg. Monthly Users:** {format_number(total_users / len(df_traffic)) if len(df_traffic) > 0 else 0}")
    print(f"- {growth_str}")
    print(f"- **Avg. Bounce Rate:** {avg_bounce:.1f}%")
    print(f"- **Avg. Session Duration:** {avg_duration:.0f} seconds")
    print("\n")

    print("## 2. Traffic Sources")
    if not top_sources.empty:
        for _, row in top_sources.iterrows():
            print(f"- **{row['sessionSourceMedium']}:** {row['percentage']:.1f}% ({format_number(row['sessions'])})")
    else:
        print("No source data.")
    print("\n")

    print("## 3. Most Visited Areas")
    print("**Top 10 Pages:**")
    if not top_10_pages.empty:
        for _, row in top_10_pages.iterrows():
            print(f"1. **{row['pageTitle']}** (`{row['pagePath']}`) - {format_number(row['screenPageViews'])} views")
    else:
        print("No page data.")
    print("\n")

    print("## 4. Product Interest")
    print("**Top Viewed Products:**")
    if not top_products.empty:
        for _, row in top_products.iterrows():
            print(f"1. **{row['pageTitle']}** - {format_number(row['screenPageViews'])} views")
    else:
        print("No product page data found.")
    
    print("\n**Top Search Queries:**")
    if not top_search.empty:
        for _, row in top_search.iterrows():
            print(f"- \"{row['searchTerm']}\" ({row['screenPageViews']} times)")
    else:
        print("No site search data available.")
    print("\n")

    print("## 5. Audience Insights")
    print("**Device Breakdown:**")
    if not df_device.empty:
        for _, row in df_device.iterrows():
            print(f"- **{row['deviceCategory'].capitalize()}:** {row['percentage']:.1f}%")
    
    print("\n**Top Locations (Country):**")
    if not top_countries.empty:
        for _, row in top_countries.iterrows():
            print(f"- **{row['country']}:** {row['percentage']:.1f}%")

    print("\n**Top Locations (City):**")
    if not top_cities.empty:
        for _, row in top_cities.iterrows():
            print(f"- **{row['city']}:** {row['percentage']:.1f}%")

    print("\n")
    print("## 6. Additional Insights")
    print(f"- **Engagement Rate:** {df_traffic['engagementRate'].mean() * 100:.1f}% (Sessions >10s or 2+ pageviews)")
    print(f"- **Total Leads (Form Submits):** {lead_count} (Tracking started Dec 2025)")
    print(f"- **Lead Proxy (Contact Page Views):** {format_number(contact_views)}")
    print(f"- **User Retention:** {new_users_pct:.1f}% New vs {returning_users_pct:.1f}% Returning")

if __name__ == "__main__":
    main()
