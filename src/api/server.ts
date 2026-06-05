import { createServer, type IncomingMessage, type ServerResponse, type Server } from "node:http";
import { randomUUID } from "node:crypto";
import { prisma } from "../db/client.js";
import { logger } from "../logger.js";

const PORT         = Number(process.env.BOT_API_PORT ?? 3002);
const API_SECRET   = process.env.BOT_API_SECRET ?? "";
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
          include: { config: true },
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

        const config = await prisma.guildConfig.upsert({
          where: { guildId },
          update: data,
          create: { guildId, ...data },
        });
        return send(res, 200, { config }, requestId);
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
