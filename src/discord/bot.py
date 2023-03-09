import discord
import os
import logging
from discord.ext import commands
from dotenv import load_dotenv


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()

class SkyWizzBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def load_cogs(self):
        # Load the extensions when the bot starts up
        print("Loading cogs...")
        for filename in os.listdir('cogs'):
            if filename.endswith('.py') and filename != "__init__.py":
                print(f"Loading extension: {filename}" )
                await bot.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.load_cogs()
        print("Finished loading cogs!")

        print("Guilds:")
        for guild in self.guilds:
            print(f"- {guild.name} ({guild.id})")

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)


intents = discord.Intents.all()
bot = SkyWizzBot(command_prefix='!', intents=intents)
bot.run(os.getenv('DISCORD_TOKEN'), log_handler=handler, log_level=logging.DEBUG)
