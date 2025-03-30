import random
from datetime import datetime

from disnake import Colour
from static import aprilfool
from static import hololive_talent


RESULTS = ["大凶", "凶", "小吉", "中吉", "大吉"]
LUCKY_COLORS = ["綠", "藍", "紫", "金", "橘", "紅", "黃"]
BADLUCK_IMGS = ["https://i.imgur.com/ipi9ZhN.png", "https://i.imgur.com/liah3aW.png"]


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
    today = datetime.utcnow().date()
    if today.month == 4 and today.day == 1:
        name, url = random.choice(list(aprilfool.talent.items()))
    else:
        name, url = random.choice(list(hololive_talent.talent.items()))
    return name, url


def get_guardian_angel_image(angel: str) -> str:
    today = datetime.utcnow().date()
    if today.month == 4 and today.day == 1:
        return aprilfool.talent.get(angel)
    return hololive_talent.talent.get(angel)


def to_colour_obj(colour: str) -> Colour:
    match colour:
        case "綠":
            return Colour.green()
        case "藍":
            return Colour.blue()
        case "紫":
            return Colour.purple()
        case "金":
            return Colour.gold()
        case "橘":
            return Colour.orange()
        case "紅":
            return Colour.red()
        case "黃":
            return Colour.yellow()


def get_image_url(luck: str, seed: int) -> str:
    random.seed(seed)
    match luck:
        case "大凶":
            return "https://i.imgur.com/cG1E38m.png"
        case "凶":
            return random.choice(BADLUCK_IMGS)
        case "小吉":
            return "https://i.imgur.com/atoTZfT.png"
        case "中吉":
            return "https://i.imgur.com/0rk6Fnr.png"
        case "大吉":
            return "https://i.imgur.com/dZHjqkh.png"
