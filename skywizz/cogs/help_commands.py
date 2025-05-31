from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd


class Help(commands.Cog):
    """
        Class that holds help commands that provide detailed help to the user
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
        self.hidden = False
        self.logger = logger
        self.__cog_name__ = "Help"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='help', aliases=['h'])
    async def help_command(self, ctx, *args):
        """
        Help command that lists the commands available

        Args:
            args (str, optional): The command name or alias

        Example:
            `!help`
            `!help search`

        Usage:
            `help <command_name>`
        """
        if args:
            await self._detailed_help(ctx, args[0])
        else:
            await self._default_help(ctx)

    async def _default_help(self, ctx):
        """
        Default help command layout
        """
        embed = embd.newembed(title='Command List')
        for cog in self.bot.cogs.values():
            if not cog.hidden:
                cog_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
                if cog_commands:
                    command_list = [f"`{cmd.name}`" + (f" (aliases: {' | '.join(cmd.aliases)})" if cmd.aliases else "")
                                    for cmd in cog_commands]
                    embed.add_field(name=cog.__cog_name__, value='\n'.join(command_list), inline=False)
        await ctx.send(embed=embed)

    async def _detailed_help(self, ctx, command_name):
        """
        Detailed help command

        Args:
            command_name (str): command corresponding to the argument
                                given by the user
        """
        command = self.bot.get_command(command_name)
        if not command:
            await ctx.send(embed=skywizz.error())
            return
        embed = embd.newembed(title=
                              f"{command.name.capitalize()} Command Help",
                              description=command.help)
        if command.aliases:
            embed.add_field(name='Aliases',
                            value=' | '.join(command.aliases),
                            inline=False)
        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(Help(bot, logger))
