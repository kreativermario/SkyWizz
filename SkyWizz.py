import asyncio
import os
import time
import logging
from typing import Optional

import colorlog
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from os.path import join, dirname

# Local imports
import skywizz


class SkyWizzClient(commands.Bot):
    def __init__(self, *args, testing_guild_id: Optional[int] = None, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.testing_guild_id = testing_guild_id

    async def setup_hook(self) -> None:
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        logger = logging.getLogger('discord')
        time_start = time.perf_counter()
        # Load the extensions when the bot starts up
        skywizz.events.__init__(self)
        await skywizz.cogs.calculator_commands.setup(self)
        await skywizz.cogs.general_commands.setup(self)
        await skywizz.cogs.help_commands.setup(self)
        await skywizz.cogs.meme_commands.setup(self)
        await skywizz.cogs.networking_commands.setup(self)
        await skywizz.cogs.reminder_commands.setup(self)
        await skywizz.cogs.weather_commands.setup(self)
        logger.info(f"Registered commands and events in {round(time.perf_counter() - time_start, 2)}s")
        await self.change_presence(status=discord.Status.online,
                                  activity=discord.Game(skywizz.config.bot_status()))  # Update Bot status
        logger.info('Guilds:')
        for guild in self.guilds:
            logger.info(f'- {guild.name} ({guild.id})')


async def main():
    load_dotenv(join(dirname(__file__), '.env'))
    # Set up logger
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger.addHandler(handler)  # Add the file handler

    if os.getenv('CONFIG_VERSION') != skywizz.config_version():
        if os.path.isfile('.env'):
            logger.error("Missing environment variables. Please backup and delete .env, then run SkyWizz.py again.")
            quit(2)
        logger.warning("Unable to find required environment variables. Running setup.py...")  # if .env not found
        skywizz.setup.__init__()  # run setup.py

    logger.info("Initializing bot...")
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True
    intents.typing = False
    server_id = 1150788933798592552
    async with SkyWizzClient(command_prefix=skywizz.config.bot_prefix(),
                             intents=intents,
                             testing_guild_id=server_id,
                             logger=logger,
                             help_command=None) as bot:
        try:
            # bot.run(skywizz.config.bot_token(), log_handler=handler,
            #         log_level=logging.DEBUG)
            await bot.start(skywizz.config.bot_token())
        except Exception as e:
            logger.error(f"[/!\\] Error: Failed to connect to DiscordAPI. "
                         f"Please check your bot token in .env file!\n{e}")
            time.sleep(5)
            exit(1)

    @bot.check
    def global_cooldown_check(ctx):
        default_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)
        bucket = default_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True

asyncio.run(main())