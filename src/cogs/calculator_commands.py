import discord
from discord.ext import commands

class CalculatorCogs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(bot.command_prefix)

    @commands.command(name='sum', aliases=['somar'])
    async def sum_numbers(self, ctx, *args):
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


async def setup(bot):
    print('Loading Calculator Commands...')
    await bot.add_cog(CalculatorCogs(bot))
