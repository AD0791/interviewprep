# Multi-Stage Build using UV package manager
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy config files
COPY pyproject.toml ./

# Mount cache for faster rebuilds, install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --no-cache -r requirements.txt

# Final runner stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
