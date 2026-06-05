import "dotenv/config";
import { Events, MessageFlags, type InteractionReplyOptions } from "discord.js";
import { client } from "./client.js";
import { commands } from "./commands/index.js";
import { prisma } from "./db/client.js";
import { upsertGuild, markGuildLeft, getConfig } from "./db/guild.js";
import { getWelcomeConfig } from "./db/welcome.js";
import { registerCommands } from "./register-commands.js";
import { logger } from "./logger.js";

const startedAt = new Date();
export { startedAt };

async function shutdown(code: number = 0): Promise<never> {
  logger.info("bot", "shutting down", { code });
  await client.destroy();
  await prisma.$disconnect();
  process.exit(code);
}

process.on("SIGTERM", () => shutdown(0));
process.on("SIGINT",  () => shutdown(0));

client.once(Events.ClientReady, async (c) => {
  await registerCommands().catch((err) =>
    logger.error("bot", "registerCommands failed", { err: String(err) })
  );

  const syncs = c.guilds.cache.map((g) =>
    upsertGuild(g.id, g.name, g.icon).catch((err) =>
      logger.error("bot", "guild sync failed", { guildId: g.id, err: String(err) })
    )
  );
  await Promise.all(syncs);

  logger.info("bot", "ready", { username: c.user.username, guilds: c.guilds.cache.size });
});

client.on(Events.GuildCreate, (guild) => {
  logger.info("bot", "guild joined", { guildId: guild.id, name: guild.name });
  upsertGuild(guild.id, guild.name, guild.icon).catch((err) =>
    logger.error("bot", "upsertGuild failed on join", { guildId: guild.id, err: String(err) })
  );
});

client.on(Events.GuildDelete, (guild) => {
  logger.info("bot", "guild left", { guildId: guild.id, name: guild.name });
  markGuildLeft(guild.id).catch((err) =>
    logger.error("bot", "markGuildLeft failed", { guildId: guild.id, err: String(err) })
  );
});

/**
 * GuildMemberAdd — sends a welcome message when a new member joins.
 * NOTE: GuildMembers is a privileged intent — it must be enabled in the Discord Developer Portal
 * under Bot > Privileged Gateway Intents before this handler will fire.
 */
client.on(Events.GuildMemberAdd, async (member) => {
  const config = await getWelcomeConfig(member.guild.id).catch(() => null);
  if (!config?.enabled || !config.channelId) return;

  const channel = member.guild.channels.cache.get(config.channelId);
  if (!channel?.isTextBased()) return;

  const msg = config.message
    .replace(/\{user\}/g, `<@${member.id}>`)
    .replace(/\{username\}/g, member.user.username)
    .replace(/\{server\}/g, member.guild.name)
    .replace(/\{memberCount\}/g, member.guild.memberCount.toString());

  await channel.send(msg).catch((err) =>
    logger.error("bot", "welcome message failed", { guildId: member.guild.id, err: String(err) })
  );
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = commands.get(interaction.commandName);
  if (!command) return;

  if (interaction.guildId) {
    const cfg = await getConfig(interaction.guildId).catch((err) => {
      logger.error("bot", "getConfig failed", { guildId: interaction.guildId, err: String(err) });
      return null;
    });
    if (cfg?.disabledCommands.includes(interaction.commandName)) {
      await interaction.reply({
        content: "This command is disabled on this server.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }
  }

  const t = Date.now();
  try {
    await command.execute(interaction);
    logger.info("cmd", "executed", {
      command: interaction.commandName,
      userId: interaction.user.id,
      guildId: interaction.guildId ?? "dm",
      ms: Date.now() - t,
    });
    if (interaction.guildId) {
      prisma.commandUsage.create({
        data: { guildId: interaction.guildId, commandName: interaction.commandName, userId: interaction.user.id },
      }).catch((err) => logger.error("cmd", "usage log failed", { err: String(err) }));
    }
  } catch (error) {
    logger.error("cmd", "execution failed", {
      command: interaction.commandName,
      userId: interaction.user.id,
      guildId: interaction.guildId ?? "dm",
      err: String(error),
      ms: Date.now() - t,
    });
    const options: InteractionReplyOptions = {
      content: "Something went wrong.",
      flags: MessageFlags.Ephemeral,
    };
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp(options);
    } else {
      await interaction.reply(options);
    }
  }
});

async function main() {
  await client.login(process.env.BOT_TOKEN);
}

main().catch(async (error) => {
  logger.error("bot", "fatal startup error", { err: String(error) });
  await shutdown(1);
});
