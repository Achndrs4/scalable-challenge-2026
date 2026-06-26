FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
