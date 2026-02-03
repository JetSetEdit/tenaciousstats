FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY api/requirements.txt ./api/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r api/requirements.txt

# Copy application code (api/, public/, utils/, run_vercel_local.py, etc.)
COPY . .

# Expose port (dashboard + API on same port)
EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DOCKER=1

# Run unified app: dashboard at / and API at /api (same as run_vercel_local.py)
CMD ["python", "run_vercel_local.py"]
