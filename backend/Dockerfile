FROM python:3.14-slim AS builder
WORKDIR /app

# Install system dependencies (needed for any native packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make pkg-config libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the uv config files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14-slim AS production
WORKDIR /app

# Create non‑root user
RUN addgroup --system app && adduser --system --group app

# Copy installed Python packages from builder
COPY --from=builder --chown=app:app /app/.venv /home/app/.venv

# Copy application code
COPY --chown=app:app . .

ENV PATH=/home/app/.venv/bin:$PATH
ENV HOME=/home/app
USER app

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]