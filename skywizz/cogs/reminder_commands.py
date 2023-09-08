import asyncio
import datetime

import discord
from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd


class Reminder(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Reminder Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='remindme')
    async def remindme_command(self, ctx, duration: float, *, message: str = None):
        """
        Set a reminder for a specified duration from now.

        **Parameters:**
        - duration: The duration of the reminder in minutes.
        - message: The message to send as a reminder.

        **Example:**
        - `!remindme 10 Take a break`
        """

        # verifications
        #if no description provided
        if message is None:
            error_embed = skywizz.messages.invalid_argument(given_arg=("duration"),
                                                            valid_args=("duration", "message"),
                                                            recommendation="Try using a description")
            await ctx.send(embed=error_embed)
            return

        #if duration is too much
        minute_limit = 10080  # 7days
        if duration > minute_limit:
            error_embed = skywizz.messages.invalid_argument(given_arg=duration,
                                                            valid_args= f"Duration maximum limit is {minute_limit}",
                                                            recommendation= f"Try a number less than {minute_limit}")
            await ctx.send(embed=error_embed)
            return

        #valid arguments logic
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
