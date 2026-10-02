from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

LIB = "/usr/share/fonts/truetype/liberation/"
SRC = os.path.expanduser("~/workspace/cades-liquidation")
OUT = os.path.join(SRC, "social", "og-share.png")

W, H = 1200, 630
NAVY = (8, 47, 92)
ORANGE = (224, 123, 26)
WHITE = (255, 255, 255)
MUTED = (185, 205, 228)

def font(name, size):
    return ImageFont.truetype(os.path.join(LIB, name), size)

img = Image.new("RGB", (W, H), NAVY)
d = ImageDraw.Draw(img)

# photo strip across the top: warehouse + 2 appliances
PH = 330
wh = ImageOps.fit(Image.open(os.path.join(SRC, "photos", "warehouse-2.jpg")).convert("RGB"), (600, PH), Image.LANCZOS)
a1 = ImageOps.fit(Image.open(os.path.join(SRC, "photos", "photo-31-ge-frenchdoor-hero.jpg")).convert("RGB"), (300, PH), Image.LANCZOS)
a2 = ImageOps.fit(Image.open(os.path.join(SRC, "photos", "photo-12-lg-set-black.jpg")).convert("RGB"), (300, PH), Image.LANCZOS)
img.paste(wh, (0, 0)); img.paste(a1, (600, 0)); img.paste(a2, (900, 0))
d.rectangle([0, PH - 6, W, PH], fill=ORANGE)

def centered(cx, y, text, fnt, fill):
    bb = d.textbbox((0, 0), text, font=fnt)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), text, font=fnt, fill=fill)

def spaced(cx, y, text, fnt, fill, spacing):
    widths = [d.textlength(c, font=fnt) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=fnt, fill=fill)
        x += w + spacing

centered(W / 2, 372, "CADE'S LIQUIDATION", font("LiberationSans-Bold.ttf", 96), WHITE)
spaced(W / 2, 492, "AMAZING PRODUCTS  \u00b7  AMAZING PRICES", font("LiberationSans-Bold.ttf", 34), ORANGE, 6)
centered(W / 2, 552, "4.9/5 273+ Marketplace ratings  \u00b7  14-day money-back  \u00b7  Bloomington-Normal, IL",
         font("LiberationSans-Regular.ttf", 28), MUTED)

img.save(OUT)
print("saved", OUT, img.size)
