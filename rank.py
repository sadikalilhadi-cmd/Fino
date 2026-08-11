import io
from PIL import Image, ImageDraw, ImageFont
import requests

WIDTH = 934
HEIGHT = 282

BACKGROUND = (15, 15, 15)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
BAR_BG = (55, 55, 55)
BAR_FILL = (255, 255, 255)

STATUS = {
    "online": (67, 181, 129),
    "idle": (250, 166, 26),
    "dnd": (237, 66, 69),
    "offline": (116, 127, 141)
}

try:
    FONT_BIG = ImageFont.truetype("assets/fonts/bold.ttf", 34)
    FONT_MED = ImageFont.truetype("assets/fonts/bold.ttf", 22)
    FONT_SMALL = ImageFont.truetype("assets/fonts/regular.ttf", 18)
except:
    FONT_BIG = ImageFont.load_default()
    FONT_MED = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()


def rounded(draw, xy, radius, color):
    draw.rounded_rectangle(xy, radius=radius, fill=color)


def circle(draw, x, y, r, color):
    draw.ellipse((x-r, y-r, x+r, y+r), fill=color)


async def create_rank_card(
    member,
    level,
    xp,
    next_xp,
    rank,
):

    card = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(card)
