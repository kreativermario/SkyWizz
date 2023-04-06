import discord
from discord.ext import commands


class GeneralCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ = "General Commands"

    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        """
        Shows the round-trip time of the bot's connection to Discord.
        """
        print('Received ping!')
        # convert to milliseconds and round to whole number
        rtt = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="Pong!",
            description=f"Round-trip time: {rtt} ms",
            color=discord.Color.green()
        )
        embed.set_footer(text="Powered by SkyWizz")

        await ctx.send(embed=embed)


async def setup(bot):
    print('Loading AirportsCog...')
    await bot.add_cog(GeneralCommands(bot))
