from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = os.path.expanduser("~/workspace/cades-liquidation-site/logo")
LIB = "/usr/share/fonts/truetype/liberation/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/"

BLUE = (15, 92, 171)
NAVY = (8, 47, 92)
ORANGE = (224, 123, 26)
WHITE = (255, 255, 255)
INK = (29, 36, 48)
S = 1600  # square canvas

def font(name, size):
    return ImageFont.truetype(os.path.join(LIB, name), size)

def centered(d, cx, y, text, fnt, fill):
    bb = d.textbbox((0, 0), text, font=fnt)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), text, font=fnt, fill=fill)
    return bb[3] - bb[1]

def spaced(d, cx, y, text, fnt, fill, spacing):
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing

def rounded(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)

# ============ CONCEPT A: price-tag icon + wordmark (on white) ============
img = Image.new("RGB", (S, S), WHITE)
d = ImageDraw.Draw(img)
# tag shape on transparent layer, rotated
tag = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
td = ImageDraw.Draw(tag)
# tag pointing up-left: body rect + point
td.polygon([(180, 120), (560, 120), (560, 560), (180, 560), (60, 340)], fill=BLUE + (255,))
td.ellipse([105, 295, 195, 385], fill=(255, 255, 255, 255))  # hole
tag = tag.rotate(-18, resample=Image.BICUBIC, expand=True)
img.paste(tag, (330, 180), tag)
# % on the tag
fpct = font("LiberationSans-Bold.ttf", 200)
d.text((0, 0), "", font=fpct)  # warm up
# place % near tag center (approx after rotation)
import math as m
cx_t, cy_t = 330 + tag.width / 2, 180 + tag.height / 2
bb = d.textbbox((0, 0), "%", font=fpct)
d.text((cx_t - (bb[2]-bb[0])/2 - bb[0] + 30, cy_t - (bb[3]-bb[1])/2 - bb[1] - 10),
       "%", font=fpct, fill=ORANGE)
# wordmark
centered(d, S/2, 950, "CADE'S", font("LiberationSans-Bold.ttf", 190), INK)
spaced(d, S/2, 1170, "LIQUIDATION", font("LiberationSans-Bold.ttf", 104), ORANGE, 14)
img.save(f"{OUT}/logo-a-tag.png")

# ============ CONCEPT B: blue badge ============
img = Image.new("RGB", (S, S), WHITE)
d = ImageDraw.Draw(img)
rounded(d, [180, 330, S-180, S-330], 120, NAVY)
# thin orange inner border
d.rounded_rectangle([210, 360, S-210, S-360], radius=95, outline=ORANGE, width=10)
centered(d, S/2, 560, "CADE'S", font("LiberationSans-Bold.ttf", 230), WHITE)
spaced(d, S/2, 830, "LIQUIDATION", font("LiberationSans-Bold.ttf", 118), ORANGE, 16)
# small slash accent
d.rectangle([S/2 - 90, 1020, S/2 + 90, 1032], fill=ORANGE)
centered(d, S/2, 1075, "BLOOMINGTON-NORMAL, IL", font("LiberationSans-Regular.ttf", 52), (180, 200, 220))
img.save(f"{OUT}/logo-b-badge.png")

# ============ CONCEPT C: CL monogram ============
img = Image.new("RGB", (S, S), WHITE)
d = ImageDraw.Draw(img)
rounded(d, [430, 300, S-430, 860], 140, BLUE)
# orange corner slash (tag nod)
d.polygon([(S-430, 300), (S-430, 430), (S-560, 300)], fill=ORANGE)
centered(d, S/2, 420, "CL", font("LiberationSans-Bold.ttf", 300), WHITE)
centered(d, S/2, 980, "CADE'S LIQUIDATION", font("LiberationSans-Bold.ttf", 110), INK)
spaced(d, S/2, 1130, "AMAZING PRODUCTS \u00b7 AMAZING PRICES",
       font("LiberationSans-Regular.ttf", 44), (120, 135, 150), 6)
img.save(f"{OUT}/logo-c-monogram.png")
print("done")
