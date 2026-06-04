import {
  EmbedBuilder,
  MessageFlags,
  SlashCommandBuilder,
  time,
  TimestampStyles,
} from "discord.js";
import type { Command } from "./index.js";

export const server: Command = {
  data: new SlashCommandBuilder()
    .setName("server")
    .setDescription("Show information about this server"),

  async execute(interaction) {
    if (!interaction.guild) {
      await interaction.reply({
        content: "This command can only be used in a server.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }

    const guild = interaction.guild;
    const owner = await guild.fetchOwner();

    const embed = new EmbedBuilder()
      .setTitle(guild.name)
      .setColor(0x5865f2)
      .setThumbnail(guild.iconURL())
      .addFields(
        { name: "Owner", value: owner.user.tag, inline: true },
        { name: "Members", value: guild.memberCount.toString(), inline: true },
        {
          name: "Created",
          value: time(guild.createdAt, TimestampStyles.LongDate),
          inline: true,
        },
        { name: "ID", value: guild.id, inline: true }
      )
      .setTimestamp();

    await interaction.reply({ embeds: [embed] });
  },
};
