# Fix Business Profile (when it used to work)

Business Profile stops working when the **OAuth token expires**. The app then uses a fallback credential (service account) that has no Business Profile locations.

**If you already ran `gbp_oauth_login.py` and it still says "no locations":**  
The account you signed in with (e.g. tenacioustapesmedia@gmail.com) has **no Business Profile location** linked in Google’s API. Check: open [business.google.com](https://business.google.com), sign in with **that same account**, and confirm you see your business and its location. If you don’t, either add/claim the business with that account, or run `gbp_oauth_login.py` again and sign in with the Google account that **already owns** the profile.

## Fix in 3 steps

### 1. Refresh the OAuth token (local)

From the project root:

```powershell
python gbp_oauth_login.py
```

- A browser will open. **Sign in with the Google account that OWNS the Business Profile** (e.g. **tenacioustapesmedia@gmail.com**).
- The script saves a new `token.pickle`. You only need to do this again when the token expires (every few weeks/months).

**If you see "Missing OAuth client JSON":**  
Put `client_secrets.json` in the project root. Get it from [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials): create an **OAuth 2.0 Client ID** (Desktop app), download the JSON, and save it as `client_secrets.json` in this folder.

### 2. Restart the dashboard

Stop the current server (Ctrl+C in the terminal where it’s running), then start it again:

```powershell
python run_vercel_local.py
```

This makes the app use the new `token.pickle` and the `/api/gbp/ratings` route.

### 3. Verify

```powershell
python check_google_auth.py
```

You should see: **`[GBP] OK - GBP OK (1 account(s), N location(s))`**

Then open http://localhost:8000, tick **Business Profile**, and click **Refresh Data**. Ratings, reviews, and insights should load.

---

## Fix on Vercel (production)

If the live dashboard at tenacious-stats-dashboard.vercel.app loses Business Profile:

1. Run `python gbp_oauth_login.py` locally and sign in with the business owner account (as above).
2. Encode the new token and set it in Vercel:
   - Create the base64 token (e.g. run a small script that reads `token.pickle`, base64-encodes it, and prints the string).
   - In Vercel: Project → Settings → Environment Variables → set **`GOOGLE_OAUTH_TOKEN_B64`** to that value.
3. Redeploy (or wait for the next deploy).

Once the new token is in `GOOGLE_OAUTH_TOKEN_B64`, production will use it and Business Profile will work again.
