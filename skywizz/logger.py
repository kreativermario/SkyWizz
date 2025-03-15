import logging
import colorlog
from skywizz import config

def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s:%(name)s:%(message)s',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = logging.getLogger('discord')
    logger.setLevel(config.log_level())
    logger.addHandler(handler)
    return logger

logger = setup_logger()
