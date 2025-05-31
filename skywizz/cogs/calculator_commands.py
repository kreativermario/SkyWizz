from discord.ext import commands
import skywizz
import skywizz.tools as tools
import skywizz.tools.embed as embd


class CalculatorCommands(commands.Cog):
    """
    CalculatorCommands cog provides basic arithmetic operations:
    sum, multiplication, and subtraction.

    Args:
        bot: Discord API client
        logger: Logger object for logging purposes

    Attributes:
        bot: Discord API client
        logger: Logger object for logging purposes
        hidden (bool): Determines if this list of commands should show in the help command.
        __cog_name__ (str): Name for the help command.
    """

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = "Calculator Commands"
        self.logger.info(f"Loaded {self.__cog_name__}")

    async def _parse_arguments(self, ctx, args, operation_name):
        """
        Helper function to validate and parse numeric arguments.

        Args:
            ctx: The command context.
            args: List of arguments received from the command.
            operation_name: The name of the operation (for error messages).

        Returns:
            List of valid numbers or None (if an error occurs).
        """
        if len(args) < 2:
            missing_args_embed = skywizz.messages.missing_argument(
                expected="At least two numbers",
                recommendation=f"{operation_name} <number1> <number2> <...>"
            )
            await ctx.send(embed=missing_args_embed)
            return None

        valid_numbers = []
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                error_embed = skywizz.messages.invalid_argument(
                    given_arg=arg, valid_args="5, 4, 10, ..."
                )
                await ctx.send(embed=error_embed)
                return None

        return valid_numbers

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name="sum")
    async def sum_numbers(self, ctx, *args):
        """
        Adds two or more numbers.

        Example:
            `!sum 50 90`

        Usage:
            `sum <number1> <number2> <...>`
        """
        valid_numbers = await self._parse_arguments(ctx, args, "sum")
        if valid_numbers is None:
            return

        result = sum(valid_numbers)
        embed = embd.newembed(title="Sum Result", description=f"{ctx.author.mention} {result}")
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name="product", aliases=["prod"])
    async def multiply_numbers(self, ctx, *args):
        """
        Multiplies two or more numbers.

        Example:
            `!product 50 10`

        Usage:
            `product <number1> <number2> <...>`
        """
        valid_numbers = await self._parse_arguments(ctx, args, "product")
        if valid_numbers is None:
            return

        result = tools.product(valid_numbers)
        embed = embd.newembed(title="Product Result", description=f"{ctx.author.mention} {result}")
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name="subtract")
    async def subtract_numbers(self, ctx, *args):
        """
        Subtracts multiple numbers from the first number.

        Example:
            `!subtract 50 10.5`

        Usage:
            `subtract <number1> <number2> <...>`
        """
        valid_numbers = await self._parse_arguments(ctx, args, "subtract")
        if valid_numbers is None:
            return

        result = tools.subtract(valid_numbers)
        embed = embd.newembed(title="Subtraction Result", description=f"{ctx.author.mention} {result}")
        await ctx.send(embed=embed)


async def setup(bot, logger):
    await bot.add_cog(CalculatorCommands(bot, logger))
