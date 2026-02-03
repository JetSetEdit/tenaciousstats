"""
Run the downloaded Vercel deployment locally.
Uses the main Tenacious Stats API (from parent repo) and serves this download's public/ (frontend).
"""
import os
import sys
import webbrowser
import threading
import time

# This folder is vercel-deployment-download; project root is parent.
DOWNLOAD_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(DOWNLOAD_ROOT, "src")
MAIN_PROJECT = os.path.dirname(DOWNLOAD_ROOT)

# Use main project's API (FastAPI)
sys.path.insert(0, MAIN_PROJECT)
os.chdir(MAIN_PROJECT)

import uvicorn
from fastapi.staticfiles import StaticFiles
from api.index import app

# Serve THIS download's public folder (deployed frontend)
public_path = os.path.join(SRC, "public")
if not os.path.exists(public_path):
    print(f"Error: {public_path} not found")
    sys.exit(1)

# Remove root route from API so static files serve /
for route in list(app.routes):
    if hasattr(route, "path") and route.path == "/":
        app.routes.remove(route)

app.mount("/", StaticFiles(directory=public_path, html=True), name="public")
print(f"Serving frontend from: {public_path}")
print("API from main project:", MAIN_PROJECT)


def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8001")


if __name__ == "__main__":
    print("Vercel deployment download – dev server at http://localhost:8001")
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8001)
