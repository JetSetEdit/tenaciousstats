import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# The scope for GBP API
SCOPES = ["https://www.googleapis.com/auth/business.manage"]

# The file you just uploaded
CLIENT_SECRETS_FILE = "client_secret_422791924330-vct94ddsips3n0d99ceafm5sc2v6m7pl.apps.googleusercontent.com.json"
TOKEN_FILE = 'token.pickle'

def get_refresh_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    
    # This will open a browser window for you to sign in
    # Make sure to sign in with the Google Account that owns the Business Profile
    creds = flow.run_local_server(port=0)

    print("\n--- AUTH SUCCESSFUL ---")
    print(f"Refresh Token: {creds.refresh_token}")
    
    # Save the credentials for later use
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)
    print(f"Credentials saved to {TOKEN_FILE}")

if __name__ == '__main__':
    get_refresh_token()
