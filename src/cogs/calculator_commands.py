import discord
from discord.ext import commands
from .utils.utility_functions import product, subtract


class CalculatorCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ = "Calculator Commands"
        print(bot.command_prefix)

    @commands.command(name='sum', aliases=['somar'])
    async def sum_numbers(self, ctx, *args):
        """
        Command that sums given numbers
        :param ctx:
        :param args:
        :return:
        """
        valid_numbers = []
        color = discord.Color.blue()
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            text = 'No valid numbers provided!'
        else:
            text = str(sum(valid_numbers))

        embed = discord.Embed(
            title='Sum Result',
            description=f'{ctx.author.mention} {text}',
            color=color
        )
        embed.set_footer(text='Powered by SkyWizz')

        await ctx.send(embed=embed)

    @commands.command(name='product', aliases=['multiplicar', 'multi',
                                               'prod'])
    async def multiply(self, ctx, *args):
        valid_numbers = []
        color = discord.Color.blue()
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            text = 'No valid numbers provided!'
        else:
            text = str(product(valid_numbers))

        embed = discord.Embed(
            title='Sum Result',
            description=f'{ctx.author.mention} {text}',
            color=color
        )
        embed.set_footer(text='Powered by SkyWizz')

        await ctx.send(embed=embed)

    @commands.command(name='subtract', aliases=['subtrair', 'subtrai'])
    async def subtract_numbers(self, ctx, *args):
        valid_numbers = []
        color = discord.Color.blue()
        for arg in args:
            try:
                num = float(arg)
                valid_numbers.append(num)
            except ValueError:
                pass

        if not valid_numbers:
            text = 'No valid numbers provided!'
        else:
            text = str(subtract(valid_numbers))

        embed = discord.Embed(
            title='Sum Result',
            description=f'{ctx.author.mention} {text}',
            color=color
        )
        embed.set_footer(text='Powered by SkyWizz')

        await ctx.send(embed=embed)


async def setup(bot):
    print('Loading Calculator Commands...')
    await bot.add_cog(CalculatorCommands(bot))
