import { Client, GatewayIntentBits } from "discord.js";

export const client = new Client({
  // GuildMembers is a privileged intent — enable it in the Discord Developer Portal
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers],
});
