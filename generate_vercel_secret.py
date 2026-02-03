import pickle
import base64
import os

TOKEN_PICKLE = 'token.pickle'

def generate_secret():
    if not os.path.exists(TOKEN_PICKLE):
        print("Error: token.pickle not found. Please run get_refresh_token.py first.")
        return

    try:
        with open(TOKEN_PICKLE, 'rb') as token:
            token_content = token.read()
            
        # Encode to Base64
        secret_b64 = base64.b64encode(token_content).decode('utf-8')
        
        print("\n=== VERCEL SECRET VALUE (COPY THE LINE BELOW) ===")
        print(secret_b64)
        print("=================================================")
        print("\nInstructions:")
        print("1. Copy the long string above.")
        print("2. Go to Vercel Project Settings > Environment Variables.")
        print("3. Add a new variable:")
        print("   Key: GOOGLE_OAUTH_TOKEN_B64")
        print("   Value: [Paste the string]")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_secret()
