from discord.ext import commands


class CommandsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(bot.command_prefix)

    @commands.command(name="ping", aliases=["pong"])
    async def ping(self, ctx):
        print("Received ping!")
        await ctx.send('Pong!')


async def setup(bot):
    print("Loading CommandsCog")
    await bot.add_cog(CommandsCog(bot))