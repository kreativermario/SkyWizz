import discord
import subprocess
from discord.ext import commands


class Networking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ = 'Networking'

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
            error_embed.set_footer(text='Powered by SkyWizz')
            await ctx.send(embed=error_embed)
            return

        host = args[0]

        # Display processing message
        processing_embed = discord.Embed(title='Processing...', color=0xffd700)
        processing_embed.add_field(name='Message',
                                   value='Performing traceroute, '
                                         'please wait...')
        processing_embed.set_footer(text='Powered by SkyWizz')
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
            error_embed.set_footer(text='Powered by SkyWizz')
            await processing_message.edit(embed=error_embed)
            return
        except subprocess.TimeoutExpired:
            # Display message if traceroute command took too long
            timeout_embed = discord.Embed(title='Timeout', color=0xff0000)
            timeout_embed.add_field(name='Message',
                        value=f'Traceroute took too long and was cancelled')
            timeout_embed.set_footer(text='Powered by SkyWizz')
            await processing_message.edit(embed=timeout_embed)
            return

        # Traceroute successful, create and send embed with results
        results_embed = discord.Embed(title=f'Traceroute to {host}',
                                      color=0x00ff00)
        results_embed.add_field(name='Results:',
                                value=f'```{traceroute_result}```')
        results_embed.set_footer(text='Powered by SkyWizz')
        await processing_message.edit(embed=results_embed)


async def setup(bot):
    print('Loading Networking...')
    await bot.add_cog(Networking(bot))
