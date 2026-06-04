import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const uptime: Command = {
  data: new SlashCommandBuilder()
    .setName("uptime")
    .setDescription("Show how long the bot has been running"),
  async execute(interaction) {
    await interaction.reply("uptime stub");
  },
};
