import discord
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ =  "Help"

    @commands.command(name='help', aliases=['h'])
    async def help_command(self, ctx, *args):
        if not args:
            # No args, show default help message
            prefix = self.bot.command_prefix
            embed = discord.Embed(title='Command List', color=0x00ff00)
            for cog in self.bot.cogs.values():
                # Filter out hidden cogs
                if not cog.hidden:
                    cog_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
                    if cog_commands:
                        command_list = [f"`{prefix}{cmd.name}`" + (
                            f" (aliases: {' | '.join(cmd.aliases)})" if cmd.aliases else "") + f"\n{cmd.help}" for cmd
                                        in cog_commands]
                        embed.add_field(name=cog.__cog_name__, value='\n'.join(command_list), inline=False)
        else:
            # Arg given, try to show detailed command help
            command = self.bot.get_command(args[0])
            if not command:
                await ctx.send(f"No command found for '{args[0]}'")
                return
            prefix = self.bot.command_prefix
            embed = discord.Embed(title=f"{command.name.capitalize()} Command Help", description=command.help,
                                  color=0x00ff00)
            if command.aliases:
                embed.add_field(name='Aliases', value=' | '.join(command.aliases), inline=False)
            if command.usage:
                embed.add_field(name='Usage', value=f"{prefix}{command.name} {command.usage}", inline=False)
        embed.set_footer(text="Powered by SkyWizz")
        await ctx.send(embed=embed)


async def setup(bot):
    print("Loading Help...")
    await bot.add_cog(Help(bot))
