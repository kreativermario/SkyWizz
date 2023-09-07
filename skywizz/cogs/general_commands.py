import discord
from discord.ext import commands
import skywizz.tools.embed as embd


class GeneralCommands(commands.Cog):
    """
    Class that holds general commands about the bot or server
    Hosts commands such as server info.
    This class extends `commands.Cog` from discord.

    **Args:**
        bot: Discord API client
        logger: Logger object for logging purposes

    **Attributes:**
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
        self.__cog_name__ = "General Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='server')
    async def server_info(self, ctx):
        """
        Command that shows details about the current server

        **Usage:**
            `!server`

        **Returns:**
            Embed with server information

        """
        embed = embd.newembed(title=f"{ctx.guild.name} Info",
                              description="Information of this Server")
        embed.add_field(name='ℹ️Server ID', value=f"{ctx.guild.id}",
                        inline=True)
        embed.add_field(name='📆Created On',
                        value=ctx.guild.created_at.strftime("%b %d %Y"),
                        inline=True)
        embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}",
                        inline=True)
        embed.add_field(name='👥Members',
                        value=f'{ctx.guild.member_count} Members',
                        inline=False)
        embed.add_field(name='💬Channels',
                        value=f'{len(ctx.guild.text_channels)} Text | '
                              f'{len(ctx.guild.voice_channels)} Voice',
                        inline=False)
        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(GeneralCommands(bot, logger))
