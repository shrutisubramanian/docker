# ── Frontend Dockerfile ───────────────────────────────────────────────
FROM node:20-alpine

LABEL maintainer="Member1 — Container Deployment & Failure Simulation"

WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json ./
RUN npm install --production

# Copy application code
COPY . .

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
