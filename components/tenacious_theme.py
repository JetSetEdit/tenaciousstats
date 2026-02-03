"""
Reusable Streamlit components for Tenacious Tapes branding
Save this as components/tenacious_theme.py
"""

import streamlit as st

def apply_tenacious_theme():
    """Applies Tenacious Tapes brand styling to Streamlit app."""
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

def tenacious_header(title: str, subtitle: str = ""):
    """Creates a branded header banner."""
    st.markdown(f"""
    <div class="tenacious-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def tenacious_footer():
    """Creates a branded footer with contact info."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.9rem;">
        <p style="color: #2c3e50;"><strong>Tenacious Tapes</strong> - Adhesive Tapes for every application</p>
        <p style="margin-top: 0.5rem; color: #7f8c8d;">
            📞 +61 (0)3 9580 5573 | ✉️ customerservice@tenacioustapes.com.au
        </p>
    </div>
    """, unsafe_allow_html=True)










