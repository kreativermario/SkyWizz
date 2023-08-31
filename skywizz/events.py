import json
import skywizz
import discord


def __init__(bot):
    """ Initialize events """
    message_send(bot)


def message_send(bot):
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)


