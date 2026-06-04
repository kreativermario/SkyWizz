import { EmbedBuilder, SlashCommandBuilder, time, TimestampStyles } from "discord.js";
import type { Command } from "./index.js";
import { startedAt } from "../index.js";

function formatDuration(ms: number): string {
  const s = Math.floor(ms / 1000);
  const days = Math.floor(s / 86400);
  const hours = Math.floor((s % 86400) / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  const seconds = s % 60;

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${seconds}s`);
  return parts.join(" ");
}

export const uptime: Command = {
  data: new SlashCommandBuilder()
    .setName("uptime")
    .setDescription("Show how long the bot has been running"),

  async execute(interaction) {
    const now = new Date();
    const ms = now.getTime() - startedAt.getTime();

    const embed = new EmbedBuilder()
      .setTitle("Uptime")
      .setColor(0x5865f2)
      .addFields(
        { name: "Running for", value: formatDuration(ms), inline: true },
        {
          name: "Started",
          value: time(startedAt, TimestampStyles.RelativeTime),
          inline: true,
        }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [embed] });
  },
};
