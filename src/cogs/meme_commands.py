import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import discord
import requests
from discord.ext import commands
from .utils.utility_functions import caption_image
from .utils.constants import FOOTER_TEXT

SUPPORTED_MIMETYPES = ["image/jpeg", "image/png", "image/webp"]


class MemeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.hidden = False
        self.__cog_name__ = 'Meme Commands'

    @commands.command(name='caption')
    async def caption(self, ctx, caption_text):
        """
        Command that creates a caption from a given image
        Attention: You must send an image along with the command!

        **Parameters:**
        - image_caption: The image's caption

        **Example:**
        - `!caption "Hello World"`

        **Usage:**
        - `caption <image_caption>`

        Usage: caption <image_caption>
        """
        # Must have caption text
        if not caption_text:
            await ctx.message.reply(
                "Please include some caption text after the `!caption` "
                "command. For example `!caption \"Hello world!\"")
            return

        # Must have a file attached
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        else:
            await ctx.message.reply('Please attach an image for me to caption.')
            return

        # File must be an image
        if mimetypes.guess_type(image_url)[0] not in SUPPORTED_MIMETYPES:
            await ctx.message.reply(
                'Sorry, the file you attached is not a supported image format. '
                'Please upload a PNG, JPEG or WebP image.')
            return

        # Fetch image file
        response = requests.get(image_url)

        # Store image file name
        image_filename = ctx.message.attachments[0].filename

        # Caption image
        final_image = caption_image(BytesIO(response.content), caption_text)

        # Send reply
        await ctx.message.reply(file=discord.File(BytesIO(final_image),
                                filename=f'captioned-{image_filename}'))

    @commands.command(name='tiocosta', alias=['antoniocosta'])
    async def tiocosta(self, ctx):
        """
        Command that sends a random quote by António Costa

        **Example:**
        - `!tiocosta`

        **Usage:**
        - `tiocosta`

        Usage: tiocosta
        """

        embed = discord.Embed(
            title="Tio Costa",
            description="Ontem foi ontem, hoje é um novo dia, muito bom céu,"
                        " ta tao bonito, adeus",
            color=discord.Color.red()
        )
        embed.set_footer(text=FOOTER_TEXT)

        await ctx.send(embed=embed)


async def setup(bot):
    print('Loading Meme Commands...')
    await bot.add_cog(MemeCog(bot))