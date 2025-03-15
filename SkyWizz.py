# Imported modules
import os
import time
import discord
import asyncio
import importlib
import pkgutil
from discord.ext import commands
from dotenv import load_dotenv
from os.path import join, dirname

# Custom modules
import skywizz
from skywizz.logger import logger

# Load environment variables
env_path = join(dirname(__file__), '.env')
if not os.path.exists(env_path):
    logger.warning("Unable to find .env file. Running setup.py...")
    skywizz.setup.__init__()  # Run setup.py if .env is missing
else:
    load_dotenv(env_path)

# Validate Configuration
if os.getenv('CONFIG_VERSION') != skywizz.config_version():
    if os.path.isfile('.env'):
        logger.error("Missing environment variables. Please backup and delete .env, then run SkyWizz.py again.")
        quit(2)
    logger.warning("Unable to find required environment variables. Running setup.py...")
    skywizz.setup.__init__()  # Run setup.py

# Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.typing = False
intents.message_content = True


bot = commands.Bot(
    command_prefix=skywizz.config.bot_prefix(),
    help_command=None,
    intents=intents
)


# Load Cogs Dynamically
async def load_cogs():
    try:
        for _, cog_name, _ in pkgutil.iter_modules(skywizz.cogs.__path__):
            cog_module = importlib.import_module(f"skywizz.cogs.{cog_name}")
            
            # Check if the module has a setup function
            if hasattr(cog_module, "setup") and callable(getattr(cog_module, "setup")):
                await cog_module.setup(bot, logger)
                logger.info(f"Loaded cog: {cog_name}")
            else:
                logger.warning(f"Skipping {cog_name}: No setup function found.")
                
        logger.info("All valid cogs loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load cogs: {e}")


@bot.event
async def on_ready():
    logger.info(f"Bot connected in {round(time.perf_counter() - bot.start_time, 2)}s")
    logger.info('Loading cogs...')
    await load_cogs()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(skywizz.config.bot_status())
    )
    logger.info(f"Connected to {len(bot.guilds)} guild(s).")


@bot.event
async def on_shutdown():
    await bot.close()
    logger.info("Bot is shutting down...")


@bot.check
def global_cooldown_check(ctx):
    cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)
    bucket = cooldown.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after)
    return True


# Run Bot
async def run_bot():
    bot.start_time = time.perf_counter()
    try:
        await bot.start(skywizz.config.bot_token())
    except discord.LoginFailure:
        logger.error("Invalid token. Check your .env file.")
    except Exception as e:
        logger.error(f"Discord API connection failed: {e}")
        await asyncio.sleep(5)
        exit(1)

if __name__ == "__main__":
    asyncio.run(run_bot())