import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        help_embed = discord.Embed(
            title="Help",
            description="List of available commands:",
            color=discord.Color.blue()
        )
        for command in self.bot.commands:
            help_embed.add_field(
                name=f"{self.bot.command_prefix}{command.name}",
                value=command.help,
                inline=False
            )
        await ctx.send(embed=help_embed)


async def setup(bot):
    print("Loading Help...")
    await bot.add_cog(HelpCog(bot))
