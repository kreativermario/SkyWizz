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
