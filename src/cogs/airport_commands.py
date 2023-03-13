import discord
from discord.ext import commands
from .utils.airport_functions import distance_between_airports, get_airport_info

class AirportsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        print('Received ping!')
        await ctx.send('Pong!')

    @commands.command(name='search', aliases=['s'])
    async def get_airport_info(self, ctx):
        # Get the second word of the message, which should be the airport code
        # If no airport code is given, it will set airport_code to ''
        airport_code = ctx.message.content.split(' ')[1].upper() \
            if len(ctx.message.content.split(' ')) > 1 else ''
        if not airport_code:
            # Set the error message if no airport code is provided
            text = 'Please provide an airport code to search for.'
            color = discord.Color.red()
        else:
            try:
                # Call API
                text = get_airport_info(airport_code)
                color = discord.Color.blue()
            except Exception as e:
                # Handle the exception by displaying an error message
                text = f'Error fetching data: {str(e)}'
                color = discord.Color.red()

        embed = discord.Embed(
            title='Airport Information',
            description=text,
            color=color
        )
        embed.set_footer(text='Powered by SkyWizz')
        await ctx.send(embed=embed)

    @commands.command(name='distance', aliases=['d'])
    async def get_distance_between_airport(self, ctx):
        # Get the second word of the message, which should be the airport code
        depart_airport_code = ctx.message.content.split(' ')[1]
        arrival_airport_code = ctx.message.content.split(' ')[2]
        try:
            # Call API
            text = distance_between_airports(depart_airport_code,
                                             arrival_airport_code)
            color = discord.Color.blue()
        except Exception as e:
            # Handle the exception by displaying an error message
            text = f'Error fetching data: {str(e)}'
            color = discord.Color.red()

        embed = discord.Embed(
            title='Airport Information',
            description=text,
            color=color
        )

        await ctx.send(embed=embed)


async def setup(bot):
    print('Loading AirportsCog...')
    await bot.add_cog(AirportsCog(bot))
