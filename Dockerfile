FROM node:22-alpine AS base
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm db:generate
RUN pnpm build
RUN pnpm prune --prod

FROM node:22-alpine AS runner
WORKDIR /app
RUN addgroup -S skywizz && adduser -S skywizz -G skywizz
COPY --from=builder --chown=skywizz:skywizz /app/dist ./dist
COPY --from=builder --chown=skywizz:skywizz /app/node_modules ./node_modules
COPY --from=builder --chown=skywizz:skywizz /app/package.json ./package.json
USER skywizz
CMD ["node", "dist/index.js"]
