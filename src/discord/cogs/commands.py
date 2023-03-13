import discord
from discord.ext import commands
from src.utils.airport_functions import get_airport_info, \
    distance_between_airports


class CommandsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(bot.command_prefix)

    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        print('Received ping!')
        await ctx.send('Pong!')

    @commands.command(name='sum_numbers', aliases=['somar'])
    async def sum_numbers(self, ctx, *args):
        valid_numbers = []
        color = discord.Color.blue()
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            text = 'No valid numbers provided!'
        else:
            text = str(sum(valid_numbers))

        embed = discord.Embed(
            title='Sum Result',
            description=text,
            color=color
        )
        embed.set_footer(text='Powered by SkyWizz')

        await ctx.send(embed=embed)


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
        except Exception as e:
            # Handle the exception by displaying an error message
            text = f'Error fetching data: {str(e)}'
        await ctx.send(text)


async def setup(bot):
    print('Loading CommandsCog')
    await bot.add_cog(CommandsCog(bot))
