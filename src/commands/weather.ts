import { EmbedBuilder, MessageFlags, SlashCommandBuilder } from "discord.js";
import type { Command } from "./index.js";

const WMO: Record<number, { label: string; emoji: string }> = {
  0:  { label: "Clear sky",         emoji: "☀️" },
  1:  { label: "Mainly clear",      emoji: "🌤️" },
  2:  { label: "Partly cloudy",     emoji: "⛅" },
  3:  { label: "Overcast",          emoji: "☁️" },
  45: { label: "Fog",               emoji: "🌫️" },
  48: { label: "Icy fog",           emoji: "🌫️" },
  51: { label: "Light drizzle",     emoji: "🌦️" },
  53: { label: "Drizzle",           emoji: "🌦️" },
  55: { label: "Heavy drizzle",     emoji: "🌧️" },
  61: { label: "Light rain",        emoji: "🌧️" },
  63: { label: "Rain",              emoji: "🌧️" },
  65: { label: "Heavy rain",        emoji: "🌧️" },
  71: { label: "Light snow",        emoji: "🌨️" },
  73: { label: "Snow",              emoji: "❄️" },
  75: { label: "Heavy snow",        emoji: "❄️" },
  77: { label: "Snow grains",       emoji: "🌨️" },
  80: { label: "Light showers",     emoji: "🌦️" },
  81: { label: "Showers",           emoji: "🌧️" },
  82: { label: "Violent showers",   emoji: "⛈️" },
  85: { label: "Snow showers",      emoji: "🌨️" },
  86: { label: "Heavy snow showers",emoji: "❄️" },
  95: { label: "Thunderstorm",      emoji: "⛈️" },
  96: { label: "Thunderstorm + hail",emoji: "⛈️" },
  99: { label: "Thunderstorm + hail",emoji: "⛈️" },
};

const WIND_DIRS = ["N","NE","E","SE","S","SW","W","NW"];

function windDir(deg: number): string {
  return WIND_DIRS[Math.round(deg / 45) % 8];
}

function embedColor(code: number): number {
  if (code === 0 || code === 1) return 0xf9c74f;
  if (code <= 3) return 0xa8dadc;
  if (code <= 55) return 0x8ecae6;
  if (code <= 67) return 0x219ebc;
  if (code <= 77) return 0xbde0fe;
  return 0x6a4c93;
}

interface GeoResult {
  name: string;
  country: string;
  latitude: number;
  longitude: number;
  admin1?: string;
}

interface CurrentWeather {
  temperature_2m: number;
  apparent_temperature: number;
  relative_humidity_2m: number;
  weather_code: number;
  wind_speed_10m: number;
  wind_direction_10m: number;
}

async function geocode(city: string): Promise<GeoResult | null> {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;
  const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
  if (!res.ok) return null;
  const data = await res.json() as { results?: GeoResult[] };
  return data.results?.[0] ?? null;
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
  const data = await res.json() as { current?: CurrentWeather };
  return data.current ?? null;
}

export const weather: Command = {
  data: new SlashCommandBuilder()
    .setName("weather")
    .setDescription("Show current weather for a city")
    .addStringOption((opt) =>
      opt.setName("city").setDescription("City name").setRequired(true)
    ) as SlashCommandBuilder,

  async execute(interaction) {
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
        { name: "💧 Humidity", value: `${current.relative_humidity_2m}%`, inline: true },
        { name: "💨 Wind", value: `${current.wind_speed_10m} km/h ${windDir(current.wind_direction_10m)}`, inline: true },
      )
      .setFooter({ text: "Open-Meteo" })
      .setTimestamp();

    await interaction.editReply({ embeds: [embed] });
  },
};
