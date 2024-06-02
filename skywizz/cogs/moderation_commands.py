import discord
from discord.ext import commands
import skywizz
import skywizz.tools.embed as embd
import time


class ModerationCommands(commands.Cog):
    """
    Class that holds moderation commands

    Args:
        bot: Discord API client
        logger: Logger object for logging purposes

    Attributes:
        bot: Discord API client
        logger: Logger object for logging purposes
        hidden (bool): Attribute that determines if this list of
                 command should show in the help command or not.
                 If `false`, will show in help.
        __cog_name__ (str): Command designation for the help command
    """

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Moderation Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    async def send_embed(self, ctx, title, description, fields=None):
        embed = embd.newembed(title=title, description=description)
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @commands.command(name='kick', help="Kick a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason=None):
        """
        Command to kick a member from the server.

        Usage:
            !kick <member> [reason]

        Parameters:
            member: The member to kick.
            reason: The reason for kicking the member (optional).
        """
        await member.kick(reason=reason)
        await self.send_embed(ctx, "Kick", f"{member.display_name} has been kicked. :boot:",
                              [("Reason", reason, False) if reason else ("Reason", "No reason provided", False)])

    @commands.command(name='ban', help="Ban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        """
        Command to ban a member from the server.

        Usage:
            !ban <member> [reason]

        Parameters:
            member: The member to ban.
            reason: The reason for banning the member (optional).
        """
        await member.ban(reason=reason)
        await self.send_embed(ctx, "Ban", f"{member.display_name} has been banned. :hammer:",
                              [("Reason", reason, False) if reason else ("Reason", "No reason provided", False)])

    @commands.command(name='unban', help="Unban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, *, member):
        """
        Command to unban a member from the server.

        Usage:
            !unban <member>

        Parameters:
            member: The member to unban (format: username#discriminator).
        """
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await self.send_embed(ctx, "Unban", f"{user.display_name} has been unbanned. :unlock:")
                return

    @commands.command(name='purge', help="Purge a specified number of messages from the channel.")
    @commands.has_permissions(manage_messages=True)
    async def purge_messages(self, ctx, limit: int):
        """
        Command to purge a specified number of messages from the channel.

        Usage:
            !purge <limit>

        Parameters:
            limit: The number of messages to purge.
        """
        await ctx.channel.purge(limit=limit + 1)  # Add 1 to account for the command message
        await self.send_embed(ctx, "Purge", f"{limit} messages have been purged. :wastebasket:")

    @kick_member.error
    async def kick_member_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.send_embed(ctx, "Kick Error", "You don't have permission to kick members.")

    @ban_member.error
    async def ban_member_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.send_embed(ctx, "Ban Error", "You don't have permission to ban members.")

    @unban_member.error
    async def unban_member_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.send_embed(ctx, "Unban Error", "You don't have permission to unban members.")

    @purge_messages.error
    async def purge_messages_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.send_embed(ctx, "Purge Error", "You don't have permission to manage messages.")


async def setup(bot, logger):
    await bot.add_cog(ModerationCommands(bot, logger))
