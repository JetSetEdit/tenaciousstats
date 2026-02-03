# Google Business Profile API – Handover Document

**Purpose:** Automate posting new blog articles from the Tenacious Tapes website (RSS feed) to Google Business Profile (GBP).

**Last updated:** January 2025

---

## 1. What was completed

### 1.1 RSS feed

- **Chosen feed:** `https://www.tenacioustapes.com.au/feed/` (WordPress main feed).
- The page `https://www.tenacioustapes.com.au/on-a-roll/` is the blog listing; the **feed** for posts is `/feed/`.
- Optional “pretty” feed for browsers: XSLT stylesheet and must-use plugin were created (see **Files** below). These are optional and can be removed if not needed.

### 1.2 API approach

- **Decision:** Use **OAuth 2.0** (user login), not a service account.
- **Reason:** The existing service account invite for GBP was stuck (“Awaiting response”) because service accounts cannot accept email invites. Google’s Business Profile API posting flow is built around OAuth 2.0 for user-authorized access.
- **Flow:** One-time OAuth login → save **refresh token** → script uses refresh token to get **access tokens** and call the API. No ongoing “invite” or email acceptance.

### 1.3 Google Cloud project

- **Project:** **Tenacious Tapes Videos** (`tenacious-tapes-videos`).
- This project already had Business Profile–related APIs enabled and is the one allowlisted for GBP API access.
- **Credentials page:** [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials?project=tenacious-tapes-videos)

### 1.4 OAuth client (Desktop app)

- A **Desktop app** OAuth 2.0 client was created in **Tenacious Tapes Videos** for the RSS → GBP script.
- **Client ID:** `422791924330-vct94ddsips3n0d99ceafm5sc2v6m7pl.apps.googleusercontent.com`
- **Client secret:** Stored in the JSON file in this project (see **Files**). **Do not commit or share this file.**

### 1.5 OAuth consent screen – Test users

- **Audience** (OAuth consent screen) was configured: [Google Auth Platform → Audience](https://console.cloud.google.com/apis/credentials/consent?project=tenacious-tapes-videos) (or: Credentials → OAuth consent screen → Audience).
- The Google account that manages the Tenacious Tapes Business Profile was added as a **Test user** so it can sign in during the one-time OAuth flow.

### 1.6 One-time OAuth login (refresh token) – in progress

- **Step 3** from the setup guide was started: use the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground) to get a **refresh token**.
- **Steps:** Use your own OAuth credentials (Client ID + Client secret), add scope `https://www.googleapis.com/auth/business.manage`, click “Authorize APIs”, sign in with the test user, then “Exchange authorization code for tokens”.
- **If redirect error:** Add `https://developers.google.com/oauthplayground` as an authorized redirect URI for the Desktop OAuth client in the Google Cloud Console.
- **Outcome needed:** Copy the **Refresh token** from the Playground response and store it securely (env var or config the script will read). This token is used by the automation; no repeat login needed unless the token is revoked.

---

## 2. What remains to do

1. **Finish Step 3:** Complete the OAuth Playground flow and save the **refresh token** somewhere secure (e.g. `.env` or a config file excluded from version control).
2. **Step 4 – Build the script:** A script (e.g. PHP or other) that:
   - Reads **Client ID**, **Client secret**, and **Refresh token** from config/env.
   - Uses the refresh token to obtain an **access token** (OAuth2 token endpoint).
   - Fetches the RSS feed, detects new posts, and creates **local posts** on the Business Profile via the Business Profile API.
   - Can be run on a schedule (cron, task scheduler, or similar).

The detailed “start from scratch” steps are in **`GBP-RSS-START-FROM-SCRATCH.md`** in this folder.

---

## 3. Key links

| What | URL |
|------|-----|
| Google Cloud – Tenacious Tapes Videos | [console.cloud.google.com](https://console.cloud.google.com?project=tenacious-tapes-videos) |
| Credentials (OAuth client) | [Credentials](https://console.cloud.google.com/apis/credentials?project=tenacious-tapes-videos) |
| OAuth consent / Audience (test users) | [Consent / Audience](https://console.cloud.google.com/apis/credentials/consent?project=tenacious-tapes-videos) |
| OAuth 2.0 Playground (get refresh token) | [developers.google.com/oauthplayground](https://developers.google.com/oauthplayground) |
| WordPress RSS feed (production) | `https://www.tenacioustapes.com.au/feed/` |

---

## 4. Files in this project

| File | Purpose |
|------|--------|
| `client_secret_422791924330-...apps.googleusercontent.com.json` | OAuth Desktop client credentials (Client ID + Client secret). **Keep private; do not commit to Git.** |
| `00_new_tenacious/GBP-RSS-START-FROM-SCRATCH.md` | Step-by-step OAuth and script outline. |
| `00_new_tenacious/GBP-API-HANDOVER.md` | This handover document. |

Optional “pretty” feed (if used on live site):

- `yryaeab/public_html/wp-content/pretty-feed.xsl`
- `yryaeab/public_html/wp-content/mu-plugins/pretty-feed.php`

---

## 5. Security and good practice

- **Client secret** and **refresh token** must not be committed to version control. Add the client secret JSON file (and any config containing the refresh token) to `.gitignore`.
- If the client secret or refresh token is ever exposed, revoke/regenerate in Google Cloud Console and re-run the one-time OAuth flow to get a new refresh token.
- Store the refresh token in environment variables or a config file that is only on the machine/server running the script and is not in the repo.

---

## 6. Summary table

| Item | Status |
|------|--------|
| RSS feed URL chosen | Done – `https://www.tenacioustapes.com.au/feed/` |
| API method chosen | Done – OAuth 2.0 (not service account) |
| Google Cloud project | Done – Tenacious Tapes Videos |
| Desktop OAuth client | Done – Client ID + secret in JSON file |
| Test user on consent screen | Done – added in Audience |
| Refresh token | In progress – complete via OAuth Playground |
| RSS → GBP posting script | Not started – Step 4 |
