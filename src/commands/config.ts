import {
  EmbedBuilder,
  MessageFlags,
  PermissionFlagsBits,
  SlashCommandBuilder,
} from "discord.js";
import type { Command } from "./index.js";
import { getConfig, setConfig, upsertGuild } from "../db/guild.js";

const VALID_TIMEZONES = Intl.supportedValuesOf("timeZone");

export const config: Command = {
  data: new SlashCommandBuilder()
    .setName("config")
    .setDescription("View or update server configuration")
    .addSubcommand((sub) =>
      sub
        .setName("view")
        .setDescription("Show the current server configuration")
    )
    .addSubcommand((sub) =>
      sub
        .setName("set")
        .setDescription("Update server configuration")
        .addStringOption((opt) =>
          opt
            .setName("prefix")
            .setDescription("Command prefix (1–5 characters)")
            .setRequired(false)
        )
        .addStringOption((opt) =>
          opt
            .setName("timezone")
            .setDescription("IANA timezone name, e.g. Europe/Lisbon")
            .setRequired(false)
        )
    ) as SlashCommandBuilder,

  async execute(interaction) {
    if (!interaction.guild) {
      await interaction.reply({
        content: "This command can only be used in a server.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }

    const sub = interaction.options.getSubcommand();

    if (sub === "view") {
      const cfg = await getConfig(interaction.guild.id);
      const embed = new EmbedBuilder()
        .setTitle("Server Configuration")
        .setColor(0x5865f2)
        .addFields(
          { name: "Prefix", value: cfg?.prefix ?? "!", inline: true },
          { name: "Timezone", value: cfg?.timezone ?? "UTC", inline: true }
        );
      await interaction.reply({ embeds: [embed] });
      return;
    }

    if (sub === "set") {
      if (
        !interaction.memberPermissions?.has(PermissionFlagsBits.ManageGuild)
      ) {
        await interaction.reply({
          content: "You need the **Manage Server** permission to change settings.",
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      const prefix = interaction.options.getString("prefix");
      const timezone = interaction.options.getString("timezone");

      if (!prefix && !timezone) {
        await interaction.reply({
          content: "Provide at least one option to update.",
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      if (prefix !== null && (prefix.length < 1 || prefix.length > 5)) {
        await interaction.reply({
          content: "Prefix must be 1–5 characters.",
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      if (timezone !== null && !VALID_TIMEZONES.includes(timezone)) {
        await interaction.reply({
          content: `\`${timezone}\` is not a valid IANA timezone. Examples: \`UTC\`, \`Europe/Lisbon\`, \`America/New_York\`.`,
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      await upsertGuild(interaction.guild.id, interaction.guild.name);
      const updated = await setConfig(interaction.guild.id, {
        ...(prefix !== null ? { prefix } : {}),
        ...(timezone !== null ? { timezone } : {}),
      });

      const embed = new EmbedBuilder()
        .setTitle("Configuration Updated")
        .setColor(0x57f287)
        .addFields(
          { name: "Prefix", value: updated.prefix, inline: true },
          { name: "Timezone", value: updated.timezone, inline: true }
        );

      await interaction.reply({ embeds: [embed] });
    }
  },
};
