# Docker Setup - Complete Containerized Development

## Prerequisites

1. **Docker Desktop** must be installed and running
   - Check system tray for Docker icon (whale)
   - Wait until it shows "Docker Desktop is running"

2. **credentials.json** file in project root
   - Required for Google Analytics API access

## Quick Start

### Start the app (dashboard + API in one container)

```bash
docker-compose -f docker-compose.dev.yml up
```

Or use npm (if defined in package.json):
```bash
npm run docker:up
```

This will:
- Build the container with all dependencies
- Run the unified app (same as `run_vercel_local.py`) on http://localhost:8000
- Serve the dashboard at `/` and the API at `/api`
- Watch for code changes via volume mounts (hot reload)

### Access the application

- **Dashboard:** http://localhost:8000
- **API:** http://localhost:8000/api
- **Health check:** http://localhost:8000/api/health

## Useful Commands

### Start in Background (Detached Mode)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### View Logs
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

### View app logs only
```bash
docker-compose -f docker-compose.dev.yml logs -f app
```

### Stop Everything
```bash
docker-compose -f docker-compose.dev.yml down
```

### Rebuild After Changes
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Restart the app
```bash
docker-compose -f docker-compose.dev.yml restart app
```

## Troubleshooting

### Docker Desktop Not Running
- Start Docker Desktop from Start Menu
- Wait for the whale icon in system tray to be steady (not animating)

### Port already in use
- Stop any existing service on port 8000
- Or change the host port in `docker-compose.dev.yml` (e.g. `"8001:8000"`)

### Credentials Error
- Ensure `credentials.json` exists in project root
- Check file permissions

### Rebuild Everything
```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

## Development Workflow

1. Start Docker Desktop
2. Run `docker-compose -f docker-compose.dev.yml up`
3. Make code changes (hot reload enabled)
4. View logs if needed: `docker-compose -f docker-compose.dev.yml logs -f`
5. Stop when done: `docker-compose -f docker-compose.dev.yml down`

## What's in the container

- **Unified app:** FastAPI serves both the dashboard (HTML at `/`) and the API at `/api` (same as `run_vercel_local.py`)
- **Isolated:** No need to install Python packages on the host
- **Consistent:** Same environment for all developers








