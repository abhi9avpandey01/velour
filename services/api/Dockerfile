# ──────────────────────────────────────────────────────────────
# Velour API — Dockerfile (multi-stage)
# ──────────────────────────────────────────────────────────────

# ── Base stage ──────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.4
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy dependency files first (better layer caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no dev deps in production base)
RUN poetry config virtualenvs.create false

# ── Development ─────────────────────────────────
FROM base AS development

# Install all dependencies including dev
RUN poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production ──────────────────────────────────
FROM base AS production

# Install only production dependencies
RUN poetry install --no-interaction --no-ansi --only main

# Copy application code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
