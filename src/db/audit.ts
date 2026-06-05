import { type Prisma } from "@prisma/client";
import { prisma } from "./client.js";

export async function createAuditLog(
  guildId: string,
  actorId: string,
  actorName: string,
  action: string,
  changes: Record<string, [unknown, unknown]>
): Promise<void> {
  await prisma.auditLog.create({
    data: { guildId, actorId, actorName, action, changes: changes as Prisma.InputJsonValue },
  });
}
