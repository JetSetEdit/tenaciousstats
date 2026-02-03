import os
import datetime
from dateutil.relativedelta import relativedelta
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

def get_last_month_dates():
    today = datetime.date.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - datetime.timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return first_day_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d'), first_day_last_month.strftime('%B %Y')

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

def load_csv(filename):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame()

def format_number(num):
    num = float(num)
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return f"{num:.0f}"

def main():
    start_date, end_date, month_name = get_last_month_dates()
    print(f"Generating report for: {month_name} ({start_date} to {end_date})...")
    
    try:
        client = BetaAnalyticsDataClient()
    except Exception as e:
        print(f"Error authenticating: {e}")
        return

    # --- FETCH DATA ---

    # 1. Overview
    df_overview = run_report(client, [], ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate'], start_date, end_date)
    
    # 2. Sources
    df_sources = run_report(client, ['sessionSourceMedium'], ['sessions'], start_date, end_date)
    
    # 3. Pages
    df_pages = run_report(client, ['pagePath', 'pageTitle'], ['screenPageViews'], start_date, end_date)
    
    # 4. New vs Returning
    df_retention = run_report(client, ['newVsReturning'], ['sessions'], start_date, end_date)
    
    # 5. Cities
    df_cities = run_report(client, ['city'], ['sessions'], start_date, end_date)

    # --- PROCESS DATA ---
    
    if not df_overview.empty:
        stats = df_overview.iloc[0]
        sessions = float(stats['sessions'])
        users = float(stats['totalUsers'])
        views = float(stats['screenPageViews'])
        bounce_rate = float(stats['bounceRate']) * 100
        avg_duration = float(stats['averageSessionDuration'])
        engagement_rate = float(stats['engagementRate']) * 100
    else:
        sessions = users = views = bounce_rate = avg_duration = engagement_rate = 0

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
    contact_views = 0
    
    if not df_pages.empty:
        df_pages['screenPageViews'] = df_pages['screenPageViews'].astype(int)
        top_pages = df_pages.sort_values('screenPageViews', ascending=False).head(10)
        
        product_pages = df_pages[df_pages['pagePath'].str.contains('/product/', case=False) | df_pages['pagePath'].str.contains('/product-category/', case=False)]
        top_products = product_pages.sort_values('screenPageViews', ascending=False).head(5)
        
        # Contact Page Views
        contact_page = df_pages[df_pages['pagePath'].str.contains('contact', case=False)]
        contact_views = contact_page['screenPageViews'].sum()

    # Lead Events (Categorized)
    df_events = load_csv('top_events.csv')
    direct_inquiries = 0
    referral_intent = 0
    
    if not df_events.empty:
        # Direct Inquiries (Forms + Phone + Email)
        forms = df_events[df_events['eventName'] == 'generate_lead']['eventCount'].sum()
        phones = df_events[df_events['eventName'] == 'click_phone']['eventCount'].sum()
        emails = df_events[df_events['eventName'] == 'click_email']['eventCount'].sum()
        direct_inquiries = int(forms + phones + emails)
        
        # Referral Intent (Buy Online)
        buys = df_events[df_events['eventName'] == 'click_buy_online']['eventCount'].sum()
        referral_intent = int(buys)

    # New vs Returning
    new_users_pct = 0
    returning_users_pct = 0
    if not df_retention.empty:
        df_retention['sessions'] = df_retention['sessions'].astype(int)
        total_retention = df_retention['sessions'].sum()
        for _, row in df_retention.iterrows():
            pct = (row['sessions'] / total_retention) * 100
            if row['newVsReturning'] == 'new':
                new_users_pct = pct
            elif row['newVsReturning'] == 'returning':
                returning_users_pct = pct

    # Top Cities
    if not df_cities.empty:
        df_cities['sessions'] = df_cities['sessions'].astype(int)
        top_cities = df_cities.sort_values('sessions', ascending=False).head(5)
        total_city_sessions = df_cities['sessions'].sum()
        top_cities['pct'] = (top_cities['sessions'] / total_city_sessions) * 100
    else:
        top_cities = pd.DataFrame()


    # --- GENERATE MARKDOWN REPORT ---
    report_filename = f"Monthly_Report_{month_name.replace(' ', '_')}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(f"# Monthly Website Analytics: {month_name}\n")
        f.write(f"**Period:** {start_date} to {end_date}\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write(f"- **Total Sessions:** {format_number(sessions)}\n")
        f.write(f"- **Total Page Views:** {format_number(views)}\n")
        f.write(f"- **Total Users:** {format_number(users)}\n")
        f.write(f"- **Direct Inquiries (Forms/Phone):** {direct_inquiries}\n")
        f.write(f"- **Referral Intent (Buy Online):** {referral_intent}\n")
        f.write(f"- **Avg. Session Duration:** {avg_duration:.0f} seconds\n\n")
        
        f.write("## 2. Traffic Sources\n")
        if not top_sources.empty:
            for _, row in top_sources.iterrows():
                f.write(f"- **{row['sessionSourceMedium']}:** {row['pct']:.1f}% ({format_number(row['sessions'])})\n")
        else:
            f.write("No source data available.\n")
        f.write("\n")
        
        f.write("## 3. Most Visited Areas\n")
        if not top_pages.empty:
            for _, row in top_pages.iterrows():
                f.write(f"1. **{row['pageTitle']}** (`{row['pagePath']}`) - {format_number(row['screenPageViews'])} views\n")
        else:
            f.write("No page data available.\n")
        f.write("\n")
        
        f.write("## 4. Product Interest\n")
        if not top_products.empty:
            for _, row in top_products.iterrows():
                f.write(f"1. **{row['pageTitle']}** - {format_number(row['screenPageViews'])} views\n")
        else:
            f.write("No product page data found.\n")
        f.write("\n")
        
        f.write("## 5. Additional Insights\n")
        f.write(f"- **Engagement Rate:** {engagement_rate:.1f}% (Sessions >10s or 2+ pageviews)\n")
        f.write(f"- **Lead Proxy (Contact Page Views):** {format_number(contact_views)}\n")
        f.write(f"- **User Retention:** {new_users_pct:.1f}% New vs {returning_users_pct:.1f}% Returning\n")
        f.write("\n**Top Cities:**\n")
        if not top_cities.empty:
            for _, row in top_cities.iterrows():
                f.write(f"- **{row['city']}:** {row['pct']:.1f}%\n")
        else:
            f.write("No city data available.\n")

    print(f"Report generated: {report_filename}")

if __name__ == "__main__":
    main()
