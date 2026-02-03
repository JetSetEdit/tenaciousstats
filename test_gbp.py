import sys
import os
from googleapiclient.discovery import build

# Add api directory to path
sys.path.append(os.path.join(os.getcwd(), 'api'))

import gbp

def debug_gbp():
    print("Debugging GBP Integration...")
    creds = gbp.get_creds()
    
    try:
        print("\n--- Account Management API ---")
        service = build('mybusinessaccountmanagement', 'v1', credentials=creds)
        print(f"Service: {service}")
        
        if hasattr(service, 'accounts'):
            accounts_resource = service.accounts()
            print(f"Accounts Resource: {accounts_resource}")
            print(f"Dir(accounts): {dir(accounts_resource)}")
            
            if hasattr(accounts_resource, 'list'):
                print("SUCCESS: accounts.list() exists!")
                accounts = accounts_resource.list().execute()
                print(f"Accounts: {accounts}")
            else:
                print("FAIL: accounts.list() does NOT exist.")
        else:
            print("Service has no 'accounts' attribute.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_gbp()
