import functools
import warnings
import aiohttp
import textwrap
import whois

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .exceptions import *
from .embed import *


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


async def get_coordinates(city_name, country_name=None):
    """
    Function that gets the GPS coordinates of a given city_name and
    optionally a country name
    """
    async with aiohttp.ClientSession() as session:
        url = 'https://nominatim.openstreetmap.org/search'

        params = {
            "format": "json",
            "q": city_name,  # Use "q" for query, which accepts city and country
        }

        if country_name:
            params["q"] = f"{city_name}, {country_name}"

        async with session.get(url, params=params) as response:
            data = await response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
            else:
                raise ValueError("Location not found")


async def reverse_gps(latitude, longitude):
    """
    Function that returns the city,country given GPS coordinates
    """
    async with aiohttp.ClientSession() as session:
        url = 'https://nominatim.openstreetmap.org/reverse'
        params = {
            "format": "json",
            "lat": latitude,
            "lon": longitude,
            "zoom": 10,
        }
        async with session.get(url, params=params) as response:
            data = await response.json()
            if data:
                city = data['address']['city']
                country = data['address']['country']
                country_code = data['address']['country_code']
                return city, country, country_code
            else:
                raise ValueError("Country not found")


def check_request_status(response):
    """
    Check if the API response is successful
    :param response: API response object
    :type response: Response object from the requests library
    """
    if not (200 <= response.status_code < 300):
        raise APIRequestError(f'Request failed with status '
                              f'{response.status_code}: {response.text}')


async def whois_lookup(domain):
    """
    Performs a WHOIS lookup for the specified domain.

    **Parameters:**
    - domain: The domain to lookup.

    **Returns:**
    - A dictionary containing the WHOIS data for the domain.
    """

    date_format = '%Y-%m-%d %H:%M:%S'
    whois_data = whois.whois(domain)
    if isinstance(whois_data.expiration_date, list):
        expiration_date = whois_data.expiration_date[0].strftime(date_format) \
            if whois_data.expiration_date[0] is not None else 'N/A'
    else:
        expiration_date = whois_data.expiration_date

    if isinstance(whois_data.creation_date, list):
        creation_date = whois_data.creation_date[0].strftime(date_format)
    else:
        creation_date = whois_data.creation_date.strftime(date_format) \
            if whois_data.creation_date is not None else 'N/A'

    if isinstance(whois_data.last_updated, list):
        last_updated = whois_data.last_updated[0].strftime(date_format)
    else:
        last_updated = whois_data.last_updated.strftime(date_format) \
            if whois_data.last_updated is not None else 'N/A'

    name = whois_data.name if whois_data.name is not None else 'N/A'
    country = whois_data.country if whois_data.country is not None else 'N/A'
    registrar = whois_data.registrar if whois_data.registrar is not None \
        else 'N/A'
    name_servers = whois_data.name_servers

    return {
        'name': name,
        'country': country,
        'registrar': registrar,
        'creation_date': creation_date,
        'expiration_date': expiration_date,
        'last_updated': last_updated,
        'name_servers': name_servers
    }


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


def caption_image(image_file, caption):
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
