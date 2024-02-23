import discord
from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd


class GeneralCommands(commands.Cog):
    """
    Class that holds general commands about the bot or server
    Hosts commands such as server info.
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
        self.__cog_name__ = "General Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='server')
    async def server_info(self, ctx):
        """
        Command that shows details about the current server

        Usage:
            `!server`

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

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='botinfo')
    async def config_info(self, ctx):
        """
        Command that returns general information about the bot such as name,
        version, links, licenses, readme etc.

        Usage:
            !botinfo
        """
        embed = embd.newembed(title="Bot Information",
                              description="Information about SkyWizz")
        embed.add_field(name='📄 Description',
                        value='SkyWizz is a simple Discord bot project that'
                              ' was created in order to learn and improve how'
                              ' to program in Python and manage a medium to large'
                              ' project on GitHub. It was originally conceived'
                              ' around aviation APIs for flight tracking but has'
                              ' since pivoted to work with other free APIs such'
                              ' as Open-Meteo.')
        embed.add_field(name='⚙️ Version',
                        value=skywizz.version(),
                        inline=False)
        embed.add_field(name='📘 Documentation',
                        value='If you need help with documentation, check '
                              '[here]'
                              '(https://kreativermario.github.io/SkyWizz/).',
                        inline=False)
        embed.add_field(name='🤖 APIs used',
                        value="[OpenMeteo](https://open-meteo.com/)"
                              " for weather related commands."
                              "\n[OpenStreetMaps](https://www.openstreetmap.org/)"
                              " for geocaching commands.")
        embed.add_field(name='📎 Links',
                        value='If you want to contribute or host this bot, check'
                              'our [GitHub](https://github.com/kreativermario/SkyWizz)',
                        inline=False)
        embed.set_image(url="https://camo.githubusercontent.com"
                            "/2f305caed27907586d74b24339a30ab5c285ea8a85c61"
                            "d43922b42117861d498"
                            "/68747470733a2f2f692e70696e696d672e636f6d2f"
                            "6f726967696e616c732f63382f34632f37612f63383"
                            "4633761383065363662393838646166653236376436"
                            "37626561366438352e6a7067")
        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(GeneralCommands(bot, logger))
