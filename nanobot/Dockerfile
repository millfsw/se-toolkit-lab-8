# Multi-stage build for nanobot gateway
# Build context: ./nanobot

# ---- Build stage ----
FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS builder

WORKDIR /app

# Copy root workspace files
COPY ../pyproject.toml ../uv.lock* ./

# Copy nanobot project
COPY pyproject.toml entrypoint.py config.json ./nanobot/

# Copy workspace members that nanobot needs
COPY ../mcp ./mcp
COPY ../nanobot-websocket-channel/nanobot-webchat ./nanobot-websocket-channel/nanobot-webchat
COPY ../nanobot-websocket-channel/nanobot-channel-protocol ./nanobot-websocket-channel/nanobot-channel-protocol

# Copy nanobot workspace
COPY workspace ./nanobot/workspace

# Install all workspace dependencies
RUN uv sync --no-dev

# ---- Runtime stage ----
FROM python:3.14-slim-bookworm

WORKDIR /app/nanobot

# Install uv for runtime
COPY --from=builder /uv /bin/uv

# Copy installed packages from builder (includes all workspace members)
COPY --from=builder /app/.venv /app/.venv

# Copy application files
COPY config.json entrypoint.py ./
COPY workspace ./workspace

# Set PATH to include uv and venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run the entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
