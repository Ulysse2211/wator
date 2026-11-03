FROM node:26-alpine AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
COPY nuxt.config.ts tsconfig.json ./
COPY app ./app
COPY public ./public
RUN npm ci && npm run generate

FROM python:3.14-alpine AS backend
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.14-alpine AS runtime
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN adduser -D -u 10001 app
COPY --from=backend /app/.venv ./.venv
COPY main.py ./main.py
COPY --from=frontend /app/.output/public ./static
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
