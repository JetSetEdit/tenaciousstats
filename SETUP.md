# Tenacious Stats Dashboard - Setup Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Google Analytics 4** property with API access
3. **Authentication** (choose one method below)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Authentication Setup

You have two options for authenticating with Google Analytics:

### Option 1: Service Account (Recommended for Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the **Google Analytics Data API**
4. Go to **IAM & Admin** > **Service Accounts**
5. Create a new service account or use existing one
6. Create a JSON key and download it
7. Save the JSON file as `credentials.json` in this directory
8. Grant the service account access to your GA4 property

### Option 2: gcloud CLI (For Development)

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Run authentication:
```bash
gcloud auth application-default login
```
3. Select your Google account that has access to the GA4 property

## Running the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features

- **Date Range Selection**: Choose custom start and end dates
- **Section Selection**: Toggle which analytics sections to display:
  - Overview (key metrics)
  - Traffic Sources
  - Top Pages
  - User Retention
  - Geographics (Cities/Countries)
  - Tech/Devices

## Configuration

Edit `dashboard.py` to change:
- `PROPERTY_ID`: Your GA4 Property ID (currently: 368035934)
- `CREDENTIALS_FILE`: Path to service account JSON (default: credentials.json)

## Troubleshooting

**Authentication Errors:**
- Ensure `credentials.json` exists OR gcloud is authenticated
- Verify the service account/user has access to the GA4 property
- Check that Google Analytics Data API is enabled in your project

**No Data Showing:**
- Verify the date range has data
- Check that the Property ID is correct
- Ensure the GA4 property is active and receiving traffic










