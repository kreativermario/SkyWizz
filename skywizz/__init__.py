import datetime
import platform
import socket
import sys
from .cogs import *
from .events import *
from .setup import *
from .config import *
from .messages import *


def version():
    return "v0.0.1"


def config_version():
    return "0.1"  # do not edit this!


def time():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def year():
    return str(datetime.datetime.now().year)


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
