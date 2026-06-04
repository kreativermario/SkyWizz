import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const config: Command = {
  data: new SlashCommandBuilder()
    .setName("config")
    .setDescription("View or update server configuration"),
  async execute(interaction) {
    await interaction.reply("config stub");
  },
};
