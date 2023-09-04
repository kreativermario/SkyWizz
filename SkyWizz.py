import os
import time
import logging
import colorlog

import discord
from discord.ext import commands
from dotenv import load_dotenv
from os.path import join, dirname
import skywizz

# Configure colorlog
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

# Set up logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)  # Add the file handler

# TODO handle if .env isn't available and call setup.py to initialize .env and ask user for input
load_dotenv(join(dirname(__file__), '.env'))

if os.getenv('CONFIG_VERSION') != skywizz.config_version():
    if os.path.isfile('.env'):
        logger.error("Missing environment variables. Please backup and delete .env, then run SkyWizz.py again.")
        quit(2)
    logger.warning("Unable to find required environment variables. Running setup.py...")  # if .env not found
    skywizz.setup.__init__()  # run setup.py

logger.info("Initializing bot...")
intents = discord.Intents.all()
intents.members = True
intents.typing = False
bot = commands.Bot(intents=intents, command_prefix=skywizz.config.bot_prefix(), help_command=None,
                   logger=logger)


@bot.event
async def on_ready():
    logger.info(f"Connected to Discord API in {round(time.perf_counter() - discord_time_start, 2)}s")
    time_start = time.perf_counter()
    # Load the extensions when the bot starts up
    logger.info('Loading cogs...')
    skywizz.events.__init__(bot)
    await skywizz.cogs.calculator_commands.setup(bot, logger)
    await skywizz.cogs.general_commands.setup(bot, logger)
    await skywizz.cogs.help_commands.setup(bot, logger)
    await skywizz.cogs.meme_commands.setup(bot, logger)
    await skywizz.cogs.networking_commands.setup(bot, logger)
    await skywizz.cogs.reminder_commands.setup(bot, logger)
    await skywizz.cogs.weather_commands.setup(bot, logger)
    logger.info(f"Registered commands and events in {round(time.perf_counter() - time_start, 2)}s")
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(skywizz.config.bot_status()))  # Update Bot status
    logger.info('Guilds:')
    for guild in bot.guilds:
        logger.info(f'- {guild.name} ({guild.id})')


@bot.check
def global_cooldown_check(ctx):
    default_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)
    bucket = default_cooldown.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after)
    return True


try:
    discord_time_start = time.perf_counter()
    bot.run(skywizz.config.bot_token(), log_handler=handler,
            log_level=logging.DEBUG)
except Exception as e:
    logger.error(f"[/!\\] Error: Failed to connect to DiscordAPI. "
                 f"Please check your bot token in .env file!\n{e}")
    time.sleep(5)
    exit(1)
