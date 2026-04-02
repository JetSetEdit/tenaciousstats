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

    _data_dir = os.path.join(public_path, "data")
    if os.path.exists(_data_dir):
        @app.get("/data/email_campaigns.json", response_class=FileResponse)
        def serve_email_campaigns():
            return FileResponse(os.path.join(_data_dir, "email_campaigns.json"))

    # Do NOT mount StaticFiles at "/" — it would shadow /api/* and cause 404s for analytics.
    print(f"Serving static files from {public_path} (/, /version.txt, /keyterms.json, /data/email_campaigns.json)")
else:
    print(f"Warning: 'public' directory not found at {public_path}")

def _open_browser(port: int):
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    base = f"http://localhost:{port}"
    print(f"Starting Vercel-like local server on {base}")
    print(f"Dashboard: {base}/   API: {base}/api")
    if not os.environ.get("DOCKER"):
        print("Serves the full dashboard (styled UI, glossary, API). Opening browser...")
        threading.Thread(target=_open_browser, args=(port,), daemon=True).start()
    uvicorn.run(
        "run_vercel_local:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[_project_root],
    )
