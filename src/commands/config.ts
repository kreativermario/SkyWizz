import {
  EmbedBuilder,
  MessageFlags,
  PermissionFlagsBits,
  SlashCommandBuilder,
} from "discord.js";
import type { Command } from "./index.js";
import { getConfig, setConfig, upsertGuild } from "../db/guild.js";

const VALID_TIMEZONES = Intl.supportedValuesOf("timeZone");

// config itself is excluded — disabling it would lock admins out
const TOGGLEABLE = ["weather", "server", "uptime"] as const;
type ToggleableCommand = (typeof TOGGLEABLE)[number];
const ALL_DISPLAY = ["weather", "server", "config", "uptime"];

export const config: Command = {
  data: new SlashCommandBuilder()
    .setName("config")
    .setDescription("View or update server configuration")
    .addSubcommand((sub) =>
      sub.setName("view").setDescription("Show the current server configuration")
    )
    .addSubcommand((sub) =>
      sub
        .setName("set")
        .setDescription("Update server configuration")
        .addStringOption((opt) =>
          opt.setName("prefix").setDescription("Command prefix (1–5 characters)").setRequired(false)
        )
        .addStringOption((opt) =>
          opt
            .setName("timezone")
            .setDescription("IANA timezone name, e.g. Europe/Lisbon")
            .setRequired(false)
        )
    )
    .addSubcommandGroup((group) =>
      group
        .setName("commands")
        .setDescription("Manage which commands are available in this server")
        .addSubcommand((sub) =>
          sub.setName("list").setDescription("List all commands and their enabled/disabled status")
        )
        .addSubcommand((sub) =>
          sub
            .setName("toggle")
            .setDescription("Enable or disable a command")
            .addStringOption((opt) =>
              opt
                .setName("command")
                .setDescription("Command to toggle")
                .setRequired(true)
                .addChoices(
                  { name: "weather", value: "weather" },
                  { name: "server",  value: "server"  },
                  { name: "uptime",  value: "uptime"  },
                )
            )
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

    const group = interaction.options.getSubcommandGroup();
    const sub   = interaction.options.getSubcommand();

    // ── /config commands list ────────────────────────────────
    if (group === "commands" && sub === "list") {
      const cfg = await getConfig(interaction.guild.id);
      const disabled = cfg?.disabledCommands ?? [];
      const lines = ALL_DISPLAY.map(
        (cmd) => `${disabled.includes(cmd) ? "🔴" : "🟢"} \`/${cmd}\``
      );
      await interaction.reply({
        embeds: [
          new EmbedBuilder()
            .setTitle("Command Status")
            .setColor(0x5865f2)
            .setDescription(lines.join("\n"))
            .setFooter({ text: "/config cannot be disabled" }),
        ],
      });
      return;
    }

    // ── /config commands toggle ──────────────────────────────
    if (group === "commands" && sub === "toggle") {
      if (!interaction.memberPermissions?.has(PermissionFlagsBits.ManageGuild)) {
        await interaction.reply({
          content: "You need the **Manage Server** permission to change settings.",
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      const commandName = interaction.options.getString("command", true) as ToggleableCommand;
      const cfg = await getConfig(interaction.guild.id);
      const disabled = cfg?.disabledCommands ?? [];
      const isDisabled = disabled.includes(commandName);
      const newDisabled = isDisabled
        ? disabled.filter((c) => c !== commandName)
        : [...disabled, commandName];

      await upsertGuild(interaction.guild.id, interaction.guild.name, interaction.guild.icon);
      await setConfig(interaction.guild.id, { disabledCommands: newDisabled });

      const action = isDisabled ? "enabled" : "disabled";
      await interaction.reply({
        embeds: [
          new EmbedBuilder()
            .setTitle(`Command ${action}`)
            .setColor(isDisabled ? 0x57f287 : 0xed4245)
            .setDescription(`\`/${commandName}\` has been **${action}** on this server.`),
        ],
      });
      return;
    }

    // ── /config view ─────────────────────────────────────────
    if (sub === "view") {
      const cfg = await getConfig(interaction.guild.id);
      await interaction.reply({
        embeds: [
          new EmbedBuilder()
            .setTitle("Server Configuration")
            .setColor(0x5865f2)
            .addFields(
              { name: "Prefix",   value: cfg?.prefix   ?? "!", inline: true },
              { name: "Timezone", value: cfg?.timezone ?? "UTC", inline: true }
            ),
        ],
      });
      return;
    }

    // ── /config set ──────────────────────────────────────────
    if (sub === "set") {
      if (!interaction.memberPermissions?.has(PermissionFlagsBits.ManageGuild)) {
        await interaction.reply({
          content: "You need the **Manage Server** permission to change settings.",
          flags: MessageFlags.Ephemeral,
        });
        return;
      }

      const prefix   = interaction.options.getString("prefix");
      const timezone = interaction.options.getString("timezone");

      if (prefix === null && timezone === null) {
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

      await upsertGuild(interaction.guild.id, interaction.guild.name, interaction.guild.icon);
      const updated = await setConfig(interaction.guild.id, {
        ...(prefix   !== null ? { prefix }   : {}),
        ...(timezone !== null ? { timezone } : {}),
      });

      await interaction.reply({
        embeds: [
          new EmbedBuilder()
            .setTitle("Configuration Updated")
            .setColor(0x57f287)
            .addFields(
              { name: "Prefix",   value: updated.prefix,   inline: true },
              { name: "Timezone", value: updated.timezone, inline: true }
            ),
        ],
      });
    }
  },
};
