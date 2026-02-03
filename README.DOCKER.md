# Docker Setup

Run the full Tenacious Stats app (dashboard + API) in one container. Same behavior as `python run_vercel_local.py` locally.

## Prerequisites

- Docker and Docker Compose installed
- `credentials.json` in the project root (for GA4; app still runs without it and returns “GA4 not available”)

## Quick start

```bash
docker-compose -f docker-compose.dev.yml up
```

Then open:

- **Dashboard:** http://localhost:8000  
- **API:** http://localhost:8000/api  
- **Health:** http://localhost:8000/api/health  

One service serves both the HTML dashboard and the `/api` endpoints, so the frontend and API use the same origin and the 404-on-API issue is avoided.

## Rebuild after code changes

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## Stop

```bash
docker-compose -f docker-compose.dev.yml down
```

## Logs

```bash
docker-compose -f docker-compose.dev.yml logs -f
```

## Production-style (no volume mounts)

```bash
docker-compose up --build
```

Uses `docker-compose.yml` (no live-reload; copies code at build time). Dashboard and API are still at http://localhost:8000 and http://localhost:8000/api.








