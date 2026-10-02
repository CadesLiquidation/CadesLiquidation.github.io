from PIL import Image, ImageDraw, ImageFont
import os

LIB = "/usr/share/fonts/truetype/liberation/"
NAVY = (8, 47, 92)
ORANGE = (224, 123, 26)
WHITE = (255, 255, 255)
INK = (29, 36, 48)
OUTSRC = os.path.expanduser("~/workspace/cades-liquidation/logo")

def font(name, size):
    return ImageFont.truetype(os.path.join(LIB, name), size)

# ---------- 1. transparent badge (same design, no white box) ----------
S = 1600
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([180, 330, S-180, S-330], radius=120, fill=NAVY + (255,))
d.rounded_rectangle([210, 360, S-210, S-360], radius=95, outline=ORANGE + (255,), width=10)
def centered(dr, cx, y, text, fnt, fill):
    bb = dr.textbbox((0, 0), text, font=fnt)
    dr.text((cx - (bb[2]-bb[0])/2 - bb[0], y), text, font=fnt, fill=fill)
def spaced(dr, cx, y, text, fnt, fill, spacing):
    widths = [dr.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text)-1)
    x = cx - total/2
    for ch, w in zip(text, widths):
        dr.text((x, y), ch, font=fnt, fill=fill)
        x += w + spacing
centered(d, S/2, 560, "CADE'S", font("LiberationSans-Bold.ttf", 230), WHITE + (255,))
spaced(d, S/2, 830, "LIQUIDATION", font("LiberationSans-Bold.ttf", 118), ORANGE + (255,), 16)
d.rectangle([S/2-90, 1020, S/2+90, 1032], fill=ORANGE + (255,))
centered(d, S/2, 1075, "BLOOMINGTON-NORMAL, IL", font("LiberationSans-Regular.ttf", 52), (180, 200, 220, 255))
badge = img.crop((150, 300, 1450, 1300))
badge.save(f"{OUTSRC}/logo-header.png")
print("transparent badge:", badge.size)

# ---------- 2. horizontal lockup for the site header ----------
H = 200
icon = Image.new("RGBA", (H, H), (0, 0, 0, 0))
di = ImageDraw.Draw(icon)
di.rounded_rectangle([0, 0, H, H], radius=44, fill=NAVY + (255,))
centered(di, H/2, 38, "CL", font("LiberationSans-Bold.ttf", 104), WHITE + (255,))
di.rounded_rectangle([52, 152, H-52, 162], radius=5, fill=ORANGE + (255,))

W = 760
lock = Image.new("RGBA", (W, H), (0, 0, 0, 0))
lock.paste(icon, (0, 0), icon)
dl = ImageDraw.Draw(lock)
x0 = H + 28
dl.text((x0, 18), "CADE'S", font=font("LiberationSans-Bold.ttf", 92), fill=INK + (255,))
spaced(dl, x0 + 250, 118, "LIQUIDATION", font("LiberationSans-Bold.ttf", 52), ORANGE + (255,), 8)
# trim right whitespace
bbox = lock.getbbox()
lockup = lock.crop(bbox)
lockup.save(f"{OUTSRC}/logo-header-lockup.png")
print("lockup:", lockup.size)

# ---------- 3. favicon (transparent) + apple touch icon (navy) ----------
w, h = badge.size
side = max(w, h)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.paste(badge, ((side-w)//2, (side-h)//2), badge)
sq.resize((64, 64), Image.LANCZOS).save(f"{OUTSRC}/favicon.png")
navy_sq = Image.new("RGBA", (side, side), NAVY + (255,))
navy_sq.paste(badge, ((side-w)//2, (side-h)//2), badge)
navy_sq.resize((180, 180), Image.LANCZOS).convert("RGB").save(f"{OUTSRC}/apple-touch-icon.png")
print("icons done")
