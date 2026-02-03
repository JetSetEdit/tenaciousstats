#!/usr/bin/env python3
"""
Create token.pickle for Google Business Profile (GBP) by signing in with the
Google account that owns your Business Profile (e.g. tenacioustapesmedia@gmail.com).

What this script automates:
  - Opens your default browser to Google sign-in
  - After you sign in, saves credentials to token.pickle (no more sign-in until token expires)
  - Dashboard then uses token.pickle for Business Profile automatically

Run from project root:  python gbp_oauth_login.py
"""

import os
import sys
import pickle
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SCOPES = ["https://www.googleapis.com/auth/business.manage"]
TOKEN_PATH = os.path.join(ROOT, "token.pickle")
CLIENT_SECRETS_DEFAULT = os.path.join(ROOT, "client_secrets.json")


def _find_client_secrets():
    """Use client_secrets.json or any downloaded client_secret_*.apps.googleusercontent.com.json in project root."""
    if os.path.exists(CLIENT_SECRETS_DEFAULT):
        return CLIENT_SECRETS_DEFAULT
    pattern = os.path.join(ROOT, "client_secret_*.apps.googleusercontent.com.json")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    return None


def main():
    client_secrets = _find_client_secrets()
    if not client_secrets:
        print("Missing OAuth client JSON — the script cannot open the browser until this file exists.\n")
        print("Put your OAuth client JSON in this project folder (exact path):")
        print(f"  {ROOT}\n")
        print("Accepted filenames:")
        print("  - client_secrets.json")
        print("  - client_secret_XXXXX.apps.googleusercontent.com.json  (as downloaded from Google)\n")
        print("How to get it:")
        print("  1. Open: https://console.cloud.google.com/apis/credentials")
        print("  2. Create OAuth 2.0 Client ID → Application type: Desktop app")
        print("  3. Download the JSON and put it in this folder (rename optional)")
        print("  4. Enable APIs: My Business Account Management, Business Information, Business Profile Performance, My Business Reviews")
        print("\nThen run again:  python gbp_oauth_login.py")
        return 1

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Install: pip install google-auth-oauthlib")
        return 1

    print("GBP OAuth login — this will open your browser.\n")
    print("  1. A browser window will open to Google sign-in.")
    print("  2. Sign in with: tenacioustapesmedia@gmail.com (or the account that owns your Business Profile).")
    print("  3. Click Allow so the app can read your Business Profile.")
    print("  4. The script will then save credentials to token.pickle automatically.\n")
    try:
        input("Press Enter to open the browser... ")
    except (EOFError, KeyboardInterrupt):
        print("Cancelled.")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes=SCOPES)
    # run_local_server starts a local HTTP server and opens the browser to the auth URL
    creds = flow.run_local_server(port=0, open_browser=True)

    with open(TOKEN_PATH, "wb") as f:
        pickle.dump(creds, f)
    print(f"\nDone. Credentials saved to: {TOKEN_PATH}")
    print("Restart the dashboard (python run_vercel_local.py); Business Profile will use this token.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
