import discord
from discord.ext import commands


class GeneralCommands(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "General Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='server')
    async def server_info(self, ctx):
        """
        Shows details about the current server

        **Usage:**
        - `server`
        """
        embed = discord.Embed(title=f"{ctx.guild.name} Info",
                              description="Information of this Server",
                              color=0x00ff00)
        embed.add_field(name='ℹ️Server ID', value=f"{ctx.guild.id}",
                        inline=True)
        embed.add_field(name='📆Created On',
                        value=ctx.guild.created_at.strftime("%b %d %Y"),
                        inline=True)
        embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}",
                        inline=True)
        embed.add_field(name='👥Members',
                        value=f'{ctx.guild.member_count} Members',
                        inline=True)
        embed.add_field(name='💬Channels',
                        value=f'{len(ctx.guild.text_channels)} Text | '
                              f'{len(ctx.guild.voice_channels)} Voice',
                        inline=True)
        embed.set_footer(text='Powered By SkyWizz')
        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(GeneralCommands(bot, logger))
