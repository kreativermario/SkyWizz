import {
  type ChatInputCommandInteraction,
  type SlashCommandBuilder,
  Collection,
} from "discord.js";
import { uptime } from "./uptime.js";
import { server } from "./server.js";
import { config } from "./config.js";
import { weather } from "./weather.js";

export interface Command {
  data: SlashCommandBuilder | ReturnType<SlashCommandBuilder["setName"]>;
  execute: (interaction: ChatInputCommandInteraction) => Promise<void>;
}

export const commands = new Collection<string, Command>([
  [uptime.data.name, uptime],
  [server.data.name, server],
  [config.data.name, config],
  [weather.data.name, weather],
]);
