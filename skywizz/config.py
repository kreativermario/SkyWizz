import os

import skywizz


def bot_token():
    return os.getenv('BOT_TOKEN')


def bot_prefix():
    return os.getenv('BOT_PREFIX', "!")


def bot_status():
    default_prefix = f'{", ".join(skywizz.config.bot_prefix())} | SkyWizz {skywizz.version()}'
    try:
        return os.getenv('BOT_STATUS', default_prefix)
    except:
        return os.getenv('BOT_STATUS', default_prefix)
