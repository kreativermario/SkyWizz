import discord
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ =  "Help"

    @commands.command(name='help', aliases=['h'])
    async def help_command(self, ctx, *args):
        """
        Help command that lists the commands available

        **Parameters:**
        - command_name: The command name or alias

        **Example:**
        - `!help`
        - `!help search`

        **Usage:**
        - `help <command_name>`
        """
        if not args:
            # No args, show default help message
            embed = discord.Embed(title='Command List', color=0x00ff00)
            for cog in self.bot.cogs.values():
                # Filter out hidden cogs
                if not cog.hidden:
                    cog_commands = [cmd for cmd in cog.get_commands()
                                    if not cmd.hidden]
                    if cog_commands:
                        command_list = [f"`{cmd.name}`" + (
                            f" (aliases: {' | '.join(cmd.aliases)})"
                            if cmd.aliases else "") for cmd in cog_commands]
                        embed.add_field(name=cog.__cog_name__,
                                        value='\n'.join(command_list),
                                        inline=False)
        elif len(args) == 1:
            # Arg given, try to show detailed command help
            command = self.bot.get_command(args[0])
            if not command:
                await ctx.send(f"No command found for '{args[0]}'")
                return
            embed = discord.Embed(title=
                                  f"{command.name.capitalize()} Command Help",
                                  description=command.help,
                                  color=0x00ff00)
            if command.aliases:
                embed.add_field(name='Aliases',
                                value=' | '.join(command.aliases),
                                inline=False)
        else:
            await ctx.send(f"Invalid number of arguments. "
                           f"Usage: `{self.bot.command_prefix}help [command]`")
            return
        embed.set_footer(text="Powered by SkyWizz")
        await ctx.send(embed=embed)


async def setup(bot):
    print("Loading Help...")
    await bot.add_cog(Help(bot))
