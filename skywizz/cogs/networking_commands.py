import discord
import subprocess
import emoji
from discord.ext import commands
from discord.ext.commands import BucketType
import skywizz
import skywizz.tools as tools
import skywizz.tools.embed as embd


class Networking(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = 'Networking'
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        """
        Shows the round-trip time of the bot's connection to Discord.

        **Usage:**
        - `ping`
        """
        # convert to milliseconds and round to whole number
        rtt = round(self.bot.latency * 1000)

        embed = embd.newembed(title="Pong!",
                              description=f"Round-trip time: {rtt} ms")

        await ctx.send(embed=embed)

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='whois')
    async def whois_command(self, ctx, *, domain: str):
        """
        Performs a WHOIS lookup for the specified domain.

        **Parameters:**
        - domain: The domain to lookup.

        **Example:**
        - `!whois google.com`

        **Usage:**
        - `whois <domain>`
        """
        # Display processing message
        processing_embed = embd.newembed(title='Processing...', description='',
                                         color=0xffd700)
        processing_embed.add_field(name='Message',
                                   value=f'Performing WHOIS lookup for `{domain}`...'
                                         'please wait...')
        processing_message = await ctx.send(embed=processing_embed)

        try:
            whois_data = await tools.whois_lookup(domain)
            # Limit the output to only the relevant fields
            if whois_data['country'].lower() != 'n/a':
                flag_emoji = emoji.emojize(f":flag_{whois_data['country'].lower()}:")
            else:
                flag_emoji = ''

            embed = embd.newembed(title=f"WHOIS lookup for {domain}",
                                  description='',
                                  color=0x7289DA)
            embed.add_field(name="Name", value=whois_data['name'],
                            inline=False)
            embed.add_field(name="Country", value=f"{flag_emoji} "
                                                  f"{whois_data['country']}",
                            inline=False)
            embed.add_field(name="Registrar", value=whois_data['registrar'],
                            inline=False)
            embed.add_field(name="Creation Date",
                            value=whois_data['creation_date'], inline=False)
            embed.add_field(name="Expiration Date",
                            value=whois_data['expiration_date'], inline=False)
            embed.add_field(name="Updated Date",
                            value=whois_data['last_updated'], inline=False)
            embed.add_field(name="Name Servers",
                            value="\n".join(whois_data['name_servers']),
                            inline=False)
            embed.set_footer(text=f'Requested by {ctx.author.display_name}')
            await processing_message.edit(content=None, embed=embed)
        except Exception as e:
            error_embed = skywizz.specific_error(f"An error occurred while "
                                                 f"performing a WHOIS lookup "
                                                 f"for `{domain}`.")
            error_embed.add_field(name="Error", value=str(e))
            await processing_message.edit(content=None, embed=error_embed)

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.command(name='traceroute', aliases=['tr'])
    async def traceroute_command(self, ctx, *args):
        """
        Traceroute command that performs a traceroute to a given host

        **Parameters:**
        - host: The IP address or domain name to trace route to

        **Example:**
        - `!traceroute 8.8.8.8`
        - `!traceroute google.com`

        **Usage:**
        - `traceroute <host>`
        """
        if not args:
            # Display error message if traceroute command failed
            error_embed = skywizz.specific_error('Please provide a host to '
                                                 'traceroute to')
            await ctx.send(embed=error_embed)
            return

        host = args[0]

        # Display processing message
        processing_embed = embd.newembed(title='Processing...',
                                         description='',
                                         color=0xffd700)
        processing_embed.add_field(name='Message',
                                   value='Performing traceroute, '
                                         'please wait...')
        processing_message = await ctx.send(embed=processing_embed)

        try:
            # Run traceroute command with timeout of 30 seconds
            traceroute_result = subprocess.check_output(
                ['traceroute', '-m', '15', '-n', '-q', '1', '-w', '2', host],
                timeout=30, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            # Display error message if traceroute command failed
            error_embed = skywizz.specific_error(f'Traceroute failed with '
                                                 f'error: {e}')
            await processing_message.edit(embed=error_embed)
            return
        except subprocess.TimeoutExpired:
            # Display message if traceroute command took too long
            timeout_embed = skywizz.specific_error('Traceroute took too long '
                                                   'and was cancelled')
            await processing_message.edit(embed=timeout_embed)
            return

        # Traceroute successful, create and send embed with results
        results_embed = embd.newembed(title=f'Traceroute to {host}',
                                      description='',
                                      color=0x00ff00)
        results_embed.add_field(name='Results:',
                                value=f'```{traceroute_result}```')
        await processing_message.edit(embed=results_embed)


async def setup(bot, logger):
    await bot.add_cog(Networking(bot, logger))
