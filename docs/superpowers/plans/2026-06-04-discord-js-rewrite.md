# SkyWizz Bot — discord.js Rewrite (Bare Bones)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the SkyWizz Discord bot from Python to TypeScript using discord.js v14, with three commands: `/uptime`, `/server`, `/config`. Guild config persisted in Postgres via Prisma.

**Architecture:** Single Node.js service. Commands are individual files registered via a command handler at startup. Prisma manages a minimal schema (Guild + GuildConfig). docker-compose exposes the bot and a local Postgres for dev.

**Tech Stack:** discord.js 14, TypeScript 5, Prisma 6, Node 22 (Alpine), tsx (dev), pnpm

---

## Repo changes on this branch

All Python source files (`SkyWizz.py`, `skywizz/`, `requirements.txt`, `pyproject.toml`, `poetry.lock`, `skywizz.db`) are removed. The Dockerfile, docker-compose files, and GitHub Actions workflows are replaced. The mkdocs folder is removed. New source lives in `src/`.

## File Map

```
SkyWizz/
├── src/
│   ├── index.ts                  # entry: load env, init client, register commands, login
│   ├── client.ts                 # create and export the Discord Client singleton
│   ├── deploy-commands.ts        # one-shot script: POST slash commands to Discord API
│   ├── commands/
│   │   ├── index.ts              # load all commands from this directory, export map
│   │   ├── uptime.ts             # /uptime command
│   │   ├── server.ts             # /server command
│   │   └── config.ts             # /config command (show + set prefix/timezone)
│   └── db/
│       ├── client.ts             # Prisma client singleton
│       └── guild.ts              # upsertGuild, getConfig, setConfig helpers
├── prisma/
│   └── schema.prisma
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml            # local dev: bot + postgres
├── docker-compose.prod.yml       # prod: bot only, joins external skywizz-data network
└── .github/
    └── workflows/
        └── deploy.yml            # build → Harbor → Portainer update (keep existing pattern)
```

---

### Task 1: Remove Python artifacts and scaffold TypeScript project

**Files:**
- Delete: `SkyWizz.py`, `skywizz/`, `requirements.txt`, `pyproject.toml`, `poetry.lock`, `skywizz.db`, `mkdocs/`
- Create: `package.json`, `tsconfig.json`, `.env.example`, `.gitignore`, `src/index.ts` (stub)

- [ ] **Step 1: Remove Python artifacts**

```bash
git rm -r SkyWizz.py skywizz/ requirements.txt pyproject.toml poetry.lock mkdocs/
rm -f skywizz.db
```

- [ ] **Step 2: Create `package.json`**

```json
{
  "name": "skywizz",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "deploy-commands": "tsx src/deploy-commands.ts",
    "db:generate": "prisma generate",
    "db:push": "prisma db push",
    "db:migrate": "prisma migrate deploy"
  },
  "dependencies": {
    "@prisma/client": "^6.0.0",
    "discord.js": "^14.16.0",
    "dotenv": "^16.4.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "prisma": "^6.0.0",
    "tsx": "^4.19.0",
    "typescript": "^5.7.0"
  }
}
```

- [ ] **Step 3: Create `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 4: Create `.gitignore`**

```gitignore
node_modules/
dist/
.env
*.db
.next/
.prisma/
```

- [ ] **Step 5: Create `.env.example`**

```
# Discord application credentials — https://discord.com/developers/applications
BOT_TOKEN=your_bot_token_here
CLIENT_ID=your_application_client_id
GUILD_ID=your_dev_guild_id_for_local_command_registration

# PostgreSQL
DATABASE_URL=postgresql://skywizz:password@localhost:5432/skywizz

# Runtime
NODE_ENV=development
LOG_LEVEL=info
TIMEZONE=UTC
```

- [ ] **Step 6: Create stub `src/index.ts` so the repo compiles**

```typescript
import "dotenv/config";

console.log("SkyWizz starting...");
```

- [ ] **Step 7: Install dependencies**

```bash
pnpm install
```

Expected: `node_modules/` populated, `pnpm-lock.yaml` created.

- [ ] **Step 8: Commit**

```bash
git add package.json tsconfig.json .gitignore .env.example src/index.ts pnpm-lock.yaml
git commit -m "chore: replace Python scaffold with TypeScript / discord.js"
```

---

### Task 2: Prisma schema

**Files:**
- Create: `prisma/schema.prisma`

- [ ] **Step 1: Create `prisma/schema.prisma`**

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Guild {
  id       String      @id
  name     String
  joinedAt DateTime    @default(now())
  leftAt   DateTime?
  config   GuildConfig?
}

model GuildConfig {
  guildId   String   @id
  prefix    String   @default("!")
  timezone  String   @default("UTC")
  updatedAt DateTime @updatedAt

  guild Guild @relation(fields: [guildId], references: [id], onDelete: Cascade)
}
```

- [ ] **Step 2: Start local Postgres and push schema**

Start Postgres (docker-compose is wired in Task 6 — for now run a quick one-liner):

```bash
docker run -d --name skywizz-dev-pg \
  -e POSTGRES_USER=skywizz \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=skywizz \
  -p 5432:5432 postgres:17-alpine
```

Copy `.env.example` to `.env` and set `DATABASE_URL=postgresql://skywizz:password@localhost:5432/skywizz`.

```bash
pnpm db:generate
pnpm db:push
```

Expected: `Prisma schema loaded ... Your database is now in sync with your Prisma schema.`

- [ ] **Step 3: Commit**

```bash
git add prisma/schema.prisma
git commit -m "feat: add Prisma schema with Guild and GuildConfig models"
```

---

### Task 3: Prisma client + DB helpers

**Files:**
- Create: `src/db/client.ts`, `src/db/guild.ts`

- [ ] **Step 1: Create `src/db/client.ts`**

```typescript
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ?? new PrismaClient({ log: ["warn", "error"] });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
```

- [ ] **Step 2: Create `src/db/guild.ts`**

```typescript
import type { Guild, GuildConfig } from "@prisma/client";
import { prisma } from "./client.js";

export async function upsertGuild(id: string, name: string): Promise<Guild> {
  return prisma.guild.upsert({
    where: { id },
    update: { name, leftAt: null },
    create: { id, name },
  });
}

export async function markGuildLeft(id: string): Promise<void> {
  await prisma.guild.update({
    where: { id },
    data: { leftAt: new Date() },
  });
}

export async function getConfig(
  guildId: string
): Promise<GuildConfig | null> {
  return prisma.guildConfig.findUnique({ where: { guildId } });
}

export async function setConfig(
  guildId: string,
  data: Partial<Pick<GuildConfig, "prefix" | "timezone">>
): Promise<GuildConfig> {
  return prisma.guildConfig.upsert({
    where: { guildId },
    update: data,
    create: { guildId, ...data },
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/db/
git commit -m "feat: add Prisma client singleton and guild DB helpers"
```

---

### Task 4: Discord client + command handler skeleton

**Files:**
- Create: `src/client.ts`, `src/commands/index.ts`, `src/commands/uptime.ts` (stub)

- [ ] **Step 1: Create `src/client.ts`**

```typescript
import { Client, GatewayIntentBits, Partials } from "discord.js";

export const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
  ],
  partials: [Partials.Channel],
});
```

- [ ] **Step 2: Create command interface type in `src/commands/index.ts`**

```typescript
import {
  type ChatInputCommandInteraction,
  type SlashCommandBuilder,
  Collection,
} from "discord.js";
import { uptime } from "./uptime.js";
import { server } from "./server.js";
import { config } from "./config.js";

export interface Command {
  data: SlashCommandBuilder | ReturnType<SlashCommandBuilder["setName"]>;
  execute: (interaction: ChatInputCommandInteraction) => Promise<void>;
}

export const commands = new Collection<string, Command>([
  [uptime.data.name, uptime],
  [server.data.name, server],
  [config.data.name, config],
]);
```

- [ ] **Step 3: Create stub `src/commands/uptime.ts` so it compiles**

```typescript
import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const uptime: Command = {
  data: new SlashCommandBuilder()
    .setName("uptime")
    .setDescription("Show how long the bot has been running"),
  async execute(interaction) {
    await interaction.reply("uptime stub");
  },
};
```

- [ ] **Step 4: Create stub `src/commands/server.ts`**

```typescript
import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const server: Command = {
  data: new SlashCommandBuilder()
    .setName("server")
    .setDescription("Show information about this server"),
  async execute(interaction) {
    await interaction.reply("server stub");
  },
};
```

- [ ] **Step 5: Create stub `src/commands/config.ts`**

```typescript
import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const config: Command = {
  data: new SlashCommandBuilder()
    .setName("config")
    .setDescription("View or update server configuration"),
  async execute(interaction) {
    await interaction.reply("config stub");
  },
};
```

- [ ] **Step 6: Wire up `src/index.ts`**

```typescript
import "dotenv/config";
import { Events } from "discord.js";
import { client } from "./client.js";
import { commands } from "./commands/index.js";
import { prisma } from "./db/client.js";
import { upsertGuild, markGuildLeft } from "./db/guild.js";

const startedAt = new Date();
export { startedAt };

client.once(Events.ClientReady, (c) => {
  console.log(`Logged in as ${c.user.tag}`);
});

client.on(Events.GuildCreate, (guild) => {
  upsertGuild(guild.id, guild.name).catch(console.error);
});

client.on(Events.GuildDelete, (guild) => {
  markGuildLeft(guild.id).catch(console.error);
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = commands.get(interaction.commandName);
  if (!command) return;

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    const msg = { content: "Something went wrong.", ephemeral: true };
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp(msg);
    } else {
      await interaction.reply(msg);
    }
  }
});

async function main() {
  await client.login(process.env.BOT_TOKEN);
}

main().catch(async (error) => {
  console.error(error);
  await prisma.$disconnect();
  process.exit(1);
});
```

- [ ] **Step 7: Verify it compiles**

```bash
pnpm build
```

Expected: `dist/` directory created, no TypeScript errors.

- [ ] **Step 8: Commit**

```bash
git add src/
git commit -m "feat: wire discord.js client, command handler skeleton, and entry point"
```

---

### Task 5: `/uptime` command

**Files:**
- Modify: `src/commands/uptime.ts`

- [ ] **Step 1: Implement `src/commands/uptime.ts`**

```typescript
import { EmbedBuilder, SlashCommandBuilder, time, TimestampStyles } from "discord.js";
import type { Command } from "./index.js";
import { startedAt } from "../index.js";

function formatDuration(ms: number): string {
  const s = Math.floor(ms / 1000);
  const days = Math.floor(s / 86400);
  const hours = Math.floor((s % 86400) / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  const seconds = s % 60;

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);
  return parts.join(" ");
}

export const uptime: Command = {
  data: new SlashCommandBuilder()
    .setName("uptime")
    .setDescription("Show how long the bot has been running"),

  async execute(interaction) {
    const now = new Date();
    const ms = now.getTime() - startedAt.getTime();

    const embed = new EmbedBuilder()
      .setTitle("Uptime")
      .setColor(0x5865f2)
      .addFields(
        { name: "Running for", value: formatDuration(ms), inline: true },
        {
          name: "Started",
          value: time(startedAt, TimestampStyles.RelativeTime),
          inline: true,
        }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [embed] });
  },
};
```

- [ ] **Step 2: Build and verify no errors**

```bash
pnpm build
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/commands/uptime.ts
git commit -m "feat: implement /uptime command"
```

---

### Task 6: `/server` command

**Files:**
- Modify: `src/commands/server.ts`

- [ ] **Step 1: Implement `src/commands/server.ts`**

```typescript
import {
  EmbedBuilder,
  SlashCommandBuilder,
  time,
  TimestampStyles,
} from "discord.js";
import type { Command } from "./index.js";

export const server: Command = {
  data: new SlashCommandBuilder()
    .setName("server")
    .setDescription("Show information about this server"),

  async execute(interaction) {
    if (!interaction.guild) {
      await interaction.reply({ content: "This command can only be used in a server.", ephemeral: true });
      return;
    }

    const guild = interaction.guild;
    const owner = await guild.fetchOwner();

    const embed = new EmbedBuilder()
      .setTitle(guild.name)
      .setColor(0x5865f2)
      .setThumbnail(guild.iconURL())
      .addFields(
        { name: "Owner", value: owner.user.tag, inline: true },
        { name: "Members", value: guild.memberCount.toString(), inline: true },
        {
          name: "Created",
          value: time(guild.createdAt, TimestampStyles.LongDate),
          inline: true,
        },
        { name: "ID", value: guild.id, inline: true }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [embed] });
  },
};
```

- [ ] **Step 2: Build and verify**

```bash
pnpm build
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/commands/server.ts
git commit -m "feat: implement /server command"
```

---

### Task 7: `/config` command

**Files:**
- Modify: `src/commands/config.ts`

The command has two subcommands: `view` (show current config) and `set` (update prefix or timezone). `set` requires the user to have `ManageGuild` permission.

- [ ] **Step 1: Implement `src/commands/config.ts`**

```typescript
import {
  EmbedBuilder,
  PermissionFlagsBits,
  SlashCommandBuilder,
} from "discord.js";
import type { Command } from "./index.js";
import { getConfig, setConfig, upsertGuild } from "../db/guild.js";

const VALID_TIMEZONES = Intl.supportedValuesOf("timeZone");

export const config: Command = {
  data: new SlashCommandBuilder()
    .setName("config")
    .setDescription("View or update server configuration")
    .addSubcommand((sub) =>
      sub
        .setName("view")
        .setDescription("Show the current server configuration")
    )
    .addSubcommand((sub) =>
      sub
        .setName("set")
        .setDescription("Update server configuration")
        .addStringOption((opt) =>
          opt
            .setName("prefix")
            .setDescription("Command prefix (1–5 characters)")
            .setRequired(false)
        )
        .addStringOption((opt) =>
          opt
            .setName("timezone")
            .setDescription("IANA timezone name, e.g. Europe/Lisbon")
            .setRequired(false)
        )
    ) as SlashCommandBuilder,

  async execute(interaction) {
    if (!interaction.guild) {
      await interaction.reply({ content: "This command can only be used in a server.", ephemeral: true });
      return;
    }

    const sub = interaction.options.getSubcommand();

    if (sub === "view") {
      const cfg = await getConfig(interaction.guild.id);
      const embed = new EmbedBuilder()
        .setTitle("Server Configuration")
        .setColor(0x5865f2)
        .addFields(
          { name: "Prefix", value: cfg?.prefix ?? "!", inline: true },
          { name: "Timezone", value: cfg?.timezone ?? "UTC", inline: true }
        );
      await interaction.reply({ embeds: [embed] });
      return;
    }

    if (sub === "set") {
      if (
        !interaction.memberPermissions?.has(PermissionFlagsBits.ManageGuild)
      ) {
        await interaction.reply({
          content: "You need the **Manage Server** permission to change settings.",
          ephemeral: true,
        });
        return;
      }

      const prefix = interaction.options.getString("prefix");
      const timezone = interaction.options.getString("timezone");

      if (!prefix && !timezone) {
        await interaction.reply({ content: "Provide at least one option to update.", ephemeral: true });
        return;
      }

      if (prefix !== null && (prefix.length < 1 || prefix.length > 5)) {
        await interaction.reply({ content: "Prefix must be 1–5 characters.", ephemeral: true });
        return;
      }

      if (timezone !== null && !VALID_TIMEZONES.includes(timezone)) {
        await interaction.reply({
          content: `\`${timezone}\` is not a valid IANA timezone. Examples: \`UTC\`, \`Europe/Lisbon\`, \`America/New_York\`.`,
          ephemeral: true,
        });
        return;
      }

      await upsertGuild(interaction.guild.id, interaction.guild.name);
      const updated = await setConfig(interaction.guild.id, {
        ...(prefix !== null ? { prefix } : {}),
        ...(timezone !== null ? { timezone } : {}),
      });

      const embed = new EmbedBuilder()
        .setTitle("Configuration Updated")
        .setColor(0x57f287)
        .addFields(
          { name: "Prefix", value: updated.prefix, inline: true },
          { name: "Timezone", value: updated.timezone, inline: true }
        );

      await interaction.reply({ embeds: [embed] });
    }
  },
};
```

- [ ] **Step 2: Build and verify**

```bash
pnpm build
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/commands/config.ts
git commit -m "feat: implement /config view and /config set subcommands"
```

---

### Task 8: Slash command registration script

Slash commands must be registered with Discord before they appear. This one-shot script is run during deployment (or manually in dev).

**Files:**
- Create: `src/deploy-commands.ts`

- [ ] **Step 1: Create `src/deploy-commands.ts`**

```typescript
import "dotenv/config";
import { REST, Routes } from "discord.js";
import { commands } from "./commands/index.js";

const token = process.env.BOT_TOKEN;
const clientId = process.env.CLIENT_ID;
const guildId = process.env.GUILD_ID;

if (!token || !clientId) {
  throw new Error("BOT_TOKEN and CLIENT_ID are required");
}

const rest = new REST().setToken(token);

const body = [...commands.values()].map((cmd) => cmd.data.toJSON());

async function deploy() {
  if (guildId) {
    // Guild-scoped (instant, for dev)
    await rest.put(Routes.applicationGuildCommands(clientId!, guildId), { body });
    console.log(`Registered ${body.length} guild commands in ${guildId}`);
  } else {
    // Global (up to 1 h propagation, for prod)
    await rest.put(Routes.applicationCommands(clientId!), { body });
    console.log(`Registered ${body.length} global commands`);
  }
}

deploy().catch(console.error);
```

- [ ] **Step 2: Build and verify**

```bash
pnpm build
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/deploy-commands.ts
git commit -m "feat: add slash command registration script"
```

---

### Task 9: Dockerfile + docker-compose

**Files:**
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`
- Modify: `docker-compose.prod.yml`

- [ ] **Step 1: Replace `Dockerfile`**

```dockerfile
FROM node:22-alpine AS base
RUN corepack enable

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build
RUN pnpm prune --prod

# Runtime
FROM node:22-alpine AS runner
WORKDIR /app
RUN addgroup -S skywizz && adduser -S skywizz -G skywizz
COPY --from=builder --chown=skywizz:skywizz /app/dist ./dist
COPY --from=builder --chown=skywizz:skywizz /app/node_modules ./node_modules
COPY --from=builder --chown=skywizz:skywizz /app/package.json ./package.json
COPY --from=deps --chown=skywizz:skywizz /app/node_modules/.prisma ./node_modules/.prisma
USER skywizz
CMD ["node", "dist/index.js"]
```

- [ ] **Step 2: Replace `docker-compose.yml` (local dev)**

```yaml
services:
  bot:
    build: .
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: skywizz
      POSTGRES_PASSWORD: password
      POSTGRES_DB: skywizz
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U skywizz"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

- [ ] **Step 3: Replace `docker-compose.prod.yml` (production)**

```yaml
services:
  bot:
    image: ${BOT_IMAGE}
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      CLIENT_ID: ${CLIENT_ID}
      DATABASE_URL: ${DATABASE_URL}
      NODE_ENV: production
      TIMEZONE: ${TIMEZONE:-UTC}
    networks:
      - skywizz-data
    restart: unless-stopped

networks:
  skywizz-data:
    external: true
```

- [ ] **Step 4: Verify local docker build works**

```bash
docker build -t skywizz-bot-test .
```

Expected: image builds successfully, no errors.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml docker-compose.prod.yml
git commit -m "feat: replace Dockerfile and docker-compose for Node.js bot"
```

---

### Task 10: Update GitHub Actions deploy workflow

The existing deploy workflow in `.github/workflows/deploy.yml` already knows how to:
- Push images to Harbor
- Create-or-update a Portainer stack via REST API

We update it to build the new Node.js image (no Python, no Harbor migrator variant needed yet).

**Files:**
- Modify: `.github/workflows/deploy.yml`

- [ ] **Step 1: Replace `.github/workflows/deploy.yml`**

```yaml
name: Deploy

on:
  push:
    branches: [dev]
  workflow_dispatch:

env:
  STACK_NAME: skywizz-bot
  PORTAINER_ENDPOINT_ID: "9"

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.image }}
    steps:
      - uses: actions/checkout@v4

      - name: Get short SHA
        id: meta
        run: echo "image=${{ vars.HARBOR_REGISTRY }}/skywizz/skywizz-bot:${{ github.sha }}" >> "$GITHUB_OUTPUT"

      - name: Log in to Harbor
        uses: docker/login-action@v3
        with:
          registry: ${{ vars.HARBOR_REGISTRY }}
          username: ${{ secrets.HARBOR_USER }}
          password: ${{ secrets.HARBOR_PASSWORD }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    steps:
      - uses: actions/checkout@v4

      - name: Read compose file
        id: compose
        run: echo "content=$(cat docker-compose.prod.yml | jq -Rs .)" >> "$GITHUB_OUTPUT"

      - name: Check if stack exists
        id: check
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "X-API-Key: ${{ secrets.PORTAINER_API_KEY }}" \
            "${{ secrets.PORTAINER_URL }}/api/stacks" | \
            jq --arg name "$STACK_NAME" '[.[] | select(.Name == $name)] | length')
          echo "count=$STATUS" >> "$GITHUB_OUTPUT"
        env:
          STATUS: ""

      - name: Get stack ID (if exists)
        id: stack
        run: |
          ID=$(curl -s \
            -H "X-API-Key: ${{ secrets.PORTAINER_API_KEY }}" \
            "${{ secrets.PORTAINER_URL }}/api/stacks" | \
            jq --arg name "$STACK_NAME" '.[] | select(.Name == $name) | .Id')
          echo "id=$ID" >> "$GITHUB_OUTPUT"

      - name: Update existing stack
        if: steps.stack.outputs.id != ''
        run: |
          curl -s -X PUT \
            -H "X-API-Key: ${{ secrets.PORTAINER_API_KEY }}" \
            -H "Content-Type: application/json" \
            "${{ secrets.PORTAINER_URL }}/api/stacks/${{ steps.stack.outputs.id }}?endpointId=${{ env.PORTAINER_ENDPOINT_ID }}" \
            -d "{
              \"stackFileContent\": ${{ steps.compose.outputs.content }},
              \"env\": [
                {\"name\": \"BOT_IMAGE\", \"value\": \"${{ needs.build-and-push.outputs.image }}\"},
                {\"name\": \"BOT_TOKEN\", \"value\": \"${{ secrets.BOT_TOKEN }}\"},
                {\"name\": \"CLIENT_ID\", \"value\": \"${{ secrets.CLIENT_ID }}\"},
                {\"name\": \"DATABASE_URL\", \"value\": \"${{ secrets.DATABASE_URL }}\"},
                {\"name\": \"TIMEZONE\", \"value\": \"${{ vars.TIMEZONE }}\"}
              ],
              \"prune\": true,
              \"pullImage\": true
            }"

      - name: Create new stack
        if: steps.stack.outputs.id == ''
        run: |
          curl -s -X POST \
            -H "X-API-Key: ${{ secrets.PORTAINER_API_KEY }}" \
            -H "Content-Type: application/json" \
            "${{ secrets.PORTAINER_URL }}/api/stacks/create/standalone/string?endpointId=${{ env.PORTAINER_ENDPOINT_ID }}" \
            -d "{
              \"name\": \"$STACK_NAME\",
              \"stackFileContent\": ${{ steps.compose.outputs.content }},
              \"env\": [
                {\"name\": \"BOT_IMAGE\", \"value\": \"${{ needs.build-and-push.outputs.image }}\"},
                {\"name\": \"BOT_TOKEN\", \"value\": \"${{ secrets.BOT_TOKEN }}\"},
                {\"name\": \"CLIENT_ID\", \"value\": \"${{ secrets.CLIENT_ID }}\"},
                {\"name\": \"DATABASE_URL\", \"value\": \"${{ secrets.DATABASE_URL }}\"},
                {\"name\": \"TIMEZONE\", \"value\": \"${{ vars.TIMEZONE }}\"}
              ]
            }"
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: update deploy workflow for Node.js bot image"
```

---

## Verification

1. **Local build:** `pnpm build` exits 0, `dist/` contains `index.js`.
2. **Register dev commands:** Copy `.env.example` → `.env`, fill in real `BOT_TOKEN`, `CLIENT_ID`, `GUILD_ID`. Run `pnpm deploy-commands`. Expected: `Registered 3 guild commands in <guild_id>`.
3. **Run locally:** `pnpm dev`. Expected: `Logged in as SkyWizz#XXXX`.
4. **Test commands in Discord:**
   - `/uptime` → embed with "Running for Xs" and relative timestamp
   - `/server` → embed with guild name, owner, member count, created date
   - `/config view` → embed with prefix `!` and timezone `UTC`
   - `/config set prefix=?` → embed confirming `?` prefix (requires Manage Server)
   - `/config set timezone=Europe/Lisbon` → embed confirming timezone
5. **Docker build:** `docker build -t skywizz-bot-test .` exits 0.
6. **docker-compose up:** `docker compose up` starts bot + postgres, bot logs in.

---

## What comes next

This bare-bones bot is the foundation. The next PRs will add:
- More commands (moderation, weather, etc.) following the same pattern
- The `skywizz-web` management panel (separate repo, separate plan)
- Shared Postgres between bot and web (bot joins `skywizz-data` network)
- CI workflow (`ci.yml`) with `tsc --noEmit`, ESLint, and basic tests
