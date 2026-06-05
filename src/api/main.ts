import "dotenv/config";
import { startApiServer } from "./server.js";
import { prisma } from "../db/client.js";

const server = startApiServer();

async function shutdown(): Promise<never> {
  server.close();
  await prisma.$disconnect();
  process.exit(0);
}

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
