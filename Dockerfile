# ── Stage 1: Build React frontend ─────────────────────────────────────────
FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build


# ── Stage 2: Python runtime ──────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Install system deps for Playwright (chromium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 libxshmfence1 \
    fonts-liberation wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy source code
COPY agent/ agent/
COPY pyproject.toml .

# Copy built frontend from stage 1
COPY --from=frontend /app/dist dist/

# Create reports directory
RUN mkdir -p reports

# Railway sets PORT env var
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn agent.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
