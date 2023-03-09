from discord.ext import commands
from src.utils.airport_functions import get_airport_info


class CommandsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(bot.command_prefix)

    @commands.command(name="ping", aliases=["pong"])
    async def ping(self, ctx):
        print("Received ping!")
        await ctx.send('Pong!')

    @commands.command(name="search", aliases=["s"])
    async def get_airport_info(self,ctx):
        print(ctx.message.content)
        print("Received search!")
        # Get the second word of the message, which should be the airport code
        airport_code = ctx.message.content.split(' ')[1 ]
        print(f"Received search request for airport code: {airport_code}")
        # Call API
        try:
            # Call API
            text = get_airport_info(airport_code)
        except Exception as e:
            # Handle the exception by displaying an error message
            text = f'Error fetching data: {str(e)}'
        await ctx.send(text)




async def setup(bot):
    print("Loading CommandsCog")
    await bot.add_cog(CommandsCog(bot))