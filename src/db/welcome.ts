import type { WelcomeConfig } from "@prisma/client";
import { prisma } from "./client.js";

export async function getWelcomeConfig(guildId: string): Promise<WelcomeConfig | null> {
  return prisma.welcomeConfig.findUnique({ where: { guildId } });
}

export async function upsertWelcomeConfig(
  guildId: string,
  data: Partial<Pick<WelcomeConfig, "enabled" | "channelId" | "message">>
): Promise<WelcomeConfig> {
  return prisma.welcomeConfig.upsert({
    where: { guildId },
    update: data,
    create: { guildId, ...data },
  });
}
