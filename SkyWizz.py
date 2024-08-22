import os
import time
import logging
import colorlog
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os.path import join, dirname
import skywizz

# Set up logger
def setup_logger():
    global handler
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

# Load environment variables and check configuration
def load_environment_variables(env_path):
    if not os.path.exists(env_path):
        logger.warning("Unable to find .env file. Running setup.py...")
        skywizz.setup.__init__()  # Run setup.py if .env is missing
    load_dotenv(env_path)

def check_config_version():
    if os.getenv('CONFIG_VERSION') != skywizz.config_version():
        if os.path.isfile('.env'):
            logger.error("Missing environment variables. Please backup and delete .env, then run SkyWizz.py again.")
            quit(2)
        logger.warning("Unable to find required environment variables. Running setup.py...")
        skywizz.setup.__init__()  # Run setup.py

# Initialize bot
def setup_bot():
    intents = discord.Intents.all()
    intents.members = True
    intents.typing = False

    bot_instance = commands.Bot(
        command_prefix=skywizz.config.bot_prefix(),
        help_command=None,
        intents=intents,
        logger=logger
    )
    return bot_instance

# Define global variables and bot instance
logger = setup_logger()
env_path = join(dirname(__file__), '.env')
load_environment_variables(env_path)
check_config_version()
bot = setup_bot()

# Define events and commands
@bot.event
async def on_ready():
    global discord_time_start
    logger.info(f"Connected to Discord API in {round(time.perf_counter() - discord_time_start, 2)}s")
    time_start = time.perf_counter()
    
    # Initialize SQLite
    db_conn = skywizz.db.initialize_database(logger)
    
    if db_conn is None:
        logger.error("Failed to connect to the database. Exiting bot.")
        exit(1)

    logger.info('Loading cogs...')
    await load_cogs(bot, db_conn)
    logger.info(f"Registered commands and events in {round(time.perf_counter() - time_start, 2)}s")
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(skywizz.config.bot_status())
    )
    
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

async def load_cogs(bot, db_conn):
    try:
        skywizz.events.__init__(bot)
        await skywizz.cogs.calculator_commands.setup(bot, logger)
        await skywizz.cogs.utility_commands.setup(bot, logger, discord_time_start)
        await skywizz.cogs.help_commands.setup(bot, logger)
        await skywizz.cogs.meme_commands.setup(bot, logger)
        await skywizz.cogs.networking_commands.setup(bot, logger)
        await skywizz.cogs.reminder_commands.setup(bot, logger)
        await skywizz.cogs.weather_commands.setup(bot, logger)
        await skywizz.cogs.moderation_commands.setup(bot, logger, db_conn)
        await skywizz.cogs.economy.bank.setup(bot, logger, db_conn)
    except Exception as e:
        logger.error(f"Failed to load cogs: {e}")
        exit(1)

def run_bot():
    global discord_time_start
    discord_time_start = time.perf_counter()
    try:
        bot.run(skywizz.config.bot_token(), log_handler=handler, log_level=logging.DEBUG)
    except discord.LoginFailure:
        logger.error("Invalid bot token. Please check your .env file!")
    except Exception as e:
        logger.error(f"Failed to connect to Discord API: {e}")
        time.sleep(5)
        exit(1)

if __name__ == "__main__":
    run_bot()
