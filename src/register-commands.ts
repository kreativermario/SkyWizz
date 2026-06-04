import { REST, Routes } from "discord.js";
import { commands } from "./commands/index.js";

export async function registerCommands(): Promise<void> {
  const token = process.env.BOT_TOKEN!;
  const clientId = process.env.CLIENT_ID!;
  const guildId = process.env.GUILD_ID;

  const rest = new REST().setToken(token);
  const body = [...commands.values()].map((cmd) => cmd.data.toJSON());

  if (guildId) {
    await rest.put(Routes.applicationGuildCommands(clientId, guildId), { body });
    console.log(`Registered ${body.length} guild commands in ${guildId}`);
  } else {
    await rest.put(Routes.applicationCommands(clientId), { body });
    console.log(`Registered ${body.length} global commands`);
  }
}
