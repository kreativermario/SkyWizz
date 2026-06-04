import "dotenv/config";
import { REST, Routes } from "discord.js";
import { commands } from "./commands/index.js";

const token = process.env.BOT_TOKEN;
const clientId = process.env.CLIENT_ID;
const guildId = process.env.GUILD_ID;

if (!token || !clientId) {
  throw new Error("BOT_TOKEN and CLIENT_ID are required");
}

const rest = new REST().setToken(token);

const body = [...commands.values()].map((cmd) => cmd.data.toJSON());

async function deploy() {
  if (guildId) {
    await rest.put(Routes.applicationGuildCommands(clientId!, guildId), { body });
    console.log(`Registered ${body.length} guild commands in ${guildId}`);
  } else {
    await rest.put(Routes.applicationCommands(clientId!), { body });
    console.log(`Registered ${body.length} global commands`);
  }
}

deploy().catch(console.error);
