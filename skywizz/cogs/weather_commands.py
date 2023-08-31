import discord
import requests
from discord.ext import commands
import skywizz
import skywizz.tools.exceptions
import skywizz.tools as tools
import skywizz.tools.embed as embd


class WeatherCommands(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Weather Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='forecast')
    async def forecast(self, ctx, city_name: str):
        """
        Shows forecast given a city

        **Usage:**
        - `forecast`
        """
        if city_name is None:
            # Display error message if user does not give a city
            error_embed = skywizz.specific_error('Please provide a city to get the forecast')
            await ctx.send(embed=error_embed)
            return

        latitude, longitude = await tools.get_coordinates(city_name)

        # Construct the API URL
        api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}" \
                  f"&longitude={longitude}" \
                  f"&daily=weathercode," \
                  f"temperature_2m_max," \
                  f"temperature_2m_min," \
                  f"apparent_temperature_max," \
                  f"apparent_temperature_min," \
                  f"sunrise," \
                  f"sunset," \
                  f"uv_index_max," \
                  f"uv_index_clear_sky_max," \
                  f"precipitation_sum," \
                  f"rain_sum," \
                  f"precipitation_hours," \
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

        # Process the JSON response as needed
        today_date = data['daily']['time'][0]
        sunrise = data['daily']['sunrise'][0]
        sunset = data['daily']['sunset'][0]
        max_uv_index = data['daily']['uv_index_max'][0]
        max_temperature = data['daily']['temperature_2m_max'][0]
        min_temperature = data['daily']['temperature_2m_min'][0]
        precipitation_prob = data['daily']['precipitation_probability_max'][0]

        embed = embd.newembed(title=f"Weather Forecast for {city_name.capitalize()}",
                              description=f"Here's the forecast for {today_date} 🌦️")

        embed.add_field(name="Sunrise", value=sunrise)
        embed.add_field(name="Sunset", value=sunset)
        embed.add_field(name="Max UV Index", value=max_uv_index)
        embed.add_field(name="🌡️Max Temperature", value=f"{max_temperature} °C")
        embed.add_field(name="Min Temperature", value=f"{min_temperature} °C")
        embed.add_field(name="Max Precipitation Probability", value=f"{precipitation_prob} %")

        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(WeatherCommands(bot, logger))
