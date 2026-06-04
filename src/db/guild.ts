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
