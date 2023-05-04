import discord
import os
import sys
import logging
from discord.ext import commands
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
print(os.path.abspath(os.path.dirname(__file__)))

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()


async def load_cogs():
    # Load the extensions when the bot starts up
    print('Loading cogs...')
    for filename in os.listdir('cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            print(f'Loading extension: {filename}')
            await bot.load_extension(f'cogs.{filename[:-3]}')


class SkyWizzBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=None)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await load_cogs()
        print('Finished loading cogs!')

        print('Guilds:')
        for guild in self.guilds:
            print(f'- {guild.name} ({guild.id})')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)


intents = discord.Intents.all()
bot = SkyWizzBot(command_prefix='!', intents=intents)


@bot.check
def global_cooldown_check(ctx):
    default_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)
    bucket = default_cooldown.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after)
    return True


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
        raise error


bot.run(os.getenv('DISCORD_TOKEN'))

#        log_level=logging.DEBUG)
# bot.run(os.getenv('DISCORD_TOKEN'), log_handler=handler,
#        log_level=logging.DEBUG)
