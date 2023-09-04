import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import discord
import requests
from discord.ext import commands
import skywizz
import skywizz.tools as tools
import skywizz.tools.embed as embd

SUPPORTED_MIMETYPES = ["image/jpeg", "image/png", "image/webp"]


class MemeCog(commands.Cog):

    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.hidden = False
        self.__cog_name__ = 'Meme Commands'
        self.logger.info(f"Loaded {self.__cog_name__}")

    @commands.cooldown(1, 60, commands.BucketType.user)
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
            embed = skywizz.specific_error("Please include some caption "
                                           "text after the `!caption` "
                                           "command. "
                                           "For example "
                                           "`!caption \"Hello world!\"")
            await ctx.message.reply(embed=embed)
            return

        # Must have a file attached
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url
        else:
            embed = skywizz.specific_error('Please attach '
                                           'an image for me to caption.')
            await ctx.message.reply(embed=embed)
            return

        # File must be an image
        if mimetypes.guess_type(image_url)[0] not in SUPPORTED_MIMETYPES:
            embed = skywizz.specific_error('Sorry, the file you attached is '
                                           'not a supported image format. '
                                           'Please upload a PNG, JPEG or '
                                           'WebP image.')
            await ctx.message.reply(embed=embed)
            return

        # Fetch image file
        response = requests.get(image_url)

        # Store image file name
        image_filename = ctx.message.attachments[0].filename

        # Caption image
        final_image = tools.caption_image(BytesIO(response.content), caption_text)

        # Send reply
        await ctx.message.reply(file=discord.File(BytesIO(final_image),
                                                  filename=f'captioned-{image_filename}'))


async def setup(bot, logger):
    await bot.add_cog(MemeCog(bot, logger))
