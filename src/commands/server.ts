import { SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

export const server: Command = {
  data: new SlashCommandBuilder()
    .setName("server")
    .setDescription("Show information about this server"),
  async execute(interaction) {
    await interaction.reply("server stub");
  },
};
