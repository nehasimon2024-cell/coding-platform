FROM python:3.14-slim AS builder
WORKDIR /app

# Install system dependencies (needed for any native packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make pkg-config libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.14-slim AS production
WORKDIR /app

# Create non‑root user
RUN addgroup --system app && adduser --system --group app

# Copy installed Python packages from builder
COPY --from=builder --chown=app:app /root/.local /home/app/.local

# Copy application code
COPY --chown=app:app . .

ENV PATH=/home/app/.local/bin:$PATH
ENV HOME=/home/app
USER app

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]