# import discord
# from discord.ext import commands
# import asyncio
# from skywizz.db import deposit, withdraw, get_banks, bank_account_exists, create_bank_account, update_bank_balance, get_bank_accounts, get_cash_balance, get_bank_balance, get_bank_id_by_name
# from skywizz.tools import embed as embd
# from discord.ext.commands import Paginator

# class BankCommands(commands.Cog):
#     """
#     Class that holds the commands related to bank functions.
#     This class extends `commands.Cog` from discord.

#     Args:
#         bot: Discord API client
#         logger: Logger object for logging purposes
#         db_conn: SQLite database connection

#     Attributes:
#         bot: Discord API client
#         logger: Logger object for logging purposes
#         db_conn: SQLite database connection
#         hidden (bool): Attribute that determines if this list of
#                  command should show in the help command or not.
#                  If `false`, will show in help.
#         __cog_name__ (str): Command designation for the help command
#     """

#     def __init__(self, bot, logger, db_conn):
#         self.bot = bot
#         self.logger = logger
#         self.db_conn = db_conn
#         self.hidden = False
#         self.__cog_name__ = "Bank Commands"
#         self.logger.info(f"Loaded {self.__cog_name__}")

#     async def send_embed(self, ctx, title, description, color, emoji, fields=None):
#         embed = embd.newembed(title=f"{emoji} {title}", description=description, color=color)
#         if fields:
#             for name, value, inline in fields:
#                 embed.add_field(name=name, value=value, inline=inline)
#         return await ctx.send(embed=embed)

#     @commands.command(name='deposit')
#     async def deposit_command(self, ctx, bank_name: str, amount: float):
#         """
#         Command to deposit money into the bank.
#         """
#         user_id = ctx.author.id
        
#         if amount <= 0:
#             await self.send_embed(ctx, "Deposit", "Please enter a valid amount to deposit.", 0xFF0000, "❌")
#             return
        
#         cash_balance = get_cash_balance(self.db_conn, user_id)
#         if cash_balance is None or cash_balance < amount:
#             await self.send_embed(ctx, "Deposit", "Insufficient cash balance.", 0xFF0000, "❌")
#             return
        
#         if bank_name:
#             matched_banks = [(bank_id, name, account_type) for bank_id, name, _, account_type, _, _, _ in get_banks(self.db_conn) if bank_name.lower() in name.lower()]
#             if not matched_banks:
#                 await self.send_embed(ctx, "Deposit", f"No banks found matching '{bank_name}'.", 0xFF0000, "❌")
#                 return
#             elif len(matched_banks) == 1:
#                 bank_id, bank_name, _ = matched_banks[0]
#                 if deposit(self.db_conn, user_id, bank_id, amount):
#                     await self.send_embed(ctx, "Deposit", f"Successfully deposited {amount} into '{bank_name}'.", 0x00FF00, "✅")
#                 else:
#                     await self.send_embed(ctx, "Deposit", "Failed to deposit. Please try again.", 0xFF0000, "❌")
#             else:
#                 bank_names = [f"{index + 1}. {name}" for index, (_, name, _) in enumerate(matched_banks)]
#                 await self.send_embed(ctx, "Deposit", f"Multiple banks found matching '{bank_name}'. Please choose one:\n" + "\n".join(bank_names), 0x00FF00, "ℹ️")
#                 try:
#                     response = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
#                     selected_index = int(response.content) - 1
#                     if selected_index < 0 or selected_index >= len(matched_banks):
#                         await self.send_embed(ctx, "Deposit", "Invalid selection.", 0xFF0000, "❌")
#                         return
#                     bank_id, bank_name, _ = matched_banks[selected_index]
#                     if deposit(self.db_conn, user_id, bank_id, amount):
#                         await self.send_embed(ctx, "Deposit", f"Successfully deposited {amount} into '{matched_banks[selected_index][1]}'.", 0x00FF00, "✅")
#                     else:
#                         await self.send_embed(ctx, "Deposit", "Failed to deposit. Please try again.", 0xFF0000, "❌")
#                 except asyncio.TimeoutError:
#                     await self.send_embed(ctx, "Deposit", "No response received. Please try again.", 0xFF0000, "❌")
#                     return
#                 except ValueError:
#                     await self.send_embed(ctx, "Deposit", "Invalid selection.", 0xFF0000, "❌")
#                     return
#         else:
#             await self.send_embed(ctx, "Deposit", "Please specify the bank in which you want to deposit.", 0xFF0000, "❌")
#             return

#     @commands.command(name='withdraw')
#     async def withdraw_command(self, ctx, bank_name: str, amount: float):
#         """
#         Command to withdraw money from the bank.
#         """
#         user_id = ctx.author.id
        
#         if amount <= 0:
#             await self.send_embed(ctx, "Withdraw", "Please enter a valid amount to withdraw.", 0xFF0000, "❌")
#             return
        
#         if bank_name:
#             matched_banks = [(bank_id, name, account_type) for bank_id, name, _, account_type, _, _, _ in get_banks(self.db_conn) if bank_name.lower() in name.lower()]
#             if not matched_banks:
#                 await self.send_embed(ctx, "Withdraw", f"No banks found matching '{bank_name}'.", 0xFF0000, "❌")
#                 return
#             elif len(matched_banks) == 1:
#                 bank_id, bank_name, _ = matched_banks[0]
#                 if withdraw(self.db_conn, user_id, bank_id, amount):
#                     await self.send_embed(ctx, "Withdraw", f"Successfully withdrew {amount} from '{bank_name}'.", 0x00FF00, "✅")
#                 else:
#                     await self.send_embed(ctx, "Withdraw", "Failed to withdraw. Please try again.", 0xFF0000, "❌")
#             else:
#                 bank_names = [f"{index + 1}. {name}" for index, (_, name, _) in enumerate(matched_banks)]
#                 await self.send_embed(ctx, "Withdraw", f"Multiple banks found matching '{bank_name}'. Please choose one:\n" + "\n".join(bank_names), 0x00FF00, "ℹ️")
#                 try:
#                     response = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
#                     selected_index = int(response.content) - 1
#                     if selected_index < 0 or selected_index >= len(matched_banks):
#                         await self.send_embed(ctx, "Withdraw", "Invalid selection.", 0xFF0000, "❌")
#                         return
#                     bank_id, _, _ = matched_banks[selected_index]
#                     if withdraw(self.db_conn, user_id, bank_id, amount):
#                         await self.send_embed(ctx, "Withdraw", f"Successfully withdrew {amount} from '{matched_banks[selected_index][1]}'.", 0x00FF00, "✅")
#                     else:
#                         await self.send_embed(ctx, "Withdraw", "Failed to withdraw. Please try again.", 0xFF0000, "❌")
#                 except asyncio.TimeoutError:
#                     await self.send_embed(ctx, "Withdraw", "No response received. Please try again.", 0xFF0000, "❌")
#                     return
#                 except ValueError:
#                     await self.send_embed(ctx, "Withdraw", "Invalid selection.", 0xFF0000, "❌")
#                     return
#         else:
#             await self.send_embed(ctx, "Withdraw", "Please specify the bank from which you want to withdraw.", 0xFF0000, "❌")
#             return


#     @commands.command(name='banks')
#     async def banks_list_command(self, ctx, action=None, *, bank_name=None):
#         """
#         Command for banks

#         Usage:
#         !banks list - to list all banks
#         !banks create <bank_name> - to create a bank account

#         Parameters:
#         action: Action to perform (list or create)
#         bank_name: Name of the bank (required for create action)
#         """
#         if action == 'create' and bank_name:
#             await self.create_bank_account_command(ctx, bank_name)
#         else:
#             banks = get_banks(self.db_conn)

#         if not banks:
#             await ctx.send("No banks found.")
#             return

#         paginator = Paginator(prefix='', suffix='')
#         embeds = []

#         title_embed = embd.newembed(title="Banks List", description="List of banks available", color=0x00ff00)
#         embeds.append(title_embed)

#         for bank in banks:
#             bank_id, name, description, account_type, monthly_account_cost, annual_account_cost, country = bank
#             embed = embd.newembed(title=name, description=f"**Description:** {description}\n**Account Type:** {account_type}\n**Monthly Cost:** {monthly_account_cost} €\n**Annual Cost:** {annual_account_cost} €\n**Country:** {country}", color=0x00ff00)
#             embeds.append(embed)

#         current_page = 0
#         message = await ctx.send(embed = embeds[0])
#         await message.add_reaction('⬅️')
#         await message.add_reaction('➡️')
#         await message.add_reaction('❌')

#         def check(reaction, user):
#             return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '❌'] and reaction.message == message

#         while True:
#             try:
#                 reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
#             except asyncio.TimeoutError:
#                 break

#             if str(reaction.emoji) == '➡️':
#                 current_page = (current_page + 1) % len(embeds)
#             elif str(reaction.emoji) == '⬅️':
#                 current_page = (current_page - 1) % len(embeds)
#             elif str(reaction.emoji) == '❌':
#                 await message.delete()

#             if current_page == 0:
#                 await message.edit(embed=title_embed)
#             else:
#                 await message.edit(embed=embeds[current_page])

#             try:
#                 await message.remove_reaction(reaction, user)
#             except:
#                 pass


#     async def create_bank_account_command(self, ctx, bank_name_partial: str):
#         """
#         Command to create a bank account.

#         Usage:
#             !create_bank_account <bank_name_partial>

#         Parameters:
#             bank_name_partial: Partial name of the bank to create an account with.
#         """
#         user_id = ctx.author.id
        
#         # Get all bank names that partially match the provided input
#         matched_banks = [(bank_id, name, account_type) for bank_id, name, _, account_type, _, _, _ in get_banks(self.db_conn) if bank_name_partial.lower() in name.lower()]

#         if not matched_banks:
#             await self.send_embed(ctx, "Create Bank Account", "No banks found matching the provided input.", 0xFF0000, "❌")
#             return
        
#         # If only one bank matches, automatically create an account for it
#         if len(matched_banks) == 1:
#             bank_id, selected_bank_name, account_type = matched_banks[0]
#             create_bank_account(self.db_conn, user_id, bank_id, account_type)  # Defaulting to "Savings" account type
#             await self.send_embed(ctx, "Create Bank Account", f"Bank account created successfully at {selected_bank_name} bank.", 0x00FF00, "✅")
#             return
        
#         # If multiple banks match, prompt the user to choose one
#         bank_choices_str = "\n".join([f"{index + 1}. {bank[1]}" for index, bank in enumerate(matched_banks)])
#         prompt_message = f"Multiple banks found matching the provided input. Please choose one by typing its corresponding number:\n{bank_choices_str}"
        
#         await self.send_embed(ctx, "Create Bank Account", prompt_message, 0x00FF00, "ℹ️")
        
#         def check(message):
#             return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit() and 1 <= int(message.content) <= len(matched_banks)
        
#         try:
#             response = await self.bot.wait_for('message', check=check, timeout=30.0)
#             selected_bank_index = int(response.content) - 1
#             selected_bank_id, selected_bank_name, selected_bank_account_type = matched_banks[selected_bank_index]
#             create_bank_account(self.db_conn, user_id, selected_bank_id, selected_bank_account_type)  # Defaulting to "Savings" account type
#             await self.send_embed(ctx, "Create Bank Account", f"Bank account created successfully at {selected_bank_name} bank.", 0x00FF00, "✅")
#         except asyncio.TimeoutError:
#             await self.send_embed(ctx, "Create Bank Account", "No response received. Please try again.", 0xFF0000, "❌")
#         except Exception as e:
#             self.logger.error(f"Error during bank account creation: {e}")
#             await self.send_embed(ctx, "Create Bank Account", "Failed to create bank account. Please try again.", 0xFF0000, "❌")

#     @commands.command(name='balance', aliases=['bal'])
#     async def balance_command(self, ctx):
#         """
#         Command to check the balance.

#         Usage:
#             !balance

#         """
#         user_id = ctx.author.id
#         cash_balance = get_cash_balance(self.db_conn, user_id)
#         bank_accounts = get_bank_accounts(self.db_conn, user_id)

#         embed = embd.newembed(title="Balance", description='**Information**', color=0x00ff00)

#         if cash_balance is not None:
#             embed.add_field(name="💰 Cash Balance", value=f"{cash_balance} coins", inline=False)
#         else:
#             embed.add_field(name="💰 Cash Balance", value="None coins", inline=False)

#         if bank_accounts:
#             bank_balances_str = "\n".join([f"**🏦 {bank_name}**: {balance['balance']} coins (Type: {balance['account_type']})" for bank_name, balance in bank_accounts.items()])
#             embed.add_field(name="Bank Balances", value=bank_balances_str, inline=False)
#         else:
#             embed.add_field(name="Bank Balances", value="No bank accounts", inline=False)

#         await ctx.send(embed=embed)
            
# async def setup(bot, logger, db_conn):
#     await bot.add_cog(BankCommands(bot, logger, db_conn))
