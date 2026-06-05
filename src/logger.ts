type Level = "info" | "warn" | "error" | "debug";

function log(level: Level, ctx: string, msg: string, meta?: Record<string, unknown>): void {
  const entry: Record<string, unknown> = { ts: new Date().toISOString(), level, ctx, msg };
  if (meta) entry.meta = meta;
  const line = JSON.stringify(entry) + "\n";
  if (level === "error") process.stderr.write(line);
  else process.stdout.write(line);
}

export const logger = {
  info:  (ctx: string, msg: string, meta?: Record<string, unknown>) => log("info",  ctx, msg, meta),
  warn:  (ctx: string, msg: string, meta?: Record<string, unknown>) => log("warn",  ctx, msg, meta),
  error: (ctx: string, msg: string, meta?: Record<string, unknown>) => log("error", ctx, msg, meta),
  debug: (ctx: string, msg: string, meta?: Record<string, unknown>) => {
    if (process.env.NODE_ENV !== "production") log("debug", ctx, msg, meta);
  },
};
