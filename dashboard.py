import streamlit as st
import pandas as pd
import datetime
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import os
import plotly.express as px

# --- CONFIGURATION ---
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'

# Authentication Setup:
# Option 1: Service Account JSON file (credentials.json)
# Option 2: gcloud Application Default Credentials (run: gcloud auth application-default login)
if os.path.exists(CREDENTIALS_FILE):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE
    st.session_state.auth_method = "Service Account (credentials.json)"
else:
    # Will attempt to use Application Default Credentials from gcloud CLI
    st.session_state.auth_method = "gcloud Application Default Credentials"

# --- HELPER FUNCTIONS ---

@st.cache_resource
def get_client():
    """Initializes and returns the Analytics Client.
    
    Supports two authentication methods:
    1. Service Account JSON file (credentials.json)
    2. gcloud Application Default Credentials
    """
    try:
        client = BetaAnalyticsDataClient()
        return client
    except Exception as e:
        error_msg = str(e)
        if "credentials" in error_msg.lower() or "authentication" in error_msg.lower():
            st.error("""
            **Authentication Error**
            
            Please set up authentication using one of these methods:
            
            **Option 1: Service Account (Recommended for production)**
            1. Download service account JSON key from Google Cloud Console
            2. Save it as `credentials.json` in this directory
            
            **Option 2: gcloud CLI (For development)**
            1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
            2. Run: `gcloud auth application-default login`
            3. Select your Google account with GA4 access
            """)
        else:
            st.error(f"Failed to initialize Analytics client: {error_msg}")
        return None

@st.cache_data
def fetch_analytics_data(start_date, end_date, dimensions, metrics, limit=10000):
    """Fetches data from GA4 API and returns a Pandas DataFrame."""
    client = get_client()
    if not client:
        return pd.DataFrame()

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
        st.error(f"API Error: {e}")
        return pd.DataFrame()

    data = []
    for row in response.rows:
        item = {}
        for i, dim in enumerate(dimensions):
            item[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            item[met] = row.metric_values[i].value
        data.append(item)
    
    return pd.DataFrame(data)

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
    
    # Inject custom CSS for Tenacious Tapes branding
    st.markdown("""
    <style>
        /* Import Roboto font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap');
        
        /* Brand Colors */
        /* Primary orange: #FE5000 / #ff5800 */
        /* Primary dark: #d43d00 */
        /* Text dark: #2c3e50 */
        /* Text light: #7f8c8d */
        /* Background light: #f8f9fa */
        /* Background white: #ffffff */
        
        /* Main styling */
        .main {
            background-color: #f8f9fa;
            font-family: 'Roboto', sans-serif;
        }
        
        /* Header styling - black background */
        .stApp > header {
            background-color: rgb(0, 0, 0);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            color: #2c3e50;
            font-weight: 700;
        }
        
        /* Title styling */
        h1 {
            color: #2c3e50 !important;
            font-weight: 900 !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2, h3 {
            color: #2c3e50 !important;
            font-weight: 700 !important;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            color: #ff5800;
            font-weight: 700;
        }
        
        [data-testid="stMetricLabel"] {
            color: #2c3e50;
            font-weight: 500;
        }
        
        /* Buttons - orange background */
        .stButton > button {
            background-color: #ff5800;
            color: white;
            border-radius: 6px;
            border: none;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            background-color: #d43d00;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(254, 80, 0, 0.3);
        }
        
        /* Info boxes */
        .stInfo {
            background-color: #f8f9fa;
            border-left: 4px solid #ff5800;
        }
        
        /* Error boxes */
        .stError {
            border-left: 4px solid #EF4444;
        }
        
        /* Dataframes */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            background-color: #ffffff;
        }
        
        /* Divider styling */
        hr {
            border-color: #e0e0e0;
            margin: 2rem 0;
        }
        
        /* Tabs - border #e0e0e0, padding 24px */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #7f8c8d;
            font-weight: 500;
            padding: 24px;
        }
        
        .stTabs [aria-selected="true"] {
            color: #ff5800;
            font-weight: 700;
            border-bottom: 2px solid #ff5800;
        }
        
        /* Custom header banner - black background with orange accent */
        .tenacious-header {
            background: rgb(0, 0, 0);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #ff5800;
        }
        
        .tenacious-header h1 {
            color: white !important;
            margin-bottom: 0.5rem;
        }
        
        .tenacious-header p {
            color: #ffffff;
            font-size: 1.1rem;
            margin: 0;
            opacity: 0.9;
        }
        
        /* Cards/Containers */
        .element-container {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Labels - orange color for product specs style */
        label {
            color: #2c3e50;
        }
        
        /* Select boxes and inputs */
        .stSelectbox label,
        .stDateInput label,
        .stMultiselect label {
            color: #2c3e50;
            font-weight: 500;
        }
        
        /* Sidebar text */
        [data-testid="stSidebar"] {
            color: #2c3e50;
        }
        
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #2c3e50;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom header banner - black background with white text
    st.markdown("""
    <div class="tenacious-header">
        <h1>📊 Tenacious Stats Dashboard</h1>
        <p>Analytics for Tenacious Tapes - Adhesive Tapes for every application</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show authentication method in sidebar
    if 'auth_method' in st.session_state:
        st.sidebar.info(f"🔐 Auth: {st.session_state.auth_method}")

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
            "Tech/Devices"
        ],
        default=["Overview", "Traffic Sources", "Top Pages"]
    )
    
    # Reload Button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()

    # --- DATA LOADING & DISPLAY ---

    # 1. OVERVIEW SECTION
    if "Overview" in sections:
        st.header("1. Traffic Overview")
        
        # Fetch Overview Data
        df_overview = fetch_analytics_data(
            start_date_str, end_date_str, 
            [], 
            ['sessions', 'totalUsers', 'screenPageViews', 'bounceRate', 'averageSessionDuration', 'engagementRate']
        )
        
        if not df_overview.empty:
            stats = df_overview.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Sessions", format_metric(stats['sessions']))
            col2.metric("Total Users", format_metric(stats['totalUsers']))
            col3.metric("Page Views", format_metric(stats['screenPageViews']))
            col4.metric("Engagement Rate", f"{float(stats['engagementRate'])*100:.1f}%")
            
            col5, col6 = st.columns(2)
            col5.metric("Avg. Session Duration", f"{float(stats['averageSessionDuration']):.1f} sec")
            col6.metric("Bounce Rate", f"{float(stats['bounceRate'])*100:.1f}%")
        else:
            st.info("No overview data available for this period.")
            
        st.divider()

    # 2. TRAFFIC SOURCES
    if "Traffic Sources" in sections:
        st.header("2. Traffic Sources")
        
        df_sources = fetch_analytics_data(
            start_date_str, end_date_str, 
            ['sessionSourceMedium'], 
            ['sessions']
        )
        
        if not df_sources.empty:
            df_sources['sessions'] = df_sources['sessions'].astype(int)
            df_sources = df_sources.sort_values('sessions', ascending=False).head(10)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(df_sources, hide_index=True)
                
            with col2:
                # Custom color palette matching Tenacious Tapes branding (orange theme)
                colors = ['#ff5800', '#FE5000', '#d43d00', '#ff7a33', '#ff9d66', '#ffb899', '#2c3e50', '#7f8c8d', '#95a5a6', '#bdc3c7']
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
                    title_font_color="#2c3e50",
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No source data available.")
            
        st.divider()

    # 3. TOP PAGES
    if "Top Pages" in sections:
        st.header("3. Top Pages")
        
        df_pages = fetch_analytics_data(
            start_date_str, end_date_str, 
            ['pagePath', 'pageTitle'], 
            ['screenPageViews', 'activeUsers']
        )
        
        if not df_pages.empty:
            df_pages['screenPageViews'] = df_pages['screenPageViews'].astype(int)
            df_pages['activeUsers'] = df_pages['activeUsers'].astype(int)
            df_pages = df_pages.sort_values('screenPageViews', ascending=False).head(15)
            
            st.dataframe(
                df_pages[['pageTitle', 'pagePath', 'screenPageViews', 'activeUsers']], 
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No page data available.")
            
        st.divider()

    # 4. USER RETENTION
    if "User Retention" in sections:
        st.header("4. New vs Returning Users")
        
        df_retention = fetch_analytics_data(
            start_date_str, end_date_str, 
            ['newVsReturning'], 
            ['sessions']
        )
        
        if not df_retention.empty:
            df_retention['sessions'] = df_retention['sessions'].astype(int)
            
            # Custom colors for retention chart - orange theme
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
                title_font_color="#2c3e50",
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No retention data available.")
            
        st.divider()

    # 5. GEOGRAPHICS
    if "Geographics (Cities/Countries)" in sections:
        st.header("5. Geographics")
        
        tab1, tab2 = st.tabs(["Cities", "Countries"])
        
        with tab1:
            df_cities = fetch_analytics_data(
                start_date_str, end_date_str, 
                ['city'], 
                ['sessions']
            )
            if not df_cities.empty:
                df_cities['sessions'] = df_cities['sessions'].astype(int)
                df_cities = df_cities.sort_values('sessions', ascending=False).head(10)
                st.bar_chart(df_cities.set_index('city'))
        
        with tab2:
            df_country = fetch_analytics_data(
                start_date_str, end_date_str, 
                ['country'], 
                ['sessions']
            )
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
        
        df_device = fetch_analytics_data(
            start_date_str, end_date_str, 
            ['deviceCategory'], 
            ['sessions']
        )
        
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
                title_font_color="#2c3e50",
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        st.divider()
    
    # Footer with contact info
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem; background-color: #ffffff; border-top: 1px solid #e0e0e0;">
        <p style="color: #2c3e50;"><strong>Tenacious Tapes</strong> - Adhesive Tapes for every application</p>
        <p style="margin-top: 0.5rem; color: #7f8c8d;">
            📞 +61 (0)3 9580 5573 | 
            ✉️ customerservice@tenacioustapes.com.au
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #7f8c8d;">
            57 Jamieson Way, Dandenong South VIC 3175 | ABN: 29 004 309 004
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

