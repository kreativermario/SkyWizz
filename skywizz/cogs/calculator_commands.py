import discord
from discord.ext import commands
import skywizz
import skywizz.tools as tools
import skywizz.tools.embed as embd


class CalculatorCommands(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Calculator Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='sum')
    async def sum_numbers(self, ctx, *args):
        """
        Command that sums two given numbers

        **Parameters:**
        - number1 (float): the first number
        - number2 (float): the second number

        **Example:**
        - `!sum 50 90`

        **Usage:**
        - `sum <number1> <number2>`
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                                valid_args=
                                                                '5, 4, 10, ...')
                await ctx.send(embed=error_embed)
                return

        text = str(sum(valid_numbers))
        embed = embd.newembed(title='Sum Result',
                              description=f'{ctx.author.mention} {text}')
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='product', aliases=['prod'])
    async def multiply(self, ctx, *args):
        """
        Command that multiplies two numbers

        **Parameters:**
        - number1 (float): the first number
        - number2 (float): the second number

        **Example:**
        - `!product 50 10`

        **Usage:**
        - `product <number1> <number2>`
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                                valid_args=
                                                                '5, 4, 10, ...')
                await ctx.send(embed=error_embed)
                return

        text = str(tools.product(valid_numbers))
        embed = embd.newembed(title='Product Result',
                              description=f'{ctx.author.mention} {text}')
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='subtract')
    async def subtract_numbers(self, ctx, *args):
        """
        Command that subtracts one number from another

         **Parameters:**
        - number1 (float): the first number
        - number2 (float): the second number

        **Example:**
        - `!subtract 50 10.5`

        **Usage:**
        - `subtract <number1> <number2>`
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                                valid_args=
                                                                '5, 4, 10, ...')
                await ctx.send(embed=error_embed)
                return

        text = str(tools.subtract(valid_numbers))
        embed = embd.newembed(title='Subtraction Result',
                              description=f'{ctx.author.mention} {text}')

        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(CalculatorCommands(bot, logger))
