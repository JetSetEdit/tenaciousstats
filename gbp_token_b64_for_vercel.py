#!/usr/bin/env python3
"""
Print base64(token.pickle) for Vercel env GOOGLE_OAUTH_TOKEN_B64.

1. Refresh credentials:  python gbp_oauth_login.py
2. Run this script, copy the one-line output
3. Vercel → Project → Settings → Environment Variables → GOOGLE_OAUTH_TOKEN_B64
4. Redeploy
"""

import base64
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(ROOT, "token.pickle")


def main():
    if not os.path.isfile(TOKEN_PATH):
        print("No token.pickle found. Run first:  python gbp_oauth_login.py", file=sys.stderr)
        return 1
    with open(TOKEN_PATH, "rb") as f:
        raw = f.read()
    if not raw:
        print("token.pickle is empty.", file=sys.stderr)
        return 1
    print(base64.b64encode(raw).decode("ascii"))
    print(
        "\nPaste the line above into Vercel → GOOGLE_OAUTH_TOKEN_B64, then redeploy.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
