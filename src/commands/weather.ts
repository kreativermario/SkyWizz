import { EmbedBuilder, MessageFlags, SlashCommandBuilder } from "discord.js";
import { z } from "zod";
import type { Command } from "./index.js";

const WMO: Record<number, { label: string; emoji: string }> = {
  0:  { label: "Clear sky",            emoji: "☀️" },
  1:  { label: "Mainly clear",         emoji: "🌤️" },
  2:  { label: "Partly cloudy",        emoji: "⛅" },
  3:  { label: "Overcast",             emoji: "☁️" },
  45: { label: "Fog",                  emoji: "🌫️" },
  48: { label: "Icy fog",              emoji: "🌫️" },
  51: { label: "Light drizzle",        emoji: "🌦️" },
  53: { label: "Drizzle",              emoji: "🌦️" },
  55: { label: "Heavy drizzle",        emoji: "🌧️" },
  61: { label: "Light rain",           emoji: "🌧️" },
  63: { label: "Rain",                 emoji: "🌧️" },
  65: { label: "Heavy rain",           emoji: "🌧️" },
  71: { label: "Light snow",           emoji: "🌨️" },
  73: { label: "Snow",                 emoji: "❄️" },
  75: { label: "Heavy snow",           emoji: "❄️" },
  77: { label: "Snow grains",          emoji: "🌨️" },
  80: { label: "Light showers",        emoji: "🌦️" },
  81: { label: "Showers",              emoji: "🌧️" },
  82: { label: "Violent showers",      emoji: "⛈️" },
  85: { label: "Snow showers",         emoji: "🌨️" },
  86: { label: "Heavy snow showers",   emoji: "❄️" },
  95: { label: "Thunderstorm",         emoji: "⛈️" },
  96: { label: "Thunderstorm + hail",  emoji: "⛈️" },
  99: { label: "Thunderstorm + hail",  emoji: "⛈️" },
};

const WIND_DIRS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

const GeoResultSchema = z.object({
  name: z.string(),
  country: z.string(),
  latitude: z.number(),
  longitude: z.number(),
  admin1: z.string().optional(),
});

const GeoResponseSchema = z.object({
  results: z.array(GeoResultSchema).optional(),
});

const CurrentWeatherSchema = z.object({
  temperature_2m: z.number(),
  apparent_temperature: z.number(),
  relative_humidity_2m: z.number(),
  weather_code: z.number(),
  wind_speed_10m: z.number(),
  wind_direction_10m: z.number(),
});

const WeatherResponseSchema = z.object({
  current: CurrentWeatherSchema.optional(),
});

type GeoResult = z.infer<typeof GeoResultSchema>;
type CurrentWeather = z.infer<typeof CurrentWeatherSchema>;

const cooldowns = new Map<string, number>();
const COOLDOWN_MS = 5_000;

function windDir(deg: number): string {
  return WIND_DIRS[Math.round(deg / 45) % 8];
}

function embedColor(code: number): number {
  if (code === 0 || code === 1) return 0xf9c74f;
  if (code <= 3)  return 0xa8dadc;
  if (code <= 55) return 0x8ecae6;
  if (code <= 67) return 0x219ebc;
  if (code <= 77) return 0xbde0fe;
  return 0x6a4c93;
}

async function geocode(city: string): Promise<GeoResult | null> {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;
  const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
  if (!res.ok) return null;
  const parsed = GeoResponseSchema.safeParse(await res.json());
  return parsed.success ? (parsed.data.results?.[0] ?? null) : null;
}

async function fetchWeather(lat: number, lon: number): Promise<CurrentWeather | null> {
  const params = new URLSearchParams({
    latitude: lat.toString(),
    longitude: lon.toString(),
    current: "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
    wind_speed_unit: "kmh",
    timezone: "auto",
  });
  const res = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`, {
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) return null;
  const parsed = WeatherResponseSchema.safeParse(await res.json());
  return parsed.success ? (parsed.data.current ?? null) : null;
}

export const weather: Command = {
  data: new SlashCommandBuilder()
    .setName("weather")
    .setDescription("Show current weather for a city")
    .addStringOption((opt) =>
      opt.setName("city").setDescription("City name").setRequired(true).setMaxLength(100)
    ) as SlashCommandBuilder,

  async execute(interaction) {
    const now = Date.now();
    const last = cooldowns.get(interaction.user.id) ?? 0;
    const remaining = COOLDOWN_MS - (now - last);
    if (remaining > 0) {
      await interaction.reply({
        content: `Please wait ${Math.ceil(remaining / 1000)}s before using this again.`,
        flags: MessageFlags.Ephemeral,
      });
      return;
    }
    cooldowns.set(interaction.user.id, now);

    const city = interaction.options.getString("city", true);
    await interaction.deferReply();

    const location = await geocode(city);
    if (!location) {
      await interaction.editReply({ content: `Could not find a location matching **${city}**.` });
      return;
    }

    const current = await fetchWeather(location.latitude, location.longitude);
    if (!current) {
      await interaction.editReply({ content: "Weather data unavailable right now. Try again later." });
      return;
    }

    const condition = WMO[current.weather_code] ?? { label: "Unknown", emoji: "🌡️" };
    const place = location.admin1
      ? `${location.name}, ${location.admin1}, ${location.country}`
      : `${location.name}, ${location.country}`;

    const embed = new EmbedBuilder()
      .setTitle(`${condition.emoji} ${place}`)
      .setColor(embedColor(current.weather_code))
      .setDescription(condition.label)
      .addFields(
        { name: "🌡️ Temperature", value: `${current.temperature_2m}°C (feels like ${current.apparent_temperature}°C)`, inline: true },
        { name: "💧 Humidity",    value: `${current.relative_humidity_2m}%`, inline: true },
        { name: "💨 Wind",        value: `${current.wind_speed_10m} km/h ${windDir(current.wind_direction_10m)}`, inline: true },
      )
      .setFooter({ text: "Open-Meteo" })
      .setTimestamp();

    await interaction.editReply({ embeds: [embed] });
  },
};
