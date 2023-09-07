import discord
from discord.ext import commands
import skywizz
import skywizz.tools as tools
import skywizz.tools.embed as embd


class CalculatorCommands(commands.Cog):
    """
    Class that holds the commands related to calculator functions such as
    sum, multiply and subtract.
    This class extends `commands.Cog` from discord.

    **Args:**
        bot: Discord API client
        logger: Logger object for logging purposes

    **Attributes:**
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
        self.__cog_name__ = "Calculator Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='sum')
    async def sum_numbers(self, ctx, *args):
        """
        Command that sums two or more given numbers

        **Args:**
            *args (float): Variable length argument list, this means you can have multiple numbers, but must pass 2 numbers.

        **Example:**
            `!sum 50 90`

        **Usage:**
            `sum <number1> <number2> <...>`

        **Returns:**
            Returns an embed with the result

        **Raises:**
            InvalidArgument: If the given arguments are not numbers, will send
                            an error embed
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                            valid_args=
                                                            '5, 4, 10, ...')
            await ctx.send(embed=error_embed)
            return
        else:
            text = str(sum(valid_numbers))
        embed = embd.newembed(title='Sum Result',
                              description=f'{ctx.author.mention} {text}')
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='product', aliases=['prod'])
    async def multiply(self, ctx, *args):
        """
        Command that multiplies two or more numbers

        **Args:**
            *args (float): Variable length argument list. This means it receives multiple numbers but must pass 2 numbers minimum.

        **Example:**
            `!product 50 10`

        **Usage:**
            `product <number1> <number2> <...>`

        **Returns:**
            Returns an embed with the result

        **Raises:**
            InvalidArgument: if the arguments are not numbers, will send an error embed
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                            valid_args=
                                                            '5, 4, 10, ...')
            await ctx.send(embed=error_embed)
            return
        else:
            text = str(tools.product(valid_numbers))
        embed = embd.newembed(title='Product Result',
                              description=f'{ctx.author.mention} {text}')
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='subtract')
    async def subtract_numbers(self, ctx, *args):
        """
        Command that subtracts multiple numbers from another

         **Parameters:**
            *args (float): Variable length argument list. This means it receives multiple numbers but must receive atleast two.

        **Example:**
            `!subtract 50 10.5`

        **Usage:**
            `subtract <number1> <number2> <...>`

        **Returns:**
            An embed with the result

        **Raises:**
            InvalidArgument: if the arguments are not numbers
        """
        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            error_embed = skywizz.messages.invalid_argument(given_arg=args,
                                                            valid_args=
                                                            '5, 4, 10, ...')
            await ctx.send(embed=error_embed)
            return
        else:
            text = str(tools.subtract(valid_numbers))

        embed = embd.newembed(title='Subtraction Result',
                              description=f'{ctx.author.mention} {text}')

        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(CalculatorCommands(bot, logger))
