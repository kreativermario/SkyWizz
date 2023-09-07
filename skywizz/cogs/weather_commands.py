import discord
import requests
import emoji
from discord.ext import commands
from datetime import datetime

import skywizz
import skywizz.tools.exceptions
import skywizz.tools as tools
import skywizz.tools.embed as embd


def create_forecast_embed(data: dict, city: str, country: str, country_code: str,
                          latitude: str, longitude: str):
    """
    Function that creates a weather forecast embed given API data

    Args:
        data: Open-meteo API weather data
        city: City name
        country: Country name
        country_code: Country code like US, FR, DE
        latitude: GPS latitude coordinates
        longitude: GPS longitude coordinates

    Returns:
        embed (discord.Embed): A discord embed with the weather data and relevant information

    """
    #TODO Raise custom exception if data empty or any field, or dont create field

    # Process the JSON response as needed
    weather_code = data['daily']['weathercode'][0]
    today_date = data['daily']['time'][0]
    sunrise = data['daily']['sunrise'][0]
    sunset = data['daily']['sunset'][0]
    # Assuming sunrise and sunset are in ISO 8601 format, e.g., '2023-09-03T05:35'
    sunrise_datetime = datetime.fromisoformat(sunrise)
    sunset_datetime = datetime.fromisoformat(sunset)
    sunrise_formatted = sunrise_datetime.strftime('%H:%M')
    sunset_formatted = sunset_datetime.strftime('%H:%M')
    max_uv_index = data['daily']['uv_index_max'][0]
    max_temperature = data['daily']['temperature_2m_max'][0]
    min_temperature = data['daily']['temperature_2m_min'][0]
    precipitation_sum = data['daily']['precipitation_sum'][0]
    precipitation_prob = data['daily']['precipitation_probability_max'][0]
    wind_speed_max = data['daily']['windspeed_10m_max'][0]
    wind_direction = data['daily']['winddirection_10m_dominant'][0]

    # Create flag emoji
    if country_code.lower() != 'n/a':
        flag_emoji = emoji.emojize(f":flag_{country_code.lower()}:")
    else:
        flag_emoji = ''

    weather_emoji, weather_description = tools.return_weather_emoji(weather_code)

    embed = embd.newembed(title="Weather Forecast",
                          description=f"Here's the forecast for {today_date}")
    embed.add_field(name="🌍 Location",
                    value=f"{city}, {country} {flag_emoji}",
                    inline=False)
    embed.add_field(name=f"{weather_emoji} Weather",
                    value=weather_description,
                    inline=False)
    embed.add_field(name="🌅 Sunrise",
                    value=sunrise_formatted)
    embed.add_field(name="🌇 Sunset",
                    value=sunset_formatted)
    embed.add_field(name="☀️ Max UV Index",
                    value=max_uv_index)
    embed.add_field(name="🌡️ Max Temperature",
                    value=f"{max_temperature} °C")
    embed.add_field(name="❄️ Min Temperature",
                    value=f"{min_temperature} °C")
    embed.add_field(name="🌬️ Max Wind Speed",
                    value=f"{wind_speed_max} km/h", )
    embed.add_field(name="🪁 Wind Direction", value=f"{wind_direction}º")
    embed.add_field(name="🌧️ Precipitation",
                    value=f"{precipitation_sum} mm", )
    embed.add_field(name="☔ Max Precipitation Probability",
                    value=f"{precipitation_prob} %", )
    embed.add_field(name="🛰️ GPS Coordinates",
                    value=f"`Latitude: {latitude}, "
                          f"Longitude: {longitude}`",
                    inline=False)
    # Get the map image URL
    map_image_url = tools.get_map_image_url(latitude, longitude)

    # Add the map image as a field in the embed
    embed.add_field(name="📌 Map", value=f"[View Location]({map_image_url})")

    return embed


class WeatherCommands(commands.Cog):
    """
        Class that holds weather commands
        This class extends `commands.Cog` from discord.

        Args:
            bot: Discord API client
            logger: Logger object for logging purposes

        Attributes:
            bot: Discord API client
            logger: Logger object for logging purposes
            hidden (bool): Attribute that determines if this list of
                     command should show in the help command or not.
                     If `false`, will show in help.
            __cog_name__ (str): Command designation for the help command
    """

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Weather Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='forecast')
    async def forecast(self, ctx, *, location: str):
        """
        Command that shows weather forecast given a city and optionally a country.

        Args:
            location: city name, and optionally country (e.g., "Paris, France")

        Example:
            `!forecast Paris, France`

        Usage:
            `forecast <city_name>, <country (optional)>`
        """
        # Split the location into city and country (if available)
        location_parts = location.split(',')
        if len(location_parts) < 1:
            # Display error message if user does not provide a location
            error_embed = skywizz.specific_error('Please provide a location '
                                                 'to get the forecast')
            await ctx.send(embed=error_embed)
            return

        city_name = location_parts[0].strip()
        country_name = location_parts[1].strip() if len(location_parts) > 1 else None

        try:
            latitude, longitude = await tools.get_coordinates(city_name=city_name,
                                                              country_name=country_name)
            city, country, country_code = await tools.reverse_gps(latitude, longitude)
            self.logger.debug(f"RETRIEVED: {city}, {country}, {country_code}")
        except Exception:
            # Display error message if API response fails
            error_embed = skywizz.error()
            await ctx.send(embed=error_embed)
            return

        # Construct the API URL
        api_url = f"https://api.open-meteo.com/v1/forecast?" \
                  f"latitude={latitude}" \
                  f"&longitude={longitude}" \
                  f"&daily=weathercode," \
                  f"temperature_2m_max," \
                  f"temperature_2m_min," \
                  f"sunrise,sunset," \
                  f"uv_index_max," \
                  f"precipitation_sum," \
                  f"precipitation_probability_max," \
                  f"windspeed_10m_max," \
                  f"winddirection_10m_dominant" \
                  f"&timezone=auto" \
                  f"&forecast_days=1"

        # Make the HTTP request
        response = requests.get(api_url)
        try:
            tools.check_request_status(response)
        except skywizz.tools.APIRequestError:
            # Display error message if API response fails
            error_embed = skywizz.specific_error('Oops! Looks like there '
                                                 'was an error fetching '
                                                 'weather information '
                                                 'for that city...')
            await ctx.send(embed=error_embed)
            return

        data = response.json()
        embed = create_forecast_embed(data, city, country, country_code,
                                      latitude, longitude)

        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(WeatherCommands(bot, logger))
