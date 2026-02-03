import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy
)
import pandas as pd

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

# CUSTOM DATES
START_DATE = '2025-12-01'
END_DATE = '2025-12-10'
REPORT_NAME = 'Report_Dec_01_to_Dec_10_2025.md'

def run_report(client, dimensions, metrics, start_date, end_date, row_limit=10000):
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=dim) for dim in dimensions],
        metrics=[Metric(name=met) for met in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=row_limit
    )
    response = client.run_report(request=request)

    data = []
    for row in response.rows:
        item = {}
        for i, dim in enumerate(dimensions):
            item[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            item[met] = row.metric_values[i].value
        data.append(item)
    
    return pd.DataFrame(data)

def format_number(num):
    num = float(num)
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return f"{num:.0f}"

def main():
    print(f"Generating Custom Report for: {START_DATE} to {END_DATE}...")
    
    try:
        client = BetaAnalyticsDataClient()
    except Exception as e:
        print(f"Error authenticating: {e}")
        return

    # --- FETCH DATA ---
    
    # 1. Overview
    df_overview = run_report(client, [], ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate'], START_DATE, END_DATE)
    
    # 2. Sources
    df_sources = run_report(client, ['sessionSourceMedium'], ['sessions'], START_DATE, END_DATE)
    
    # 3. Pages
    df_pages = run_report(client, ['pagePath', 'pageTitle'], ['screenPageViews'], START_DATE, END_DATE)
    
    # 4. Cities
    df_cities = run_report(client, ['city'], ['sessions'], START_DATE, END_DATE)

    # 5. Events (For Leads)
    df_events = run_report(client, ['eventName'], ['eventCount'], START_DATE, END_DATE)

    # --- PROCESS DATA ---
    
    if not df_overview.empty:
        stats = df_overview.iloc[0]
        sessions = float(stats['sessions'])
        users = float(stats['totalUsers'])
        views = float(stats['screenPageViews'])
        avg_duration = float(stats['averageSessionDuration'])
        engagement_rate = float(stats['engagementRate']) * 100
    else:
        sessions = users = views = avg_duration = engagement_rate = 0

    # Top Sources
    if not df_sources.empty:
        df_sources['sessions'] = df_sources['sessions'].astype(int)
        top_sources = df_sources.sort_values('sessions', ascending=False).head(5)
        total_source_sessions = df_sources['sessions'].sum()
        top_sources['pct'] = (top_sources['sessions'] / total_source_sessions) * 100
    else:
        top_sources = pd.DataFrame()

    # Top Pages & Products
    top_pages = pd.DataFrame()
    top_products = pd.DataFrame()
    
    if not df_pages.empty:
        df_pages['screenPageViews'] = df_pages['screenPageViews'].astype(int)
        top_pages = df_pages.sort_values('screenPageViews', ascending=False).head(10)
        
        # Filter for Products
        product_pages = df_pages[df_pages['pagePath'].str.contains('/product/', case=False) | df_pages['pagePath'].str.contains('/product-category/', case=False)]
        top_products = product_pages.sort_values('screenPageViews', ascending=False).head(5)
    else:
        top_pages = pd.DataFrame()

    # Lead Events
    direct_inquiries = 0
    referral_intent = 0
    
    if not df_events.empty:
        df_events['eventCount'] = df_events['eventCount'].astype(int)
        # Direct Inquiries
        forms = df_events[df_events['eventName'] == 'generate_lead']['eventCount'].sum()
        phones = df_events[df_events['eventName'] == 'click_phone']['eventCount'].sum()
        emails = df_events[df_events['eventName'] == 'click_email']['eventCount'].sum()
        direct_inquiries = int(forms + phones + emails)
        
        # Referral Intent
        buys = df_events[df_events['eventName'] == 'click_buy_online']['eventCount'].sum()
        referral_intent = int(buys)

    # Top Cities
    if not df_cities.empty:
        df_cities['sessions'] = df_cities['sessions'].astype(int)
        top_cities = df_cities.sort_values('sessions', ascending=False).head(5)
        total_city_sessions = df_cities['sessions'].sum()
        top_cities['pct'] = (top_cities['sessions'] / total_city_sessions) * 100
    else:
        top_cities = pd.DataFrame()

    # --- GENERATE MARKDOWN REPORT ---
    
    with open(REPORT_NAME, 'w', encoding='utf-8') as f:
        f.write(f"# Custom Analytics Report: Dec 1 - Dec 10, 2025\n")
        f.write(f"**Period:** {START_DATE} to {END_DATE}\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write(f"- **Total Sessions:** {format_number(sessions)}\n")
        f.write(f"- **Total Page Views:** {format_number(views)}\n")
        f.write(f"- **Total Users:** {format_number(users)}\n")
        f.write(f"- **Direct Inquiries (Forms/Phone):** {direct_inquiries}\n")
        f.write(f"- **Referral Intent (Buy Online):** {referral_intent}\n")
        f.write(f"- **Avg. Session Duration:** {avg_duration:.0f} seconds\n")
        f.write(f"- **Engagement Rate:** {engagement_rate:.1f}%\n\n")
        
        f.write("## 2. Traffic Sources\n")
        if not top_sources.empty:
            for _, row in top_sources.iterrows():
                f.write(f"- **{row['sessionSourceMedium']}:** {row['pct']:.1f}% ({format_number(row['sessions'])})\n")
        else:
            f.write("No source data available.\n")
        f.write("\n")
        
        f.write("## 3. Most Visited Pages\n")
        if not top_pages.empty:
            for _, row in top_pages.iterrows():
                f.write(f"1. **{row['pageTitle']}** (`{row['pagePath']}`) - {format_number(row['screenPageViews'])} views\n")
        else:
            f.write("No page data available.\n")
        f.write("\n")
        
        f.write("## 4. Top Products\n")
        if not top_products.empty:
            for _, row in top_products.iterrows():
                f.write(f"1. **{row['pageTitle']}** - {format_number(row['screenPageViews'])} views\n")
        else:
            f.write("No product page data found.\n")
        f.write("\n")
        
        f.write("## 5. Top Cities\n")
        if not top_cities.empty:
            for _, row in top_cities.iterrows():
                f.write(f"- **{row['city']}:** {row['pct']:.1f}%\n")
        else:
            f.write("No city data available.\n")

    print(f"Report generated: {REPORT_NAME}")

if __name__ == "__main__":
    main()
