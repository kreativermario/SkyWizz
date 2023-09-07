import asyncio
import datetime

import discord
from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd


class Reminder(commands.Cog):
    """
        Class that holds reminder commands
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
        self.__cog_name__ = "Reminder Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='remindme')
    async def remindme_command(self, ctx, duration: int, *, message: str):
        """
        Command that sets a reminder for a specified duration from now.

        Args:
            duration: The duration of the reminder in minutes.
            message: The message to send as a reminder.

        Example:
            `!remindme 10 Take a break`
        """
        reminder_time = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=duration)

        embed = embd.newembed(title=f"Reminder: {message}",
                              description=f"Set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')} UTC.",
                              )
        embed.set_footer(text="Reminder set by {}".format(ctx.author.display_name))
        await ctx.send(embed=embed)

        await asyncio.sleep(duration * 60)
        feedback_embed = embd.newembed(title="Reminder",
                                       description=f"{message}")
        feedback_embed.set_footer(text="Reminder sent by {}".format(self.bot.user.display_name))
        await ctx.author.send(embed=feedback_embed)


async def setup(bot, logger):
    await bot.add_cog(Reminder(bot, logger))
