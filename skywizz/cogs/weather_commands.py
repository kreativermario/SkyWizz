import os
import matplotlib.pyplot as plt
import pandas as pd
import discord
import emoji
from discord.ext import commands
from datetime import datetime

import skywizz
import skywizz.tools.exceptions
import skywizz.tools as tools
import skywizz.tools.embed as embd


def create_daily_forecast_embed(data: dict, city: str, country: str, country_code: str,
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
    def get_field(name, value, inline=True):
        return {"name": name, "value": value, "inline": inline}

    def format_time(iso_time):
        time = datetime.fromisoformat(iso_time)
        return time.strftime('%H:%M')

    daily = data['daily']

    fields = [
        get_field("🌍 Location", f"{city}, {country} {emoji.emojize(f':flag_{country_code.lower()}:')}"),
        get_field("🌅 Sunrise", format_time(daily['sunrise'][0])),
        get_field("🌇 Sunset", format_time(daily['sunset'][0])),
        get_field("☀️ Max UV Index", daily['uv_index_max'][0]),
        get_field("🌡️ Max Temperature", f"{daily['temperature_2m_max'][0]} °C"),
        get_field("❄️ Min Temperature", f"{daily['temperature_2m_min'][0]} °C"),
        get_field("🌬️ Max Wind Speed", f"{daily['windspeed_10m_max'][0]} km/h"),
        get_field("🪁 Wind Direction", f"{daily['winddirection_10m_dominant'][0]}º"),
        get_field("🌧️ Precipitation", f"{daily['precipitation_sum'][0]} mm"),
        get_field("☔ Max Precipitation Probability", f"{daily['precipitation_probability_max'][0]} %"),
        get_field("🛰️ GPS Coordinates", f"`Latitude: {latitude}, Longitude: {longitude}`", inline=False),
    ]

    weather_code = daily['weathercode'][0]
    weather_emoji, weather_description = tools.return_weather_emoji(weather_code)
    fields.insert(1, get_field(f"{weather_emoji} Weather", weather_description, inline=False))

    embed = embd.newembed(title="Weather Forecast",
                          description=f"Here's the forecast for {daily['time'][0]}")

    for field in fields:
        embed.add_field(**field)

    # Get the map image URL
    map_image_url = tools.get_map_image_url(latitude, longitude)
    embed.add_field(name="📌 Map", value=f"[View Location]({map_image_url})")

    return embed


def create_weekly_plot(user_id: str, data: dict, city: str, country: str,
                       country_code: str):
    """
    Function that creates the weekly (7 days) forecast plot with max temperature and
    min temperature

    Args:
        user_id: Unique discord user id of the user that requested the weekly forecast
        data: API data
        city: City name
        country: Country name
        country_code: Country code like FR, DE

    Returns:
        unique_filename (str): Unique filename for the plot
        embed (discord.Embed): Embed to be sent
    """
    # Create unique filename to not overwrite
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f'images/weekly_forecast_{user_id}_{timestamp}.png'

    # Create a DataFrame from the weather data
    weather_df = pd.DataFrame({
        'Day': data['daily']['time'],
        'Max Temp (°C)': data['daily']['temperature_2m_max'],
        'Min Temp (°C)': data['daily']['temperature_2m_min']
    })

    # Create a line plot using pandas with different line colors
    plt.figure(figsize=(12, 6))  # Increase figsize for more margin
    plt.plot(weather_df['Day'], weather_df['Max Temp (°C)'], marker='o',
             linestyle='-', color='red', label='Max Temperature')
    plt.plot(weather_df['Day'], weather_df['Min Temp (°C)'], marker='o',
             linestyle='-', color='blue', label='Min Temperature')

    # Adjust vertical positions for Max Temp values
    for i, max_temp in enumerate(weather_df['Max Temp (°C)']):
        plt.text(i, max_temp + 0.8, f"{max_temp}°C", ha='center', va='bottom')
    # Adjust vertical positions for Min Temp values
    for i, min_temp in enumerate(weather_df['Min Temp (°C)']):
        plt.text(i, min_temp - 0.8, f"{min_temp}°C", ha='center', va='top')

    plt.xlabel('Day')
    plt.ylabel('Temperature (°C)')
    plt.title(f'Weekly Temperature Forecast for {city}, {country}')

    plt.grid(True)

    # Place the legend slightly above the x-axis label with padding
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fancybox=True,
               shadow=True, ncol=2)

    # Add some padding to the graph bounds
    plt.margins(y=0.3)

    # Save the plot as an image
    plt.savefig(unique_filename, bbox_inches='tight')

    # Close the plot to free up resources
    plt.close()

    # Include the graph as an attachment in the Discord embed
    country_emoji = emoji.emojize(f':flag_{country_code.lower()}:')
    embed = embd.newembed(title=f"📡 Weekly Forecast for {city}, {country} "
                                f"{country_emoji}",
                          description="📈 Temperature graph for the week:")
    embed.set_image(url=f'attachment://{unique_filename}')

    return unique_filename, embed


async def daily_forecast(ctx, city: str, country: str, country_code: str,
                         latitude: str, longitude: str):
    """
    Function that fetches daily forecast data and returns to user

    Args:
        ctx: Discord context object
        city: City name
        country: Country name
        country_code: Country code like FR, DE
        latitude: GPS Latitude coordinates
        longitude: GPS longitude coordinates
    Raises:
        skywizz.tools.exceptions.APIRequestError: if API request fails

    """
    api_url = skywizz.tools.get_daily_forecast_api_url(latitude,
                                                       longitude)
    try:
        data = skywizz.tools.get_api_data(api_url)
        if data is None:
            raise skywizz.tools.exceptions.APIRequestError
    except skywizz.tools.exceptions.APIRequestError:
        # Display error message if API response fails
        error_embed = skywizz.specific_error('Oops! Looks like there '
                                             'was an error fetching '
                                             'weather information '
                                             'for that city...')
        await ctx.send(embed=error_embed)
        return
    embed = create_daily_forecast_embed(data, city, country, country_code,
                                        latitude, longitude)
    await ctx.send(embed=embed)


async def weekly_forecast(ctx, city: str, country: str, country_code: str,
                          latitude: str,longitude: str):
    """
    Function that handles weekly forecast

    Args:
        ctx: Discord context object
        city: City name
        country: Country name
        country_code: Country code like FR, DE
        latitude: GPS Latitude coordinates
        longitude: GPS longitude coordinates
    Raises:
        skywizz.tools.exceptions.APIRequestError: if API request fails

    """
    api_url = skywizz.tools.get_weekly_forecast_api_url(latitude,
                                                       longitude)
    try:
        data = skywizz.tools.get_api_data(api_url)
        if data is None:
            raise skywizz.tools.exceptions.APIRequestError
    except skywizz.tools.exceptions.APIRequestError:
        # Display error message if API response fails
        error_embed = skywizz.specific_error('Oops! Looks like there '
                                             'was an error fetching '
                                             'weather information '
                                             'for that city...')
        await ctx.send(embed=error_embed)
        return

    # Create a unique filename for the weekly graph
    user_id = ctx.author.id
    unique_filename, embed = create_weekly_plot(user_id=user_id,
                                                     data=data,
                                                     city=city,
                                                     country=country,
                                                     country_code=country_code)
    await ctx.send(embed=embed)
    # Send the embed with the graph as an attachment
    with open(unique_filename, 'rb') as plot_file:
        plot_file = discord.File(plot_file, filename=unique_filename)
        await ctx.send(file=plot_file)

    # Delete the image file after sending
    os.remove(unique_filename)


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
    async def forecast(self, ctx, forecast_type: str,  *, location: str):
        """
        Command that shows weather forecast given a city and optionally a country.

        Args:
            ctx: Discord context client
            forecast_type: Type of forecast `daily` /  `d` or `weekly` / `w`.
            location: city name, and optionally country (e.g., "Paris, France")

        Example:
            `!forecast daily Paris, France`
            `!forecast d Paris, France`
            `!forecast weekly New York City`
            `!forecast w New York City`

        Usage:
            `forecast <daily or weekly> <city_name>, <country (optional)>`
        """
        # Check if forecast type is valid
        if forecast_type.lower() not in ['d', 'daily', 'w', 'weekly']:
            # Display error message if user does not provide a valid argument
            error_embed = skywizz.invalid_argument(forecast_type,
                                                   'daily or weekly',
                                                   'Please use !help forecast if '
                                                   'you need further help.')
            await ctx.send(embed=error_embed)
            return

        # Split the location into city and country (if available)
        location_parts = location.split(',')
        if len(location_parts) < 1:
            # Display error message if user does not provide a location
            self.logger.error("No location provided")
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
        except Exception as e:
            # Display error message if API response fails
            self.logger.error(f"Failed to get coordinates for {city_name}, {country_name} - Error: {e}")
            error_embed = skywizz.error()
            await ctx.send(embed=error_embed)
            return

        # If daily forecast
        if forecast_type.lower() == 'daily' or forecast_type.lower() == 'd':
            await daily_forecast(ctx=ctx, city=city, country=country,
                                country_code=country_code,
                                latitude=latitude, longitude=longitude)
        # If weekly forecast
        elif forecast_type.lower() == 'weekly' or forecast_type.lower() == 'w':
            await weekly_forecast(ctx=ctx, city=city, country=country,
                                 country_code=country_code,
                                 latitude=latitude, longitude=longitude)


async def setup(bot, logger):
    await bot.add_cog(WeatherCommands(bot, logger))
