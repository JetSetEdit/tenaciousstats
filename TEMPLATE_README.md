# Streamlit Dashboard Template Structure
# 
# This is a template structure for creating reusable Streamlit dashboards
# 
# Project Structure:
# ├── dashboard.py              # Main app file
# ├── .streamlit/
# │   └── config.toml           # Theme configuration
# ├── components/
# │   └── tenacious_theme.py    # Reusable UI components
# ├── utils/
# │   └── ga4_utils.py          # Data fetching utilities
# └── requirements.txt          # Dependencies
#
# Usage:
# 1. Copy this structure to a new project
# 2. Import components: from components.tenacious_theme import apply_tenacious_theme
# 3. Import utils: from utils.ga4_utils import fetch_ga4_data
# 4. Customize for your specific needs

"""
Example usage in a new dashboard:

import streamlit as st
from components.tenacious_theme import apply_tenacious_theme, tenacious_header, tenacious_footer
from utils.ga4_utils import fetch_ga4_data, format_metric, setup_credentials

def main():
    st.set_page_config(page_title="My Dashboard", layout="wide")
    apply_tenacious_theme()
    tenacious_header("📊 My Dashboard", "Custom subtitle")
    
    # Your dashboard code here
    
    tenacious_footer()

if __name__ == "__main__":
    main()
"""










