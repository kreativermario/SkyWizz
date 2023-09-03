import discord

import skywizz
import skywizz.tools.embed as embd


def work_in_progress():
    """Work In Progress"""
    embed = embd.newembed(title="🚧 Oopsie! This feature is in development...",
                          description="Please stay tuned to our latest updates [here]("
                                      "https://github.com/kreativermario/SkyWizz)!",
                          color=0x89CFF0)
    embed.set_footer(text=skywizz.footer())
    return embed


def notfound(s):
    embed = embd.newembed(title=f"⚠️ Oops! ``{s.capitalize()}`` not found!",
                          description=f"Unable to find the specified {s.lower()}!",
                          color=0xFF0000)
    embed.set_footer(text=skywizz.footer())
    return embed


def error(e="executing command"):
    embed = embd.newembed(title=f"⚠️ Unknown error occurred while {e}!",
                          description="Please report it to "
                                      "[SkyWizz](https://github.com/kreativermario/SkyWizz) developers "
                                      "[here](https://github.com/kreativermario/SkyWizz/issues)!",
                          color=0xFF0000)
    embed.set_footer(text=skywizz.footer())
    return embed


def invalid_argument(given_arg, valid_args, recommendation=None):
    embed = embd.newembed(title="🛑 Invalid argument!",
                          description=f"Valid argument(s): ``{valid_args}``",
                          color=0xFF0000)
    embed.add_field(name="Your argument(s):", value=f"``{given_arg}``",
                    inline=False)
    if recommendation:
        embed.add_field(name="Tip:", value=recommendation)

    embed.set_footer(text=skywizz.footer())
    return embed


def specific_error(error_message: str):
    embed = embd.newembed(title="🛑 Something went wrong!",
                          description=error_message,
                          color=0xFF0000)
    embed.set_footer(text=skywizz.footer())
    return embed


def too_many_arguments():
    embed = embd.newembed(title="🛑 Too many arguments!",
                          description="You have entered too many arguments!",
                          color=0xFF0000)
    embed.set_footer(text=skywizz.footer())
    return embed
