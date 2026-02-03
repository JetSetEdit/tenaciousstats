import os
import sys
import webbrowser
import threading
import time

# Ensure project root is on path and CWD so api/index.py and utils (ga4_utils) resolve
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
os.chdir(_project_root)

import uvicorn
from fastapi.responses import FileResponse
from api.index import app

# Serve static files without shadowing /api. Use explicit routes for root and key files,
# then mount static under a path that won't catch /api requests.
public_path = os.path.join(os.path.dirname(__file__), "public")

# Remove the existing root route ("/") from the API so we can serve index.html at "/"
for route in list(app.routes):
    if hasattr(route, "path") and route.path == "/":
        app.routes.remove(route)

if os.path.exists(public_path):
    # Serve index.html and key static files explicitly so /api/* is never handled by static
    @app.get("/", response_class=FileResponse)
    def serve_index():
        return FileResponse(os.path.join(public_path, "index.html"))

    @app.get("/version.txt", response_class=FileResponse)
    def serve_version():
        return FileResponse(os.path.join(public_path, "version.txt"))

    @app.get("/keyterms.json", response_class=FileResponse)
    def serve_keyterms():
        return FileResponse(os.path.join(public_path, "keyterms.json"))

    # Do NOT mount StaticFiles at "/" — it would shadow /api/* and cause 404s for analytics.
    print(f"Serving static files from {public_path} (/, /version.txt, /keyterms.json)")
else:
    print(f"Warning: 'public' directory not found at {public_path}")

def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    print("Starting Vercel-like local server on http://localhost:8000")
    print("Dashboard: http://localhost:8000/   API: http://localhost:8000/api")
    if not os.environ.get("DOCKER"):
        print("Serves the full dashboard (styled UI, glossary, API). Opening browser...")
        threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
