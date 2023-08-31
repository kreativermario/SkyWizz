import discord

import skywizz


def newembed(color=0x428DFF, title="SkyWizz", description="SkyWizz"):
    em = discord.Embed(colour=color, title=title, description=description)
    em.set_footer(text=skywizz.copyright())

    return em