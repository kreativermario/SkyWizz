import discord
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ =  "Help"

    @commands.command(name="help")
    async def help_command(self, ctx, *args):
        if not args:
            # No arguments provided, show general help
            help_embed = discord.Embed(
                title="Help",
                description=f"List of available commands:",
                color=discord.Color.blue()
            )

            # Group commands by cog name
            command_groups = {}
            for command in self.bot.commands:
                cog_name = command.cog.__cog_name__
                if cog_name not in command_groups:
                    command_groups[cog_name] = []
                command_groups[cog_name].append(command)

            # Add command fields to embed for each cog
            for cog_name, cog_commands in command_groups.items():
                command_list = [f"`{self.bot.command_prefix}{c.name}` - {c.short_doc}" for c in cog_commands if
                                c.enabled]
                if command_list:
                    help_embed.add_field(
                        name=cog_name,
                        value="\n".join(command_list),
                        inline=False
                    )

            help_embed.set_footer(text="Powered by SkyWizz")
            await ctx.send(embed=help_embed)


async def setup(bot):
    print("Loading Help...")
    await bot.add_cog(Help(bot))
