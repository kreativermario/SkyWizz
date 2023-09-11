import logging
from datetime import datetime
import platform
import socket
import sys

import colorlog

from .cogs import *
from .events import *
from .setup import *
from .config import *
from .messages import *


def setup_logger(name):
    # Configure colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    # Set up logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)  # Add the file handler
    return logger


def version():
    return "v0.0.2 - John Dalton"


def footer():
    return f"{skywizz.copyright()} - Running on {version()}"


def config_version():
    return "0.1"  # do not edit this!


def time():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def year():
    return str(datetime.now().year)


def copyright():
    if year() == "2023":
        return "© 2023 SkyWizz"
    else:
        return f"© 2023-{year()} SkyWizz"


def platform():
    return platform.system() + " " + platform.release()


def hostname():
    return socket.gethostname()


def ip():
    return socket.gethostbyname(hostname())


def path():
    return sys.path
