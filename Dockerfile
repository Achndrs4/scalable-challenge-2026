FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app
COPY pyproject.toml .
RUN uv pip install --system --no-cache .
COPY . .
