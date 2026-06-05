FROM node:24-alpine AS base
RUN corepack enable

# ── All dependencies (dev + prod) ────────────────────────
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# ── Production-only dependencies ─────────────────────────
# Separate stage so code changes don't bust this cache layer
FROM base AS prod-deps
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --prod

# ── Dev (watch mode) ──────────────────────────────────────
FROM base AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm db:generate

# ── Build ─────────────────────────────────────────────────
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm db:generate
RUN pnpm build

# ── Bot (Discord client) ──────────────────────────────────
FROM gcr.io/distroless/nodejs24-debian12:nonroot AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder   --chown=65532:65532 /app/dist        ./dist
COPY --from=prod-deps --chown=65532:65532 /app/node_modules ./node_modules
COPY --from=builder   --chown=65532:65532 /app/package.json ./package.json
COPY --from=builder   --chown=65532:65532 /app/prisma       ./prisma
COPY --from=builder   --chown=65532:65532 /app/prisma.config.ts ./prisma.config.ts
CMD ["dist/start.js"]

# ── API (HTTP server + bot-migrate via CMD override) ──────
FROM gcr.io/distroless/nodejs24-debian12:nonroot AS api
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder   --chown=65532:65532 /app/dist        ./dist
COPY --from=prod-deps --chown=65532:65532 /app/node_modules ./node_modules
COPY --from=builder   --chown=65532:65532 /app/package.json ./package.json
COPY --from=builder   --chown=65532:65532 /app/prisma       ./prisma
COPY --from=builder   --chown=65532:65532 /app/prisma.config.ts ./prisma.config.ts
EXPOSE 3002
CMD ["dist/api/main.js"]
