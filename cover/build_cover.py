from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import numpy as np

W, H = 1640, 924
PHOTOS_DIR = os.path.expanduser("~/workspace/cades-liquidation/photos")
OUT = os.path.expanduser("~/workspace/cades-liquidation-site/cover/fb-group-cover.png")
LIB = "/usr/share/fonts/truetype/liberation/"   # Arial-metric; matches site font stack
DEJAVU = "/usr/share/fonts/truetype/dejavu/"

BLUE_TOP = (13, 79, 150)
BLUE_BOT = (8, 47, 92)
ORANGE = (224, 123, 26)
GOLD = (255, 197, 49)          # site rating-star color
WHITE = (255, 255, 255)
WHITE80 = (255, 255, 255)      # drawn with alpha feel via lighter blend below
LIGHT = (225, 236, 248)        # tagline: white @ .95 over blue
LIGHTER = (232, 240, 250)
MUTED = (150, 175, 200)

# --- background: vertical gradient (site hero) ---
bg = Image.new("RGB", (W, H))
px = bg.load()
for y in range(H):
    t = y / (H - 1)
    col = tuple(int(BLUE_TOP[i] + (BLUE_BOT[i] - BLUE_TOP[i]) * t) for i in range(3))
    for x in range(W):
        px[x, y] = col

# subtle orange glow top-right (like the site's visit band)
glow = Image.new("RGB", (W, H), (0, 0, 0))
ImageDraw.Draw(glow).ellipse([W - 700, -350, W + 300, 450], fill=(90, 45, 8))
glow = glow.filter(ImageFilter.GaussianBlur(160))
bg = Image.fromarray(
    np.clip(np.array(bg, dtype=float) * 0.82 + np.array(glow, dtype=float) * 0.18,
            0, 255).astype("uint8"))

d = ImageDraw.Draw(bg)

# --- orange top bar (matches site header accent) ---
d.rectangle([0, 0, W, 12], fill=ORANGE)

# --- photo strip: warehouse shots ---
strip_photos = [
    "warehouse-exterior.jpg",
    "warehouse-1.jpg",
    "warehouse-2.jpg",
]
STRIP_Y, STRIP_H, GAP = 36, 350, 8
n = len(strip_photos)
pw = (W - GAP * (n - 1)) // n
for i, name in enumerate(strip_photos):
    im = Image.open(os.path.join(PHOTOS_DIR, name)).convert("RGB")
    tr = pw / STRIP_H
    ir = im.width / im.height
    if ir > tr:
        nw = int(im.height * tr); x0 = (im.width - nw) // 2
        im = im.crop((x0, 0, x0 + nw, im.height))
    else:
        nh = int(im.width / tr); y0 = (im.height - nh) // 2
        im = im.crop((0, y0, im.width, y0 + nh))
    im = im.resize((pw, STRIP_H), Image.LANCZOS)
    xpos = i * (pw + GAP)
    if i == n - 1:  # last panel fills any remainder
        im = im.resize((W - xpos, STRIP_H), Image.LANCZOS)
    bg.paste(im, (xpos, STRIP_Y))
d.rectangle([0, STRIP_Y + STRIP_H, W, STRIP_Y + STRIP_H + 6], fill=ORANGE)


def font(name, size, dejavu=False):
    base = DEJAVU if dejavu else LIB
    return ImageFont.truetype(os.path.join(base, name), size)


def spaced_center(y, text, fnt, fill, spacing):
    """Letterspaced centered text (for eyebrow / tagline feel)."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = (W - total) / 2
    for ch, wch in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += wch + spacing


def centered_text(y, text, fnt, fill):
    bb = d.textbbox((0, 0), text, font=fnt)
    tw = bb[2] - bb[0]
    d.text(((W - tw) / 2 - bb[0], y), text, font=fnt, fill=fill)


# --- eyebrow (mirrors site hero eyebrow) ---
spaced_center(436, "BLOOMINGTON, IL  \u00b7  SCRATCH-AND-DENT DEALS",
              font("LiberationSans-Bold.ttf", 34), (255, 255, 255), 5)

# --- title (mirrors site hero h1) ---
centered_text(486, "CADE'S LIQUIDATION", font("LiberationSans-Bold.ttf", 122), WHITE)

# --- orange divider ---
d.rectangle([(W - 130) / 2, 664, (W + 130) / 2, 672], fill=ORANGE)

# --- tagline (his own line — product-agnostic) ---
spaced_center(706, "AMAZING PRODUCTS  \u00b7  AMAZING PRICES",
              font("LiberationSans-Regular.ttf", 44), LIGHT, 6)

# --- trust row (mirrors site trustbar: bold lead + rest), auto-fit to width ---
trusts = [
    ("4.9", "\u2605", " 273+ Marketplace ratings"),
    ("14-day", None, " money-back guarantee"),
    ("Delivery", None, " available for a charge"),
    ("Inspected", None, " \u2014 every item checked"),
]
sep = " \u00b7 "
_trust_size = 30
while _trust_size > 18:
    f_bold = font("LiberationSans-Bold.ttf", _trust_size)
    f_reg = font("LiberationSans-Regular.ttf", _trust_size)
    f_star = font("DejaVuSans-Bold.ttf", _trust_size, dejavu=True)
    _w = sum(d.textlength(lead, font=f_bold) +
             (d.textlength(star, font=f_star) if star else 0) +
             d.textlength(rest, font=f_reg) for lead, star, rest in trusts) \
        + d.textlength(sep, font=f_reg) * (len(trusts) - 1)
    if _w <= 1540:
        break
    _trust_size -= 1
# measure total width
total_w = _w
x = (W - total_w) / 2
y_trust = 818
for j, (lead, star, rest) in enumerate(trusts):
    if j:
        d.text((x, y_trust), sep, font=f_reg, fill=MUTED)
        x += d.textlength(sep, font=f_reg)
    d.text((x, y_trust), lead, font=f_bold, fill=WHITE)
    x += d.textlength(lead, font=f_bold)
    if star:
        d.text((x, y_trust), star, font=f_star, fill=GOLD)
        x += d.textlength(star, font=f_star)
    d.text((x, y_trust), rest, font=f_reg, fill=LIGHTER)
    x += d.textlength(rest, font=f_reg)

bg.save(OUT, quality=95)
print("saved", OUT, bg.size)
