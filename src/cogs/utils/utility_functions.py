from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap


def check_request_status(response):
    """
    Function that checks the API response status code
    :param response: API Response
    :return: Raises exceptions if the API request fails
    """
    if response.status_code != 200:
        raise Exception(f'API fetch failed! Status code: '
                        f'{response.status_code}')


def get_airport_code_type(airport_code):
    """
    Function that returns which airport code type
    :param airport_code: Airport set of code
    :return: code: type of airport code
    :rtype: code: str
    """
    code = None
    # If it is IATA Code
    if len(airport_code) == 3:
        code = 'iata'
    # If it is ICAO Code
    elif len(airport_code) == 4:
        code = 'icao'
    return code


def validate_airport_code(airport_code):
    """
    Functions that validades airport code
    :param airport_code: The airport code
    :type airport_code: str
    :return:
    """
    if airport_code is None:
        raise Exception("Airport code is not valid! Try using IATA or "
                        "ICAO code format")


def product(nums):
    """
    Product function
    :param nums:
    :return:
    """
    result = 1
    for num in nums:
        result *= num
    return result


def subtract(nums):
    """
    Subtract function
    :param nums:
    :return:
    """
    result = nums[0]
    for num in nums[1:]:
        result -= num
    return result


def caption_image(image_file, caption, font="impact.ttf"):
    img = Image.open(image_file)
    draw = ImageDraw.Draw(img)

    font_size = int(img.width / 8)
    font = ImageFont.truetype("impact.ttf", font_size)

    caption = textwrap.fill(text=caption, width=img.width / (font_size / 2))

    caption_w, caption_h = draw.textsize(caption, font=font)

    draw.text(((img.width - caption_w) / 2, (img.height - caption_h) / 8),  # position
              caption,  # text
              (255, 255, 255),  # color
              font=font,  # font
              stroke_width=2,  # text outline width
              stroke_fill=(0, 0, 0))  # text outline color

    with BytesIO() as img_bytes:
        img.save(img_bytes, format=img.format)
        content = img_bytes.getvalue()

    return content


