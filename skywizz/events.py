import json
import skywizz
import discord
from discord.ext import commands


def __init__(bot):
    """ Initialize events """
    message_send(bot)
    command_error(bot)


def command_error(bot):
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Cooldown",
                description=f"Slow down Speedy Gonzales! "
                            f"Please wait {error.retry_after:.2f} seconds before using that command again.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=skywizz.notfound(ctx.invoked_with))
            raise error


def message_send(bot):
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
