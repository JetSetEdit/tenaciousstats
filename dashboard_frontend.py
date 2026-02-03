"""
Streamlit Frontend - Calls FastAPI Backend
This separates the UI from data fetching logic
"""

import streamlit as st
import pandas as pd
import datetime
import httpx
import plotly.express as px

# Backend API Configuration
API_BASE_URL = "http://localhost:8000"

# --- HELPER FUNCTIONS ---

def call_api(endpoint: str, params: dict = None):
    """Calls the FastAPI backend."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        st.error("⚠️ **Backend API not running!** Please start the backend server:\n\n```bash\npython api/backend.py\n```")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"API Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return None

def format_metric(value):
    """Formats large numbers."""
    try:
        val = float(value)
        if val >= 1_000_000:
            return f"{val/1_000_000:.1f}M"
        if val >= 1_000:
            return f"{val/1_000:.1f}K"
        return f"{val:,.0f}"
    except (ValueError, TypeError):
        return value

# --- MAIN DASHBOARD APP ---

def main():
    st.set_page_config(
        page_title="Tenacious Stats Dashboard", 
        layout="wide",
        page_icon="📊"
    )
    
    # Check backend health
    health = call_api("/health")
    if health:
        if health.get("status") == "healthy":
            st.sidebar.success("✅ Backend Connected")
        else:
            st.sidebar.warning("⚠️ Backend Issues")
    
    # Inject custom CSS (same as before)
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
        
        .main {
            background-color: #f8f9fa;
            font-family: 'Roboto', sans-serif;
        }
        
        .stApp > header {
            background-color: rgb(0, 0, 0);
        }
        
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        
        h1 {
            color: #2c3e50 !important;
            font-weight: 900 !important;
        }
        
        h2, h3 {
            color: #2c3e50 !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #ff5800;
            font-weight: 700;
        }
        
        .stButton > button {
            background-color: #ff5800;
            color: white;
            border-radius: 6px;
        }
        
        .stButton > button:hover {
            background-color: #d43d00;
        }
        
        .tenacious-header {
            background: rgb(0, 0, 0);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border-left: 4px solid #ff5800;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom header banner
    st.markdown("""
    <div class="tenacious-header">
        <h1>📊 Tenacious Stats Dashboard</h1>
        <p>Analytics for Tenacious Tapes - Adhesive Tapes for every application</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- SIDEBAR: Configuration ---
    st.sidebar.markdown("### ⚙️ Configuration")
    
    # Date Selection
    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=30)
    
    start_date = st.sidebar.date_input("Start Date", default_start)
    end_date = st.sidebar.date_input("End Date", today)
    
    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        return
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Section Selection
    sections = st.sidebar.multiselect(
        "Select Sections to View",
        [
            "Overview", 
            "Traffic Sources", 
            "Top Pages", 
            "User Retention", 
            "Geographics (Cities/Countries)",
            "Tech/Devices",
            "Events",
            "Google Business Profile"
        ],
        default=["Overview", "Traffic Sources", "Top Pages"]
    )
    
    # Reload Button
    if st.sidebar.button("Refresh Data"):
        st.rerun()
    
    # --- DATA LOADING & DISPLAY ---
    
    # 1. OVERVIEW SECTION
    if "Overview" in sections:
        st.header("1. Traffic Overview")
        
        result = call_api("/analytics/overview", {
            "start_date": start_date_str,
            "end_date": end_date_str
        })
        
        if result and result.get("success"):
            stats = result.get("data", {})
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Sessions", format_metric(stats.get('sessions', 0)))
                col2.metric("Total Users", format_metric(stats.get('totalUsers', 0)))
                col3.metric("Page Views", format_metric(stats.get('screenPageViews', 0)))
                col4.metric("Engagement Rate", f"{float(stats.get('engagementRate', 0))*100:.1f}%")
                
                col5, col6 = st.columns(2)
                col5.metric("Avg. Session Duration", f"{float(stats.get('averageSessionDuration', 0)):.1f} sec")
                col6.metric("Bounce Rate", f"{float(stats.get('bounceRate', 0))*100:.1f}%")
            else:
                st.info("No overview data available for this period.")
        else:
            st.info("Unable to fetch overview data.")
            
        st.divider()
    
    # 2. TRAFFIC SOURCES
    if "Traffic Sources" in sections:
        st.header("2. Traffic Sources")
        
        result = call_api("/analytics/sources", {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "limit": 10
        })
        
        if result and result.get("success"):
            df_sources = pd.DataFrame(result.get("data", []))
            if not df_sources.empty:
                df_sources['sessions'] = df_sources['sessions'].astype(int)
                df_sources = df_sources.sort_values('sessions', ascending=False)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.dataframe(df_sources, hide_index=True)
                    
                with col2:
                    colors = ['#ff5800', '#FE5000', '#d43d00', '#ff7a33', '#ff9d66']
                    fig = px.pie(
                        df_sources, 
                        values='sessions', 
                        names='sessionSourceMedium', 
                        title='Sessions by Source',
                        color_discrete_sequence=colors
                    )
                    fig.update_layout(
                        font_family="Roboto",
                        title_font_size=18,
                        title_font_color="#2c3e50"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No source data available.")
        else:
            st.info("Unable to fetch source data.")
            
        st.divider()
    
    # 3. TOP PAGES
    if "Top Pages" in sections:
        st.header("3. Top Pages")
        
        result = call_api("/analytics/pages", {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "limit": 15
        })
        
        if result and result.get("success"):
            df_pages = pd.DataFrame(result.get("data", []))
            if not df_pages.empty:
                df_pages['screenPageViews'] = df_pages['screenPageViews'].astype(int)
                df_pages['activeUsers'] = df_pages['activeUsers'].astype(int)
                df_pages = df_pages.sort_values('screenPageViews', ascending=False)
                
                st.dataframe(
                    df_pages[['pageTitle', 'pagePath', 'screenPageViews', 'activeUsers']], 
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No page data available.")
        else:
            st.info("Unable to fetch page data.")
            
        st.divider()
    
    # 4. USER RETENTION
    if "User Retention" in sections:
        st.header("4. New vs Returning Users")
        
        result = call_api("/analytics/retention", {
            "start_date": start_date_str,
            "end_date": end_date_str
        })
        
        if result and result.get("success"):
            df_retention = pd.DataFrame(result.get("data", []))
            if not df_retention.empty:
                df_retention['sessions'] = df_retention['sessions'].astype(int)
                
                color_map = {'new': '#ff5800', 'returning': '#d43d00'}
                fig = px.bar(
                    df_retention, 
                    x='newVsReturning', 
                    y='sessions', 
                    title='New vs Returning Sessions', 
                    color='newVsReturning',
                    color_discrete_map=color_map
                )
                fig.update_layout(
                    font_family="Roboto",
                    title_font_size=18,
                    title_font_color="#2c3e50"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No retention data available.")
        else:
            st.info("Unable to fetch retention data.")
            
        st.divider()
    
    # 5. GEOGRAPHICS
    if "Geographics (Cities/Countries)" in sections:
        st.header("5. Geographics")
        
        tab1, tab2 = st.tabs(["Cities", "Countries"])
        
        with tab1:
            result = call_api("/analytics/cities", {
                "start_date": start_date_str,
                "end_date": end_date_str,
                "limit": 10
            })
            if result and result.get("success"):
                df_cities = pd.DataFrame(result.get("data", []))
                if not df_cities.empty:
                    df_cities['sessions'] = df_cities['sessions'].astype(int)
                    df_cities = df_cities.sort_values('sessions', ascending=False)
                    st.bar_chart(df_cities.set_index('city'))
        
        with tab2:
            result = call_api("/analytics/countries", {
                "start_date": start_date_str,
                "end_date": end_date_str
            })
            if result and result.get("success"):
                df_country = pd.DataFrame(result.get("data", []))
                if not df_country.empty:
                    df_country['sessions'] = df_country['sessions'].astype(int)
                    fig = px.choropleth(
                        df_country, 
                        locations='country', 
                        locationmode='country names', 
                        color='sessions', 
                        title="Sessions by Country",
                        color_continuous_scale=['#fff5f0', '#ffb899', '#ff5800', '#d43d00']
                    )
                    fig.update_layout(
                        font_family="Roboto",
                        title_font_size=18,
                        title_font_color="#2c3e50"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
    
    # 6. TECH / DEVICES
    if "Tech/Devices" in sections:
        st.header("6. Device Categories")
        
        result = call_api("/analytics/devices", {
            "start_date": start_date_str,
            "end_date": end_date_str
        })
        
        if result and result.get("success"):
            df_device = pd.DataFrame(result.get("data", []))
            if not df_device.empty:
                df_device['sessions'] = df_device['sessions'].astype(int)
                colors = ['#ff5800', '#d43d00', '#FE5000', '#ff7a33']
                fig = px.pie(
                    df_device, 
                    values='sessions', 
                    names='deviceCategory', 
                    title='Sessions by Device',
                    color_discrete_sequence=colors
                )
                fig.update_layout(
                    font_family="Roboto",
                    title_font_size=18,
                    title_font_color="#2c3e50"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
    
    # 7. EVENTS
    if "Events" in sections:
        st.header("7. Top Events")
        
        result = call_api("/analytics/events", {
            "start_date": start_date_str,
            "end_date": end_date_str,
            "limit": 20
        })
        
        if result and result.get("success"):
            df_events = pd.DataFrame(result.get("data", []))
            if not df_events.empty:
                df_events['eventCount'] = df_events['eventCount'].astype(int)
                df_events = df_events.sort_values('eventCount', ascending=False)
                
                st.dataframe(df_events, hide_index=True, use_container_width=True)
            else:
                st.info("No event data available.")
        else:
            st.info("Unable to fetch event data.")
        
        st.divider()

    # 8. GOOGLE BUSINESS PROFILE
    if "Google Business Profile" in sections:
        st.header("8. Google Business Profile")
        
        tab1, tab2 = st.tabs(["Insights", "Reviews"])
        
        with tab1:
            st.subheader("Performance Metrics")
            result = call_api("/gbp/insights", {
                "start_date": start_date_str,
                "end_date": end_date_str
            })
            
            if result and result.get("success"):
                data = result.get("data", [])
                if data:
                    # Transform data for plotting
                    # Structure is list of objects with 'datedValues'
                    # We need to flatten this.
                    # Actually, let's see the structure returned by API.
                    # It returns a list of MetricTimeSeries.
                    # Each has 'metric': 'WEBSITE_CLICKS', 'datedValues': [...]
                    
                    # We want to create a DataFrame: Date | Metric | Value
                    records = []
                    for item in data:
                        # Item structure from fetchMultiDailyMetricsTimeSeries
                        metric_name = item.get('dailyMetric')
                        
                        # dailyMetricTimeSeries is a list (could be multiple if sub-entities exist)
                        time_series_list = item.get('dailyMetricTimeSeries', [])
                        
                        for series in time_series_list:
                            # Each series has datedValues
                            for val in series.get('datedValues', []):
                                date_obj = val.get('date')
                                if date_obj:
                                    date_str = f"{date_obj['year']}-{date_obj['month']}-{date_obj['day']}"
                                    value = int(val.get('value', 0))
                                    records.append({
                                        'Date': date_str,
                                        'Metric': metric_name,
                                        'Value': value
                                    })
                    
                    if records:
                        df_gbp = pd.DataFrame(records)
                        
                        # Summary Metrics
                        total_views = df_gbp[df_gbp['Metric'].str.contains('IMPRESSIONS')]['Value'].sum()
                        total_actions = df_gbp[df_gbp['Metric'].isin(['WEBSITE_CLICKS', 'CALL_CLICKS', 'BUSINESS_DIRECTION_REQUESTS'])]['Value'].sum()
                        
                        c1, c2 = st.columns(2)
                        c1.metric("Total Impressions", format_metric(total_views))
                        c2.metric("Total Actions", format_metric(total_actions))
                        
                        # Chart
                        fig = px.line(
                            df_gbp, 
                            x='Date', 
                            y='Value', 
                            color='Metric',
                            title='Daily Performance'
                        )
                        fig.update_layout(
                            font_family="Roboto",
                            title_font_size=18,
                            title_font_color="#2c3e50"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No data points found for this period.")
                else:
                    st.info("No insights data available.")
            elif result and "error" in result:
                st.error(f"GBP Error: {result['error']}")
                if "details" in result:
                    st.code(result["details"], language="json")
            else:
                st.info("Unable to fetch GBP insights.")
                
        with tab2:
            st.subheader("Recent Reviews")
            result = call_api("/gbp/reviews")
            
            if result and result.get("success"):
                reviews = result.get("reviews", [])
                avg_rating = result.get("averageRating", 0)
                total_count = result.get("totalReviewCount", 0)
                
                c1, c2 = st.columns(2)
                c1.metric("Average Rating", f"{avg_rating} ⭐")
                c2.metric("Total Reviews", total_count)
                
                st.markdown("---")
                
                for review in reviews:
                    reviewer = review.get('reviewer', {}).get('displayName', 'Anonymous')
                    star_rating = review.get('starRating', 'STAR_RATING_UNSPECIFIED')
                    comment = review.get('comment', '')
                    create_time = review.get('createTime', '')
                    
                    stars = "⭐" * 5
                    if star_rating == "ONE": stars = "⭐"
                    elif star_rating == "TWO": stars = "⭐⭐"
                    elif star_rating == "THREE": stars = "⭐⭐⭐"
                    elif star_rating == "FOUR": stars = "⭐⭐⭐⭐"
                    elif star_rating == "FIVE": stars = "⭐⭐⭐⭐⭐"
                    
                    with st.container():
                        st.markdown(f"**{reviewer}** {stars}")
                        st.caption(f"Posted: {create_time}")
                        if comment:
                            st.write(comment)
                        st.markdown("---")
            elif result and "error" in result:
                st.error(f"GBP Error: {result['error']}")
            else:
                st.info("Unable to fetch reviews.")

        st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem;">
        <p style="color: #2c3e50;"><strong>Tenacious Tapes</strong> - Adhesive Tapes for every application</p>
        <p style="margin-top: 0.5rem; color: #7f8c8d;">
            📞 +61 (0)3 9580 5573 | ✉️ customerservice@tenacioustapes.com.au
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()










