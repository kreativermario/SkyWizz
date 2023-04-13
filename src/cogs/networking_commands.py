import discord
import subprocess
import whois
from discord.ext import commands
from .utils.constants import FOOTER_TEXT


class Networking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ = 'Networking'

    @commands.command(name='ping', aliases=['pong'])
    async def ping(self, ctx):
        """
        Shows the round-trip time of the bot's connection to Discord.

        **Usage:**
        - `ping`
        """
        print('Received ping!')
        # convert to milliseconds and round to whole number
        rtt = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="Pong!",
            description=f"Round-trip time: {rtt} ms",
            color=discord.Color.green()
        )
        embed.set_footer(text=FOOTER_TEXT)

        await ctx.send(embed=embed)

    async def whois_lookup(self, domain):
        """
        Performs a WHOIS lookup for the specified domain.

        **Parameters:**
        - domain: The domain to lookup.

        **Returns:**
        - A dictionary containing the WHOIS data for the domain.
        """
        whois_data = whois.whois(domain)
        if isinstance(whois_data.expiration_date, list):
            expiration_date = whois_data.expiration_date[0]
        else:
            expiration_date = whois_data.expiration_date

        return {
            'registrar': whois_data.registrar,
            'creation_date': whois_data.creation_date.strftime(
                "%Y-%m-%d %H:%M:%S") if whois_data.creation_date is not None else 'N/A',
            'expiration_date': expiration_date.strftime("%Y-%m-%d %H:%M:%S") if expiration_date is not None else 'N/A',
            'last_updated': whois_data.last_updated.strftime(
                "%Y-%m-%d %H:%M:%S") if whois_data.last_updated is not None else 'N/A',
            'name_servers': whois_data.name_servers
        }

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
        processing_embed = discord.Embed(title='Processing...', color=0xffd700)
        processing_embed.add_field(name='Message',
                                   value=f'Performing WHOIS lookup for `{domain}`...'
                                         'please wait...')
        processing_embed.set_footer(text=FOOTER_TEXT)
        processing_message = await ctx.send(embed=processing_embed)

        try:
            whois_data = await self.whois_lookup(domain)
            # Limit the output to only the relevant fields
            embed = discord.Embed(title=f"WHOIS lookup for {domain}", color=0x7289DA)
            embed.add_field(name="Registrar", value=whois_data['registrar'], inline=False)
            embed.add_field(name="Creation Date", value=whois_data['creation_date'], inline=False)
            embed.add_field(name="Expiration Date", value=whois_data['expiration_date'], inline=False)
            embed.add_field(name="Updated Date", value=whois_data['last_updated'], inline=False)
            embed.add_field(name="Name Servers", value="\n".join(whois_data['name_servers']), inline=False)
            embed.set_footer(text=f'Requested by {ctx.author.display_name}')
            await processing_message.edit(content=None, embed=embed)
        except Exception as e:
            error_embed = discord.Embed(title="WHOIS Lookup Error",
                                        description=f"An error occurred while performing a WHOIS lookup for `{domain}`.",
                                        color=0xFF0000)
            error_embed.add_field(name="Error", value=str(e))
            await processing_message.edit(content=None, embed=error_embed)

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
            error_embed = discord.Embed(title='Error', color=0xff0000)
            error_embed.add_field(name='Message',
                                  value=f'Please provide a host to traceroute to')
            error_embed.set_footer(text=FOOTER_TEXT)
            await ctx.send(embed=error_embed)
            return

        host = args[0]

        # Display processing message
        processing_embed = discord.Embed(title='Processing...', color=0xffd700)
        processing_embed.add_field(name='Message',
                                   value='Performing traceroute, '
                                         'please wait...')
        processing_embed.set_footer(text=FOOTER_TEXT)
        processing_message = await ctx.send(embed=processing_embed)

        try:
            # Run traceroute command with timeout of 30 seconds
            traceroute_result = subprocess.check_output(
                ['traceroute', '-m', '15', '-n', '-q', '1', '-w', '2', host],
                timeout=30, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            # Display error message if traceroute command failed
            error_embed = discord.Embed(title='Error', color=0xff0000)
            error_embed.add_field(name='Message',
                                  value=f'Traceroute failed with error: {e}')
            error_embed.set_footer(text=FOOTER_TEXT)
            await processing_message.edit(embed=error_embed)
            return
        except subprocess.TimeoutExpired:
            # Display message if traceroute command took too long
            timeout_embed = discord.Embed(title='Timeout', color=0xff0000)
            timeout_embed.add_field(name='Message',
                                    value=f'Traceroute took too long and was cancelled')
            timeout_embed.set_footer(text=FOOTER_TEXT)
            await processing_message.edit(embed=timeout_embed)
            return

        # Traceroute successful, create and send embed with results
        results_embed = discord.Embed(title=f'Traceroute to {host}',
                                      color=0x00ff00)
        results_embed.add_field(name='Results:',
                                value=f'```{traceroute_result}```')
        results_embed.set_footer(text=FOOTER_TEXT)
        await processing_message.edit(embed=results_embed)


async def setup(bot):
    print('Loading Networking...')
    await bot.add_cog(Networking(bot))
