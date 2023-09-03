import io

import discord
import requests
import emoji
from discord.ext import commands
import skywizz
import skywizz.tools.exceptions
import skywizz.tools as tools
import skywizz.tools.embed as embd


def create_forecast_embed(data, city, country, country_code, latitude, longitude):
    # Process the JSON response as needed
    today_date = data['daily']['time'][0]
    sunrise = data['daily']['sunrise'][0]
    sunset = data['daily']['sunset'][0]
    max_uv_index = data['daily']['uv_index_max'][0]
    max_temperature = data['daily']['temperature_2m_max'][0]
    min_temperature = data['daily']['temperature_2m_min'][0]
    precipitation_prob = data['daily']['precipitation_probability_max'][0]
    # Create flag emoji
    if country_code.lower() != 'n/a':
        flag_emoji = emoji.emojize(f":flag_{country_code.lower()}:")
    else:
        flag_emoji = ''

    embed = embd.newembed(title=f"Weather Forecast for {city}, {country}, "
                                f"{flag_emoji}",
                          description=f"Here's the forecast for {today_date} 🌦️")

    embed.add_field(name="GPS Coordinates",
                    value=f"`Latitude: {latitude}, "
                          f"Longitude: {longitude}`",
                    inline=False)
    embed.add_field(name="Sunrise", value=sunrise)
    embed.add_field(name="Sunset", value=sunset)
    embed.add_field(name="Max UV Index", value=max_uv_index)
    embed.add_field(name="🌡️Max Temperature", value=f"{max_temperature} °C")
    embed.add_field(name="Min Temperature", value=f"{min_temperature} °C")
    embed.add_field(name="Max Precipitation Probability", value=f"{precipitation_prob} %")

    # Get the map image URL
    map_image_url = tools.get_map_image_url(latitude, longitude)

    # Add the map image as a field in the embed
    embed.add_field(name="Map", value=f"[View Location]({map_image_url})")

    return embed


class WeatherCommands(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Weather Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='forecast')
    async def forecast(self, ctx, *, location):
        """
        Shows forecast given a city and optionally a country.

        **Parameters:**
        - location (str): city name, and optionally country (e.g., "Paris, France")

        **Example:**
        - `!forecast Paris, France`

        **Usage:**
        - `forecast <city_name>, <country (optional)>`
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
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}" \
                  f"&longitude={longitude}" \
                  f"&daily=weathercode," \
                  f"temperature_2m_max," \
                  f"temperature_2m_min," \
                  f"sunrise," \
                  f"sunset," \
                  f"uv_index_max," \
                  f"precipitation_sum," \
                  f"rain_sum," \
                  f"precipitation_probability_max," \
                  f"windspeed_10m_max," \
                  f"windgusts_10m_max," \
                  f"winddirection_10m_dominant" \
                  f"&timezone=auto"

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
