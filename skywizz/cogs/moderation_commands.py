# import discord
# import sqlite3
# from discord.ext import commands
# import skywizz.tools.embed as embd
# import time


# class ModerationCommands(commands.Cog):
#     """
#     Class that holds moderation commands

#     Args:
#         bot: Discord API client
#         logger: Logger object for logging purposes

#     Attributes:
#         bot: Discord API client
#         logger: Logger object for logging purposes
#         hidden (bool): Attribute that determines if this list of
#                  command should show in the help command or not.
#                  If `false`, will show in help.
#         __cog_name__ (str): Command designation for the help command
#     """

#     def __init__(self, bot, logger, db_conn):
#         self.bot = bot
#         self.db_conn = db_conn
#         self.logger = logger
#         self.hidden = False
#         self.__cog_name__ = "Moderation Commands"
#         self.logger.info(f"Loaded {self.__cog_name__}")

#     async def send_embed(self, ctx, title, description, fields=None):
#         embed = embd.newembed(title=title, description=description)
#         if fields:
#             for name, value, inline in fields:
#                 embed.add_field(name=name, value=value, inline=inline)
#         await ctx.send(embed=embed)

#     @commands.command(name='kick')
#     @commands.has_permissions(kick_members=True)
#     async def kick_member(self, ctx, member: discord.Member, *, reason=None):
#         """
#         Command to kick a member from the server.

#         Usage:
#             !kick <member> [reason]

#         Parameters:
#             member: The member to kick.
#             reason: The reason for kicking the member (optional).
#         """
#         await member.kick(reason=reason)
#         await self.send_embed(ctx, "Kick", f"{member.display_name} has been kicked. :boot:",
#                               [("Reason", reason, False) if reason else ("Reason", "No reason provided", False)])

#     @commands.command(name='ban')
#     @commands.has_permissions(ban_members=True)
#     async def ban_member(self, ctx, member: discord.Member, *, reason=None):
#         """
#         Command to ban a member from the server.

#         Usage:
#             !ban <member> [reason]

#         Parameters:
#             member: The member to ban.
#             reason: The reason for banning the member (optional).
#         """
#         await member.ban(reason=reason)
#         await self.send_embed(ctx, "Ban", f"{member.display_name} has been banned. :hammer:",
#                               [("Reason", reason, False) if reason else ("Reason", "No reason provided", False)])

#     @commands.command(name='unban')
#     @commands.has_permissions(ban_members=True)
#     async def unban_member(self, ctx, *, member):
#         """
#         Command to unban a member from the server.

#         Usage:
#             !unban <member>

#         Parameters:
#             member: The member to unban (format: username#discriminator).
#         """
#         banned_users = await ctx.guild.bans()
#         member_name, member_discriminator = member.split('#')

#         for ban_entry in banned_users:
#             user = ban_entry.user

#             if (user.name, user.discriminator) == (member_name, member_discriminator):
#                 await ctx.guild.unban(user)
#                 await self.send_embed(ctx, "Unban", f"{user.display_name} has been unbanned. :unlock:")
#                 return

#     @commands.command(name='purge')
#     @commands.has_permissions(manage_messages=True)
#     async def purge_messages(self, ctx, limit: int):
#         """
#         Command to purge a specified number of messages from the channel.

#         Usage:
#             !purge <limit>

#         Parameters:
#             limit: The number of messages to purge.
#         """
#         await ctx.channel.purge(limit=limit + 1)  # Add 1 to account for the command message
#         await self.send_embed(ctx, "Purge", f"{limit} messages have been purged. :wastebasket:")
    
#     @commands.command(name='warn')
#     @commands.has_permissions(kick_members=True)
#     async def warn_member(self, ctx, member: discord.Member, *, reason=None):
#         """
#         Command to warn a member.

#         Usage:
#             !warn <member> [reason]

#         Parameters:
#             member: The member to warn.
#             reason: The reason for warning the member (optional).
#         """
#         try:
#             # Connect to the database
#             conn = self.db_conn
#             cursor = conn.cursor()

#             # Check if the user exists in the users table
#             cursor.execute('''SELECT id FROM users WHERE id = ?''', (member.id,))
#             user_exists = cursor.fetchone()

#             # If the user doesn't exist, insert their information into the table
#             if not user_exists:
#                 cursor.execute('''INSERT INTO users (id, username, discriminator)
#                                 VALUES (?, ?, ?)''', (member.id, member.name, member.discriminator))

#             # Insert the warning into the database with a timestamp
#             timestamp = int(time.time())
#             cursor.execute('''INSERT INTO warnings (user_id, moderator_id, guild_id, reason, timestamp)
#                             VALUES (?, ?, ?, ?, ?)''', (member.id, ctx.author.id, ctx.guild.id, reason, timestamp))

#             # Commit the changes
#             conn.commit()

#             # Inform the user about the warning
#             await self.send_embed(ctx, "Warning", f"{member.display_name} has been warned. :warning:",
#                                 [("Reason", reason, False) if reason else ("Reason", "No reason provided", False)])
#         except sqlite3.Error as e:
#             self.logger.error(f"SQLite error: {e}")
#             await ctx.send("An error occurred while processing the command.")


#     @commands.command(name='warnings')
#     @commands.has_permissions(kick_members=True)
#     async def view_warnings(self, ctx, member: discord.Member = None):
#         """
#         Command to view warnings for a member or all warnings in the guild.

#         Usage:
#             !warnings [member]

#         Parameters:
#             member: Optional. The member to view warnings for. If not provided, all warnings in the guild will be shown.
#         """
#         try:
#             # Connect to the database
#             conn = self.db_conn
#             cursor = conn.cursor()

#             if member is None:
#                 # Fetch all warnings in the guild and count warnings for each username
#                 cursor.execute('''SELECT u.username, COUNT(w.user_id) AS warning_count 
#                                 FROM warnings w
#                                 JOIN users u ON w.user_id = u.id
#                                 WHERE w.guild_id = ?
#                                 GROUP BY u.username''', (ctx.guild.id,))
#                 warnings = cursor.fetchall()
#                 # Display all warnings
#                 embed = embd.newembed(title="Guild Warnings", description="Count of warnings for each username")
#                 for warning in warnings:
#                     embed.add_field(name=warning[0], value=f"Warnings: {warning[1]}", inline=False)
#                 await ctx.send(embed=embed)
#             else:
#                 # Fetch warnings for the specified member
#                 cursor.execute('''SELECT reason, timestamp FROM warnings 
#                                 WHERE user_id = ? AND guild_id = ?''', (member.id, ctx.guild.id))
#                 member_warnings = cursor.fetchall()
#                 if not member_warnings:
#                     await ctx.send(f"No warnings found for {member.display_name}.")
#                 else:
#                     # Display warnings for the specified member
#                     embed = embd.newembed(title=f":warning: {member.display_name}'s Warnings",
#                                         description=f"All warnings for {member.display_name}")
#                     for warning in member_warnings:
#                         embed.add_field(name=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(warning[1])),
#                                         value=warning[0],
#                                         inline=False)
#                     await ctx.send(embed=embed)
#         except sqlite3.Error as e:
#             self.logger.error(f"SQLite error: {e}")
#             await ctx.send("An error occurred while processing the command.")


#     @commands.command(name='clearwarn')
#     @commands.has_permissions(kick_members=True) 
#     async def clear_warnings(self, ctx, member: discord.Member, num_warnings: int = None):
#         """
#         Command to clear warnings for a member.

#         Usage:
#             !clearwarn <member> [num_warnings]

#         Parameters:
#             member: The member to clear warnings for.
#             num_warnings: The number of warnings to remove (optional).
#                         If not provided, all warnings for the member will be cleared.
#         """
#         try:
#             # Connect to the database
#             conn = self.db_conn
#             cursor = conn.cursor()

#             # If num_warnings is not provided, clear all warnings for the member
#             if num_warnings is None:
#                 cursor.execute('''DELETE FROM warnings WHERE user_id = ?''', (member.id,))
#                 conn.commit()
#                 await self.send_embed(ctx, "Warnings Cleared", f"All warnings for {member.display_name} have been cleared.")
#             else:
#                 # Delete the specified number of warnings for the member
#                 cursor.execute('''SELECT id FROM warnings WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?''', (member.id, num_warnings))
#                 rows = cursor.fetchall()
#                 for row in rows:
#                     cursor.execute('''DELETE FROM warnings WHERE id = ?''', (row[0],))
#                 conn.commit()
#                 await self.send_embed(ctx, "Warnings Cleared", f"{num_warnings} warnings have been cleared for {member.display_name}.")
#         except sqlite3.Error as e:
#             self.logger.error(f"SQLite error: {e}")
#             await ctx.send("An error occurred while processing the command.")
        
#     @kick_member.error
#     async def kick_member_error(self, ctx, error):
#         if isinstance(error, commands.MissingPermissions):
#             await self.send_embed(ctx, "Kick Error", "You don't have permission to kick members.")

#     @ban_member.error
#     async def ban_member_error(self, ctx, error):
#         if isinstance(error, commands.MissingPermissions):
#             await self.send_embed(ctx, "Ban Error", "You don't have permission to ban members.")

#     @unban_member.error
#     async def unban_member_error(self, ctx, error):
#         if isinstance(error, commands.MissingPermissions):
#             await self.send_embed(ctx, "Unban Error", "You don't have permission to unban members.")

#     @purge_messages.error
#     async def purge_messages_error(self, ctx, error):
#         if isinstance(error, commands.MissingPermissions):
#             await self.send_embed(ctx, "Purge Error", "You don't have permission to manage messages.")


# async def setup(bot, logger, db_conn):
#     await bot.add_cog(ModerationCommands(bot, logger, db_conn))
