import math
import re

from disnake import CmdInter
from disnake.ext.commands.errors import CheckFailure

VALID_CHAR = "-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"


def int_b64encode(to_encode: int):
    """Give a snowflake int and encode it into a modified base64 method."""
    o = []
    for t in range(math.floor(math.log(to_encode, 64)), -1, -1):
        p = math.floor(math.pow(64, t))
        a = math.floor((to_encode / p) % 64)
        o.append(VALID_CHAR[a])
        to_encode -= a * p
    return "".join(o)


def int_b64decode(to_decode: str):
    """Give a encoded snowflake string and decode it back to a snowflake ID."""
    o = 0
    l = len(to_decode) - 1
    for t, c in enumerate(to_decode):
        p = math.floor(math.pow(64, l - t))
        o += VALID_CHAR.index(c) * p
    return o


def add_underscore_if_digit(s):
    return "_" + s if s and s[0].isdigit() else s


def filepath_santitize(text: str) -> str:
    return re.sub(r"^[ .]|[/<>:\"\\|?*]+|[ .]$", "_", text)


def is_on_command_channel(inter: CmdInter):
    if inter.channel_id != 761814788589223978:
        raise CheckFailure("該指令僅能用於<#761814788589223978>中")
    return True
