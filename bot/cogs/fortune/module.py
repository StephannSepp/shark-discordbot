"""
fortune.module
----------------

A module for the fortune draw command use.

Should be imported as a module.
"""

import random

from disnake import Colour

from static import hololive_talent

RESULTS = ["大凶", "凶", "小吉", "中吉", "大吉"]
LUCKY_COLORS = ["綠", "藍", "紫", "金", "橘", "紅", "黃"]
BADLUCK_IMGS = ["static/fortune/BL.png", "static/fortune/BL2.png"]


def draw_fortune(seed: int) -> str:
    random.seed(seed)
    result = random.choices(RESULTS, weights=[7, 20, 25, 32, 16])[0]
    return result


def get_lucky_colour(seed: int) -> str:
    random.seed(seed)
    result = random.choice(LUCKY_COLORS)
    return result


def get_lucky_number(seed: int) -> int:
    random.seed(seed)
    result = random.randint(0, 9)
    return result


def get_guardian_angel(seed: int) -> str:
    random.seed(seed)
    name, url = random.choice(list(hololive_talent.talent.items()))
    return name, url


def get_guardian_angel_image(angel: str) -> str:
    url = hololive_talent.talent.get(angel)
    return url


def to_colour_obj(colour: str) -> Colour:
    match colour:
        case "綠": return Colour.green()
        case "藍": return Colour.blue()
        case "紫": return Colour.purple()
        case "金": return Colour.gold()
        case "橘": return Colour.orange()
        case "紅": return Colour.red()
        case "黃": return Colour.yellow()


def get_image_url(luck: str, seed: int) -> str:
    random.seed(seed)
    match luck:
        case "大凶": return "static/fortune/TL.png"
        case "凶": return random.choice(BADLUCK_IMGS)
        case "小吉": return "static/fortune/SB.png"
        case "中吉": return "static/fortune/GF.png"
        case "大吉": return "static/fortune/GGF.png"
