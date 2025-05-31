from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd


class GeneralCommands(commands.Cog):
    """
    Class that holds general commands
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


async def setup(bot, logger):
    await bot.add_cog(GeneralCommands(bot, logger))
