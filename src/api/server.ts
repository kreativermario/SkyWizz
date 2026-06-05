import { createServer, type IncomingMessage, type ServerResponse, type Server } from "node:http";
import { randomUUID } from "node:crypto";
import { prisma } from "../db/client.js";
import { logger } from "../logger.js";
import { getWelcomeConfig, upsertWelcomeConfig } from "../db/welcome.js";
import { createAuditLog } from "../db/audit.js";

const PORT         = Number(process.env.BOT_API_PORT ?? 3002);
const API_SECRET   = process.env.BOT_API_SECRET ?? "";
const BOT_TOKEN    = process.env.BOT_TOKEN ?? "";
const MAX_BODY_BYTES = 8_192;

// ── Rate limiter (sliding window, in-memory) ─────────────
const RATE_LIMIT    = 120;
const RATE_WINDOW_MS = 60_000;
const rateWindows   = new Map<string, number[]>();

function isRateLimited(ip: string): boolean {
  const now    = Date.now();
  const cutoff = now - RATE_WINDOW_MS;
  const prev   = rateWindows.get(ip) ?? [];
  const window = prev.filter((t) => t > cutoff);
  window.push(now);
  rateWindows.set(ip, window);
  return window.length > RATE_LIMIT;
}

setInterval(() => {
  const cutoff = Date.now() - RATE_WINDOW_MS;
  for (const [ip, ts] of rateWindows) {
    if ((ts.at(-1) ?? 0) < cutoff) rateWindows.delete(ip);
  }
}, RATE_WINDOW_MS).unref();

// ── Helpers ──────────────────────────────────────────────
function setSecurityHeaders(res: ServerResponse): void {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("Content-Security-Policy", "default-src 'none'");
  res.setHeader("Permissions-Policy", "geolocation=(), microphone=(), camera=()");
  res.setHeader("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
}

function send(res: ServerResponse, status: number, body: unknown, requestId: string): void {
  setSecurityHeaders(res);
  res.setHeader("X-Request-Id", requestId);
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(payload),
  });
  res.end(payload);
}

function getClientIp(req: IncomingMessage): string {
  const forwarded = req.headers["x-forwarded-for"];
  if (typeof forwarded === "string") return forwarded.split(",")[0].trim();
  return req.socket.remoteAddress ?? "unknown";
}

async function readJson(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    let raw = "";
    let bytes = 0;

    req.on("data", (chunk: Buffer) => {
      bytes += chunk.byteLength;
      if (bytes > MAX_BODY_BYTES) {
        req.destroy();
        reject(new Error("Payload too large"));
        return;
      }
      raw += chunk.toString("utf8");
    });

    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); }
      catch { reject(new Error("Invalid JSON")); }
    });

    req.on("error", reject);
  });
}

// ── Server ───────────────────────────────────────────────
export function startApiServer(): Server {
  if (!API_SECRET) {
    logger.warn("api", "BOT_API_SECRET is not set — all authenticated requests will be rejected");
  }

  const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
    const requestId = randomUUID();
    const ip        = getClientIp(req);
    const start     = Date.now();
    const method    = req.method?.toUpperCase() ?? "GET";
    const url       = new URL(req.url ?? "/", "http://localhost");
    const parts     = url.pathname.replace(/^\/|\/$/g, "").split("/");
    const [seg0, guildId, seg2] = parts;

    res.on("finish", () => {
      logger.info("api", "request", {
        method,
        path: url.pathname,
        status: res.statusCode,
        ms: Date.now() - start,
        ip,
        requestId,
      });
    });

    // ── Health (unauthenticated — used by Docker/Portainer healthchecks) ──
    if (method === "GET" && seg0 === "health" && !guildId) {
      try {
        await prisma.$queryRaw`SELECT 1`;
        return send(res, 200, { status: "ok", uptime: Math.floor(process.uptime()) }, requestId);
      } catch (err) {
        logger.error("api", "health check db failed", { err: String(err) });
        return send(res, 503, { status: "error", uptime: Math.floor(process.uptime()) }, requestId);
      }
    }

    // ── Auth ──────────────────────────────────────────────
    if (req.headers.authorization !== `Bearer ${API_SECRET}` || !API_SECRET) {
      logger.warn("api", "unauthorized request", { method, path: url.pathname, ip, requestId });
      return send(res, 401, { error: "Unauthorized" }, requestId);
    }

    // ── Rate limit ────────────────────────────────────────
    if (isRateLimited(ip)) {
      logger.warn("api", "rate limited", { ip, requestId });
      res.setHeader("Retry-After", "60");
      return send(res, 429, { error: "Too many requests" }, requestId);
    }

    try {
      // GET /guilds
      if (method === "GET" && seg0 === "guilds" && !guildId) {
        const guilds = await prisma.guild.findMany({
          where: { leftAt: null },
          select: { id: true },
        });
        return send(res, 200, { guilds }, requestId);
      }

      // GET /guilds/:id
      if (method === "GET" && seg0 === "guilds" && guildId && !seg2) {
        const guild = await prisma.guild.findUnique({
          where: { id: guildId },
          include: { config: true, welcomeConfig: true },
        });
        if (!guild || guild.leftAt !== null) {
          return send(res, 404, { error: "Guild not found" }, requestId);
        }
        return send(res, 200, { guild }, requestId);
      }

      // PATCH /guilds/:id/config
      if (method === "PATCH" && seg0 === "guilds" && guildId && seg2 === "config") {
        // Ensure the guild is known and active before touching config
        const guild = await prisma.guild.findUnique({
          where: { id: guildId },
          select: { id: true, leftAt: true },
        });
        if (!guild || guild.leftAt !== null) {
          return send(res, 404, { error: "Guild not found" }, requestId);
        }

        let body: Record<string, unknown>;
        try {
          body = (await readJson(req)) as Record<string, unknown>;
        } catch (err) {
          const msg = err instanceof Error ? err.message : "Bad request";
          return send(res, 400, { error: msg }, requestId);
        }

        const actorId   = typeof body.actorId   === "string" ? body.actorId   : undefined;
        const actorName = typeof body.actorName  === "string" ? body.actorName : "Unknown";

        const data: {
          prefix?: string;
          timezone?: string;
          disabledCommands?: string[];
        } = {};

        if (typeof body.prefix === "string" && body.prefix.length >= 1 && body.prefix.length <= 5) {
          data.prefix = body.prefix;
        }
        if (typeof body.timezone === "string" && body.timezone.length >= 1 && body.timezone.length <= 64) {
          data.timezone = body.timezone;
        }
        if (Array.isArray(body.disabledCommands) && body.disabledCommands.every((c) => typeof c === "string")) {
          data.disabledCommands = body.disabledCommands as string[];
        }

        // Fetch current config to compute changes for audit log
        const prevConfig = await prisma.guildConfig.findUnique({ where: { guildId } });

        const config = await prisma.guildConfig.upsert({
          where: { guildId },
          update: data,
          create: { guildId, ...data },
        });

        if (actorId) {
          const changes: Record<string, [unknown, unknown]> = {};
          if (data.prefix !== undefined && data.prefix !== (prevConfig?.prefix ?? "!")) {
            changes.prefix = [prevConfig?.prefix ?? "!", data.prefix];
          }
          if (data.timezone !== undefined && data.timezone !== (prevConfig?.timezone ?? "UTC")) {
            changes.timezone = [prevConfig?.timezone ?? "UTC", data.timezone];
          }
          if (data.disabledCommands !== undefined) {
            changes.disabledCommands = [prevConfig?.disabledCommands ?? [], data.disabledCommands];
          }
          createAuditLog(guildId, actorId, actorName, "config.update", changes).catch((err) =>
            logger.error("api", "audit log failed", { err: String(err) })
          );
        }

        return send(res, 200, { config }, requestId);
      }

      // GET /guilds/:id/welcome
      if (method === "GET" && seg0 === "guilds" && guildId && seg2 === "welcome") {
        const welcomeConfig = await getWelcomeConfig(guildId);
        return send(res, 200, { welcomeConfig }, requestId);
      }

      // GET /guilds/:id/channels
      if (method === "GET" && seg0 === "guilds" && guildId && seg2 === "channels") {
        if (!BOT_TOKEN) return send(res, 503, { error: "Bot token not configured" }, requestId);
        const discordRes = await fetch(`https://discord.com/api/v10/guilds/${guildId}/channels`, {
          headers: { Authorization: `Bot ${BOT_TOKEN}` },
          signal: AbortSignal.timeout(5000),
          cache: "no-store",
        } as RequestInit);
        if (!discordRes.ok) return send(res, 502, { error: "Could not fetch channels" }, requestId);
        const all = (await discordRes.json()) as { id: string; name: string; type: number; position: number }[];
        const channels = all
          .filter((c) => c.type === 0 || c.type === 5)
          .sort((a, b) => a.position - b.position)
          .map((c) => ({ id: c.id, name: c.name }));
        return send(res, 200, { channels }, requestId);
      }

      // PATCH /guilds/:id/welcome
      if (method === "PATCH" && seg0 === "guilds" && guildId && seg2 === "welcome") {
        const existingGuild = await prisma.guild.findUnique({
          where: { id: guildId },
          select: { id: true, leftAt: true },
        });
        if (!existingGuild || existingGuild.leftAt !== null) {
          return send(res, 404, { error: "Guild not found" }, requestId);
        }

        let body: Record<string, unknown>;
        try {
          body = (await readJson(req)) as Record<string, unknown>;
        } catch (err) {
          const msg = err instanceof Error ? err.message : "Bad request";
          return send(res, 400, { error: msg }, requestId);
        }

        const welcomeData: { enabled?: boolean; channelId?: string; message?: string } = {};

        if (typeof body.enabled === "boolean") {
          welcomeData.enabled = body.enabled;
        }
        if (typeof body.channelId === "string") {
          if (body.channelId.length > 100) return send(res, 400, { error: "channelId too long" }, requestId);
          if (body.channelId !== "" && !/^\d+$/.test(body.channelId)) {
            return send(res, 400, { error: "channelId must be numeric" }, requestId);
          }
          welcomeData.channelId = body.channelId;
        }
        if (typeof body.message === "string") {
          if (body.message.length < 1 || body.message.length > 500) {
            return send(res, 400, { error: "message must be 1-500 chars" }, requestId);
          }
          welcomeData.message = body.message;
        }

        const actorId   = typeof body.actorId   === "string" ? body.actorId   : undefined;
        const actorName = typeof body.actorName  === "string" ? body.actorName : "Unknown";

        const prevWelcome = await getWelcomeConfig(guildId);
        const updated = await upsertWelcomeConfig(guildId, welcomeData);

        if (actorId) {
          const changes: Record<string, [unknown, unknown]> = {};
          if (welcomeData.enabled !== undefined && welcomeData.enabled !== (prevWelcome?.enabled ?? false)) {
            changes.enabled = [prevWelcome?.enabled ?? false, welcomeData.enabled];
          }
          if (welcomeData.channelId !== undefined && welcomeData.channelId !== (prevWelcome?.channelId ?? "")) {
            changes.channelId = [prevWelcome?.channelId ?? "", welcomeData.channelId];
          }
          if (welcomeData.message !== undefined && welcomeData.message !== prevWelcome?.message) {
            changes.message = [prevWelcome?.message ?? "", welcomeData.message];
          }
          createAuditLog(guildId, actorId, actorName, "welcome.update", changes).catch((err) =>
            logger.error("api", "audit log failed", { err: String(err) })
          );
        }

        return send(res, 200, { welcomeConfig: updated }, requestId);
      }

      // GET /guilds/:id/stats
      if (method === "GET" && seg0 === "guilds" && guildId && seg2 === "stats") {
        const since = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        const usage = await prisma.commandUsage.groupBy({
          by: ["commandName"],
          where: { guildId, executedAt: { gte: since } },
          _count: { commandName: true },
          orderBy: { _count: { commandName: "desc" } },
        });
        const commands = usage.map((u) => ({ name: u.commandName, count: u._count.commandName }));
        const total = commands.reduce((sum, c) => sum + c.count, 0);
        return send(res, 200, { stats: { period: "30d", commands, total } }, requestId);
      }

      // GET /guilds/:id/audit
      if (method === "GET" && seg0 === "guilds" && guildId && seg2 === "audit") {
        const logs = await prisma.auditLog.findMany({
          where: { guildId },
          orderBy: { createdAt: "desc" },
          take: 50,
        });
        return send(res, 200, { logs }, requestId);
      }

      return send(res, 404, { error: "Not found" }, requestId);
    } catch (err) {
      logger.error("api", "unhandled error", { requestId, err: String(err) });
      return send(res, 500, { error: "Internal server error" }, requestId);
    }
  });

  server.requestTimeout  = 10_000;
  server.headersTimeout  = 15_000;
  server.keepAliveTimeout = 5_000;

  server.listen(PORT, () => {
    logger.info("api", "listening", { port: PORT });
  });

  return server;
}
