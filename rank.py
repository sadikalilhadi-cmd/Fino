import io
from PIL import Image, ImageDraw, ImageFont
import requests


# ============================================================
# FİNO RANK SYSTEM
# ============================================================

WIDTH = 934
HEIGHT = 282

BACKGROUND = (15, 15, 15)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (35, 35, 35)
BAR_BG = (55, 55, 55)
BAR_FILL = (255, 255, 255)

STATUS = {
    "online": (67, 181, 129),
    "idle": (250, 166, 26),
    "dnd": (237, 66, 69),
    "offline": (116, 127, 141)
}


# ============================================================
# FONTLAR
# ============================================================

try:
    FONT_BIG = ImageFont.truetype(
        "assets/fonts/bold.ttf",
        34
    )

    FONT_MED = ImageFont.truetype(
        "assets/fonts/bold.ttf",
        22
    )

    FONT_SMALL = ImageFont.truetype(
        "assets/fonts/regular.ttf",
        18
    )

except Exception:
    FONT_BIG = ImageFont.load_default()
    FONT_MED = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def rounded(draw, xy, radius, color):
    draw.rounded_rectangle(
        xy,
        radius=radius,
        fill=color
    )


def circle(draw, x, y, r, color):
    draw.ellipse(
        (x - r, y - r, x + r, y + r),
        fill=color
    )


def get_avatar(member):
    """
    Discord kullanıcısının avatarını indirir.
    """

    try:
        avatar_url = str(member.display_avatar.url)

        response = requests.get(
            avatar_url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        avatar = Image.open(
            io.BytesIO(response.content)
        ).convert("RGBA")

        return avatar

    except Exception:
        return None


def make_circle_avatar(avatar, size):
    """
    Avatarı daire şeklinde kırpar.
    """

    avatar = avatar.resize(
        (size, size),
        Image.Resampling.LANCZOS
    )

    mask = Image.new(
        "L",
        (size, size),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.ellipse(
        (0, 0, size, size),
        fill=255
    )

    result = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0)
    )

    result.paste(
        avatar,
        (0, 0),
        mask
    )

    return result


def format_xp(number):
    """
    XP değerini daha güzel gösterir.

    1650 -> 1.65k
    5600 -> 5.6k
    """

    try:
        number = int(number)
    except Exception:
        number = 0

    if number >= 1_000_000:
        value = number / 1_000_000
        return f"{value:.2f}".rstrip("0").rstrip(".") + "m"

    if number >= 1_000:
        value = number / 1_000
        return f"{value:.2f}".rstrip("0").rstrip(".") + "k"

    return str(number)


def safe_name(member):
    """
    Kullanıcı adını güvenli şekilde alır.
    """

    try:
        name = member.display_name
    except Exception:
        name = "User"

    if not name:
        name = "User"

    return str(name)


def get_status(member):
    """
    Discord kullanıcısının durumunu almaya çalışır.
    """

    try:
        status = str(member.status).lower()

        if status in STATUS:
            return status

    except Exception:
        pass

    return "offline"


def draw_status(
    draw,
    x,
    y,
    radius,
    status
):
    """
    Avatarın yanına Discord durum noktasını çizer.
    """

    color = STATUS.get(
        status,
        STATUS["offline"]
    )

    circle(
        draw,
        x,
        y,
        radius,
        color
    )

    # Durum noktasının etrafına koyu kenarlık
    draw.ellipse(
        (
            x - radius - 3,
            y - radius - 3,
            x + radius + 3,
            y + radius + 3
        ),
        outline=BACKGROUND,
        width=5
    )

    circle(
        draw,
        x,
        y,
        radius,
        color
    )


def calculate_progress(
    xp,
    next_xp
):
    """
    XP barının doluluk oranını hesaplar.
    """

    try:
        xp = float(xp)
        next_xp = float(next_xp)

        if next_xp <= 0:
            return 0

        progress = xp / next_xp

        if progress < 0:
            progress = 0

        if progress > 1:
            progress = 1

        return progress

    except Exception:
        return 0


# ============================================================
# RANK KARTI
# ============================================================

async def create_rank_card(
    member,
    level,
    xp,
    next_xp,
    rank,
):

    # --------------------------------------------------------
    # TEMEL KART
    # --------------------------------------------------------

    card = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(card)

    # --------------------------------------------------------
    # ÜST KISIM
    # --------------------------------------------------------

    # Kartın dış kenarı
    draw.rounded_rectangle(
        (2, 2, WIDTH - 2, HEIGHT - 2),
        radius=22,
        outline=(30, 30, 30),
        width=3
    )

    # --------------------------------------------------------
    # AVATAR
    # --------------------------------------------------------

    avatar = get_avatar(member)

    AVATAR_SIZE = 150

    AVATAR_X = 42
    AVATAR_Y = 58

    if avatar is not None:

        avatar = make_circle_avatar(
            avatar,
            AVATAR_SIZE
        )

        card.paste(
            avatar,
            (AVATAR_X, AVATAR_Y),
            avatar
        )

    else:

        # Avatar alınamazsa varsayılan koyu daire
        circle(
            draw,
            AVATAR_X + AVATAR_SIZE // 2,
            AVATAR_Y + AVATAR_SIZE // 2,
            AVATAR_SIZE // 2,
            DARK_GRAY
        )

    # --------------------------------------------------------
    # DURUM NOKTASI
    # --------------------------------------------------------

    status = get_status(member)

    draw_status(
        draw,
        AVATAR_X + AVATAR_SIZE - 8,
        AVATAR_Y + AVATAR_SIZE - 8,
        14,
        status
    )

    # --------------------------------------------------------
    # KULLANICI ADI
    # --------------------------------------------------------

    username = safe_name(member)

    NAME_X = 225
    NAME_Y = 45

    draw.text(
        (NAME_X, NAME_Y),
        username,
        font=FONT_BIG,
        fill=WHITE
    )

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    LEVEL_X = 225
    LEVEL_Y = 95

    draw.text(
        (LEVEL_X, LEVEL_Y),
        f"Level {level}",
        font=FONT_MED,
        fill=WHITE
    )

    # --------------------------------------------------------
    # RANK
    # --------------------------------------------------------

    rank_text = f"Rank #{rank}"

    rank_bbox = draw.textbbox(
        (0, 0),
        rank_text,
        font=FONT_MED
    )

    rank_width = rank_bbox[2] - rank_bbox[0]

    RANK_X = WIDTH - rank_width - 45
    RANK_Y = 50

    draw.text(
        (RANK_X, RANK_Y),
        rank_text,
        font=FONT_MED,
        fill=WHITE
    )

    # --------------------------------------------------------
    # XP YAZISI
    # --------------------------------------------------------

    xp_text = (
        f"{format_xp(xp)} / "
        f"{format_xp(next_xp)} XP"
    )

    XP_Y = 135

    draw.text(
        (NAME_X, XP_Y),
        xp_text,
        font=FONT_SMALL,
        fill=GRAY
    )

    # --------------------------------------------------------
    # XP BAR
    # --------------------------------------------------------

    BAR_X = NAME_X
    BAR_Y = 170

    BAR_WIDTH = 665
    BAR_HEIGHT = 30

    # Bar arka planı
    draw.rounded_rectangle(
        (
            BAR_X,
            BAR_Y,
            BAR_X + BAR_WIDTH,
            BAR_Y + BAR_HEIGHT
        ),
        radius=15,
        fill=BAR_BG
    )

    # XP ilerleme oranı
    progress = calculate_progress(
        xp,
        next_xp
    )

    fill_width = int(
        BAR_WIDTH * progress
    )

    # Minimum genişlik
    if fill_width > 0 and fill_width < 15:
        fill_width = 15

    if fill_width > 0:

        draw.rounded_rectangle(
            (
                BAR_X,
                BAR_Y,
                BAR_X + fill_width,
                BAR_Y + BAR_HEIGHT
            ),
            radius=15,
            fill=BAR_FILL
        )

    # --------------------------------------------------------
    # YÜZDE
    # --------------------------------------------------------

    percentage = int(
        progress * 100
    )

    percentage_text = f"{percentage}%"

    percentage_bbox = draw.textbbox(
        (0, 0),
        percentage_text,
        font=FONT_SMALL
    )

    percentage_width = (
        percentage_bbox[2]
        - percentage_bbox[0]
    )

    draw.text(
        (
            BAR_X + BAR_WIDTH - percentage_width - 12,
            BAR_Y + 5
        ),
        percentage_text,
        font=FONT_SMALL,
        fill=WHITE
    )

    # --------------------------------------------------------
    # ALT BİLGİ
    # --------------------------------------------------------

    footer_text = "Fino Level System"

    draw.text(
        (NAME_X, 225),
        footer_text,
        font=FONT_SMALL,
        fill=(110, 110, 110)
    )

    # --------------------------------------------------------
    # LEVEL NUMARASI
    # --------------------------------------------------------

    level_text = f"LEVEL {level}"

    level_bbox = draw.textbbox(
        (0, 0),
        level_text,
        font=FONT_SMALL
    )

    level_width = (
        level_bbox[2]
        - level_bbox[0]
    )

    draw.text(
        (
            WIDTH - level_width - 45,
            225
        ),
        level_text,
        font=FONT_SMALL,
        fill=(110, 110, 110)
    )

    # --------------------------------------------------------
    # PNG OLARAK KAYDET
    # --------------------------------------------------------

    output = io.BytesIO()

    card.save(
        output,
        format="PNG"
    )

    output.seek(0)

    return output


# ============================================================
# XP SEVİYE HESAPLAMA
# ============================================================

LEVEL_XP = {
    1: 100,
    2: 250,
    3: 500,
    4: 800,
    5: 1250,
    6: 2000,
    7: 3000,
    8: 4250,
    9: 5750,
    10: 7500,
    11: 9500,
    12: 11750,
    13: 14250,
    14: 17000,
    15: 20000,
    16: 23250,
    17: 26750,
    18: 30500,
    19: 34500,
    20: 38750,
}


def get_level_from_xp(xp):
    """
    Toplam XP'ye göre level bulur.
    """

    try:
        xp = int(xp)
    except Exception:
        xp = 0

    level = 0

    for current_level in sorted(
        LEVEL_XP.keys()
    ):

        required = LEVEL_XP[current_level]

        if xp >= required:
            level = current_level
        else:
            break

    return level


def get_next_level_xp(level):
    """
    Bir sonraki level için gereken XP.
    """

    try:
        level = int(level)
    except Exception:
        level = 0

    next_level = level + 1

    if next_level in LEVEL_XP:
        return LEVEL_XP[next_level]

    # 20'den sonrası için basit artış
    last_xp = LEVEL_XP[20]

    extra_levels = next_level - 20

    if extra_levels < 1:
        extra_levels = 1

    return int(
        last_xp
        + (extra_levels * 5000)
    )


def get_current_level_xp(level):
    """
    Mevcut levelın başlangıç XP'si.
    """

    try:
        level = int(level)
    except Exception:
        level = 0

    if level <= 0:
        return 0

    if level in LEVEL_XP:
        return LEVEL_XP[level]

    return int(
        LEVEL_XP[20]
        + ((level - 20) * 5000)
    )


def get_level_progress(
    total_xp,
    level
):
    """
    Rank kartında kullanılacak:
    mevcut XP / sonraki level XP
    değerlerini döndürür.
    """

    try:
        total_xp = int(total_xp)
    except Exception:
        total_xp = 0

    current_level_xp = get_current_level_xp(
        level
    )

    next_level_xp = get_next_level_xp(
        level
    )

    current_xp = (
        total_xp
        - current_level_xp
    )

    required_xp = (
        next_level_xp
        - current_level_xp
    )

    if current_xp < 0:
        current_xp = 0

    if required_xp <= 0:
        required_xp = 1

    if current_xp > required_xp:
        current_xp = required_xp

    return (
        current_xp,
        required_xp
    )


# ============================================================
# DIŞARIDAN KULLANILABİLECEK ANA FONKSİYON
# ============================================================

async def generate_rank(
    member,
    total_xp,
    rank
):
    """
    Bu fonksiyon:
    XP -> Level
    Level -> XP barı
    Rank -> Rank kartı
    işlemlerini yapar.
    """

    try:
        total_xp = int(total_xp)
    except Exception:
        total_xp = 0

    if total_xp < 0:
        total_xp = 0

    level = get_level_from_xp(
        total_xp
    )

    current_xp, next_xp = get_level_progress(
        total_xp,
        level
    )

    return await create_rank_card(
        member=member,
        level=level,
        xp=current_xp,
        next_xp=next_xp,
        rank=rank
    )


# ============================================================
# TEST DEĞERLERİ
# ============================================================

DEFAULT_LEVEL = 1
DEFAULT_XP = 0
DEFAULT_RANK = 0


# ============================================================
# DOSYA BİTTİ
# ============================================================
