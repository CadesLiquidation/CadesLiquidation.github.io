#!/usr/bin/env python3
"""Static site generator for the appliance liquidation catalog.

Reads ../cades-liquidation/inventory.json (+ listings_raw.json for descriptions)
and writes all HTML pages + copies the photos actually used into images/.

Re-runnable and idempotent. It NEVER touches config.json (that file belongs to
the site owner).

Usage:  python3 generate_site.py
Run from this directory.
"""
import html
import json
import os
import re
import shutil
import sys
import urllib.parse
from guides import GUIDES

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(HERE), "cades-liquidation")
OUT_DIR = HERE
IMG_DIR = os.path.join(OUT_DIR, "images")
LISTINGS_DIR = os.path.join(OUT_DIR, "listings")

PLACEHOLDER_NAME = "Cade's Liquidation"
PLACEHOLDER_TAGLINE = "New & scratch-and-dent appliances at liquidation prices"
PLACEHOLDER_ABOUT = (
    "Cade's Liquidation is run by Cade McClellan. We sell new, scratch-and-dent, "
    "and gently used appliances at liquidation prices: washers, dryers, "
    "refrigerators, ranges, freezers, dishwashers, and ovens. Every item is "
    "inspected and priced to move."
)
PLACEHOLDER_AREA = "Bloomington-Normal, IL"
PLACEHOLDER_RATING = "4.9 \u00b7 273+ Facebook Marketplace ratings"

FILTERS = ["All", "Washers", "Dryers", "Refrigerators", "Ranges",
           "Freezers", "Dishwashers", "Ovens"]

# Bump when styles.css / site.js change so browsers fetch the fresh files
ASSET_VER = "40"

# Canonical public URL of the site (used for share tags, sitemap, schema)
SITE_URL = "https://cadesliquidation.com"
# Google Analytics 4 measurement ID (his GA property).
GA_MEASUREMENT_ID = "G-V2FXEV2VNY"
# SMS number for prefilled text links (matches bundle.js PHONE).
SMS_PHONE = "+13094344800"

WARRANTY_NOTE = ("New and scratch-and-dent appliances may come with a 1-year "
                 "warranty, but a warranty is not guaranteed.")

APPT_NOTE = ("By appointment only \u2014 call or message to schedule a time "
             "to come see anything.")

ADDRESS_SHORT = "1206 S Adelaide St Suite 7, Normal, IL"
ADDRESS_NOTE = "Back parking lot, Suite 7 \u2014 behind Popejoy"

# Retail (MSRP) values from the load manifest, keyed by listing_id.
# Shown crossed-out above the sale price. Only filled where the
# model/price match is certain.
RETAIL_PRICES = {
    "1384781360536995": 3099,  # LG 28cu French Door (LHFS28XBS)
    "1126693043068885": 2599,  # GE 27cu French Door (GNE27JYMFS)
    "1498229855523007": 1999,  # GE Side by Side (GSS28NYYFS)
    "1108880614997392": 1199,  # LG Top Freezer (LHTNS2403S)
    "1011048761394885": 1149,  # LG Gas Dryer (DLG3421W)
    "2267447970675821": 999,   # GE White Top Freezer (GTS18HGNRWW)
    "2024831725140515": 929,   # GE Electric Glass Top Range (GRF40HSVSS)
    "1868075531223938": 699,   # Whirlpool Electric Dryer (WED4107SW)
    "1810826210014141": 699,   # Whirlpool Top Load Washer (WTW4107SW)
    "949330901055818": 629,    # Hotpoint Agitator Washer (HTW265ASWWB)
    "2699586173790624": 399,   # Frigidaire Chest Freezer
    "4719106331652104": 749,   # GE Dishwasher Stainless (GDT550PYRFS)
    "1449538590452959": 1099,  # LG Gas Range w/ Air Fry (LRGN6321Y)
    "1744440383278549": 2598,  # LG Washer+Dryer Set (WM4000HBA + DLEX4000B)
    "1643544697442082": 3000,  # Frigidaire Gallery Fridge (GRMS2773AF) — MSRP per Cade
    "1585063482717437": 649,   # Whirlpool Stainless Gas Range (WFG320M0MS) — label confirmed 2026-10-01
}


def load_reviews():
    p = os.path.join(SRC_DIR, "reviews.json")
    if os.path.exists(p):
        return json.load(open(p))
    return []


def review_card(r):
    return (f'<div class="review"><div class="stars" aria-label="5 out of 5 stars">'
            f'\u2605\u2605\u2605\u2605\u2605</div>'
            f'<p>{esc(r["text"])}</p>'
            f'<p class="review-meta">{esc(r["date"])} &middot; Facebook Marketplace review</p></div>')


def reviews_modal(reviews):
    cards = "\n".join(review_card(r) for r in reviews)
    return f"""<div class="modal-backdrop" id="reviews-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-label="Customer reviews">
    <div class="modal-head">
      <div>
        <p class="modal-kicker">Customer reviews</p>
        <p class="modal-rating"><span class="stars">\u2605\u2605\u2605\u2605\u2605</span>
        <strong>4.9</strong> &middot; 273 Marketplace ratings</p>
      </div>
      <button class="modal-close" data-close-modal aria-label="Close reviews">&times;</button>
    </div>
    <div class="modal-list">
{cards}
    </div>
    <p class="modal-foot">From Cade&rsquo;s public Facebook Marketplace profile.</p>
  </div>
</div>"""


def retail_html(listing_id, price_num, size=""):
    retail = RETAIL_PRICES.get(listing_id)
    if not retail or retail <= price_num:
        return ""
    if size == "lg":
        return f'<p class="retail-lg">Retail <s>${retail:,}</s></p>'
    return f'<p class="retail"><s>${retail:,}</s></p>'


def savings_html(listing_id, price_num):
    retail = RETAIL_PRICES.get(listing_id)
    if not retail or retail <= price_num:
        return ""
    save = retail - price_num
    pct = round(save / retail * 100)
    return f'<p class="savings">You save ${save:,.0f} ({pct}%)</p>'

# Listing photos that are generic stock shots, not the actual unit for sale
STOCK_DIR = os.path.join(SRC_DIR, "stock")
STOCK_PHOTOS = {f for f in os.listdir(STOCK_DIR)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))}

DAMAGE_RE = re.compile(r"\b(ding|dings|dent|dents|dented|scratch|scratches|scratched)\b",
                       re.IGNORECASE)


def filter_keys(category):
    c = category.strip().lower()
    if c == "washers & dryers":
        return ["washers", "dryers"]
    return [c]


def esc(s):
    return html.escape(s or "", quote=True)


def desc_to_html(description):
    """Turn a plain-text FB description into <p> paragraphs. Empty -> ''."""
    if not description or not description.strip():
        return ""
    paras = [p.strip() for p in re.split(r"\n\s*\n", description.strip()) if p.strip()]
    return "\n".join(f"<p>{esc(p)}</p>" for p in paras)


def meta_description(item, description):
    base = description.strip().replace("\n", " ") if description else ""
    if len(base) > 150:
        base = base[:147].rsplit(" ", 1)[0] + "..."
    if not base:
        base = f"{item['title']} for {item['price']}."
    return base


def load_data():
    with open(os.path.join(SRC_DIR, "inventory.json")) as f:
        inventory = json.load(f)
    descriptions = {}
    raw_path = os.path.join(SRC_DIR, "listings_raw.json")
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            for r in json.load(f):
                if r.get("description"):
                    descriptions[r["listing_id"]] = r["description"]
    for it in inventory["items"]:
        fuel, color = detect_attrs(it, descriptions.get(it["listing_id"], ""))
        it["fuel"] = fuel
        it["color"] = color
    return inventory["items"], descriptions


FUEL_WORDS = ("gas", "electric")
COLOR_WORDS = ["stainless", "black", "white", "ivory", "slate", "bisque"]


def detect_attrs(item, description):
    """Detect fuel type and color from title+description keywords.
    Returns (fuel, color) with None where nothing is stated — never guessed."""
    text = f"{item.get('title', '')} {description or ''}".lower()
    fuel = next((f for f in FUEL_WORDS if f in text), None)
    color = next((c for c in COLOR_WORDS if c in text), None)
    return fuel, color


def resolve_photos(item):
    """Return list of (src_filename) relative to images/ for this item."""
    photos = []
    if item.get("user_photo"):
        photos.append(item["user_photo"])
    if item.get("user_photo_2"):
        photos.append(item["user_photo_2"])
    for extra in item.get("user_photos") or []:
        photos.append(extra)
    if not photos:
        photos.append(item["photo"])  # stock fallback, e.g. stock/dryer.jpg
    return photos


# Extra images used by the site that aren't tied to a listing (relative to SRC_DIR)
EXTRA_IMAGES = [
    "stock/front-load-washer.jpg",
    "stock/dryer.jpg",
    "stock/french-door-fridge.jpg",
    "stock/gas-range.jpg",
    "stock/chest-freezer.jpg",
    "stock/dishwasher.jpg",
    "stock/wall-oven.jpg",
    "photos/warehouse-1.jpg",
    "photos/warehouse-2.jpg",
    "photos/photo-31-ge-frenchdoor-hero.jpg",
    "photos/cade.jpg",
    "logo/logo-header.png",
    "logo/logo-header-lockup.png",
    "logo/favicon.png",
    "logo/apple-touch-icon.png",
    "social/og-share.png",
]


def copy_photos(items):
    os.makedirs(IMG_DIR, exist_ok=True)
    used = set()
    for item in items:
        for src_rel in resolve_photos(item):
            src = os.path.join(SRC_DIR, src_rel)
            if not os.path.exists(src):
                print(f"WARNING: missing photo {src_rel} for {item['listing_id']}",
                      file=sys.stderr)
                continue
            name = os.path.basename(src_rel)
            used.add(name)
            shutil.copy2(src, os.path.join(IMG_DIR, name))
    for rel in EXTRA_IMAGES:
        src = os.path.join(SRC_DIR, rel)
        if os.path.exists(src):
            name = os.path.basename(rel)
            shutil.copy2(src, os.path.join(IMG_DIR, name))
            used.add(name)
    # remove stale images no longer referenced
    for f in os.listdir(IMG_DIR):
        if f not in used:
            os.remove(os.path.join(IMG_DIR, f))
    return used


def header(active, prefix=""):
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix}index.html"><img src="{prefix}images/logo-header-lockup.png" alt="Cade's Liquidation"></a>
    <nav class="main-nav">
      <a href="{prefix}index.html" class="{'active' if active == 'catalog' else ''}">Catalog</a>
      <a href="{prefix}bundle.html" class="{'active' if active == 'bundles' else ''}">Bundles</a>
      <a href="{prefix}about.html" class="{'active' if active == 'about' else ''}">About</a>
      <a href="{prefix}faq.html" class="{'active' if active == 'faq' else ''}">FAQ</a>
    </nav>
    <a class="btn btn-call" data-config-href="phoneHref" hidden><span data-config="phone">Call us</span></a>
  </div>
</header>"""


def footer(prefix=""):
    guide_links = "\n      ".join(
        f'<a href="{prefix}guides/{g["slug"]}.html">{esc(g["h1"])}</a>'
        for g in GUIDES)
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      <strong data-config="businessName">{esc(PLACEHOLDER_NAME)}</strong><br>
      <span data-config="serviceArea">{esc(PLACEHOLDER_AREA)}</span> &middot;
      <span data-config="tagline">{esc(PLACEHOLDER_TAGLINE)}</span>
    </div>
    <div class="footer-contact">
      <a class="btn btn-fb" data-config-href="facebookGroupUrl" hidden>Visit our Facebook group: <span data-config="facebookGroupName"></span></a>
    </div>
    <nav class="footer-guides" aria-label="Buying guides">
      <strong>Buying guides</strong>
      {guide_links}
    </nav>
  </div>
  <div class="wrap footer-small">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies &middot; {esc(ADDRESS_SHORT)}</div>
</footer>
<script src="{prefix}site.js?v={ASSET_VER}"></script>"""


def page_shell(title, meta_desc, body, active, prefix="", og_image=None,
               page_url="", json_ld=None, noindex=False):
    og_tags = ""
    if og_image:
        abs_img = f"{SITE_URL}/images/{og_image}"
        abs_url = f"{SITE_URL}/{page_url}"
        og_tags = f"""
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(abs_url)}">
<meta property="og:image" content="{esc(abs_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(meta_desc)}">
<meta name="twitter:image" content="{esc(abs_img)}">"""
    ld_tag = (f'\n<script type="application/ld+json">\n{json_ld}\n</script>'
              if json_ld else "")
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta_desc)}">{robots}{og_tags}{ld_tag}
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
<link rel="stylesheet" href="{prefix}styles.css?v={ASSET_VER}">
<link rel="icon" type="image/png" href="{prefix}images/favicon.png">
<link rel="apple-touch-icon" href="{prefix}images/apple-touch-icon.png">
</head>
<body>
{header(active, prefix)}
<main>
{body}
</main>
{footer(prefix)}
</body>
</html>
"""


def card_html(item, photo_file, prefix="", sold_badge=False):
    cats = " ".join(filter_keys(item["category"]))
    stock = photo_file in STOCK_PHOTOS
    dropped = (item.get("prev_price_num") or 0) > (item.get("price_num") or 0)
    drop_badge = ('<span class="drop-badge">Price drop</span>' if dropped and not sold_badge else "")
    drop_line = (f'<p class="price-drop">was {esc(item["prev_price"])}</p>'
                 if dropped and not sold_badge else "")
    img_html = (f'<div class="card-img{" stock-photo" if stock else ""}">'
                f'<img src="{prefix}images/{esc(photo_file)}" alt="{esc(item["title"])}" loading="lazy">'
                + (f'<span class="stock-badge{" stock-badge-low" if sold_badge else ""}">Stock photo &mdash; not the actual unit</span>'
                   if stock else "")
                + ('<span class="sold-badge">SOLD</span>' if sold_badge else "")
                + drop_badge
                + "</div>")
    return f"""<article class="card" data-cats="{cats}" data-fuel="{item.get('fuel') or ''}" data-color="{item.get('color') or ''}">
  <a href="{prefix}listings/{item['listing_id']}.html" class="card-link">
    {img_html}
    <div class="card-body">
      <span class="badge">{esc(item['category'])}</span>
      <h3>{esc(item['title'])}</h3>
      {retail_html(item['listing_id'], item.get('price_num', 0))}
      <p class="price">{esc(item['price'])}</p>
      {drop_line}
    </div>
  </a>
</article>"""


def build_index(items, photo_of, sold):
    filters = "\n".join(
        f'<button class="filter-btn{" active" if f == "All" else ""}" data-filter="{f.lower()}">{f}</button>'
        for f in FILTERS
    )
    cards = "\n".join(card_html(it, photo_of[it["listing_id"]][0]) for it in items)
    delivery_href = (f"sms:{SMS_PHONE}?&body=" +
                     urllib.parse.quote("Hi Cade, can I get a delivery quote?"))

    categories = [
        ("Washers", "front-load-washer.jpg", "washers"),
        ("Dryers", "dryer.jpg", "dryers"),
        ("Refrigerators", "french-door-fridge.jpg", "refrigerators"),
        ("Ranges", "gas-range.jpg", "ranges"),
        ("Freezers", "chest-freezer.jpg", "freezers"),
        ("Dishwashers", "dishwasher.jpg", "dishwashers"),
        ("Ovens", "wall-oven.jpg", "ovens"),
    ]
    tiles = "\n".join(
        f'<button class="cat-tile" data-goto-filter="{key}">'
        f'<img src="images/{img}?v={ASSET_VER}" alt="{label}" loading="lazy">'
        f"<span>{label}</span></button>"
        for label, img, key in categories
    )

    featured_items = sorted(items, key=lambda it: it.get("price_num", 0), reverse=True)[:3]
    featured = "\n".join(card_html(it, photo_of[it["listing_id"]][0]) for it in featured_items)

    sold_sorted = sorted(sold, key=lambda it: it.get("sold_date", ""), reverse=True)[:4]
    sold_cards = "\n".join(
        card_html(it, photo_of[it["listing_id"]][0], sold_badge=True) for it in sold_sorted)
    sold_section = f"""<section class="wrap">
  <h2 class="section-title">Recently sold</h2>
  <p class="section-sub">These moved fast.</p>
  <div class="grid">
{sold_cards}
  </div>
</section>""" if sold_sorted else ""

    body = f"""<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="eyebrow"><span data-config="serviceArea">{esc(PLACEHOLDER_AREA)}</span> &middot; Scratch-and-dent deals</p>
      <h1 data-config="businessName">{esc(PLACEHOLDER_NAME)}</h1>
      <p class="tagline" data-config="tagline">{esc(PLACEHOLDER_TAGLINE)}</p>
      <button class="rating rating-btn" id="reviews-open" type="button" title="Read customer reviews"><span class="stars">\u2605\u2605\u2605\u2605\u2605</span> <span class="rating-text" data-config="ratingText">{esc(PLACEHOLDER_RATING)}</span></button>
      <div class="hero-cta">
        <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
        <a class="btn btn-bundle btn-lg" href="bundle.html">Build a bundle &amp; save</a>
      </div>
      <p class="appt-note appt-note-hero">{esc(APPT_NOTE)}</p>
    </div>
    <div class="hero-collage">
      <img class="collage-main" src="images/photo-31-ge-frenchdoor-hero.jpg" alt="GE French door refrigerator">
      <img class="collage-a" src="images/photo-12-lg-set-black.jpg" alt="Washer and dryer set">
      <img class="collage-b" src="images/photo-18-frigidaire-gallery.jpg" alt="Refrigerator">
    </div>
  </div>
</section>
<section class="trustbar">
  <div class="wrap trustbar-inner">
    <div class="trust"><strong>4.9\u2605</strong><span>273+ Marketplace ratings</span></div>
    <div class="trust"><strong>14-day</strong><span>money-back guarantee</span></div>
    <div class="trust"><strong>Delivery</strong><span>available for a charge</span></div>
    <div class="trust"><strong>Inspected</strong><span>every item checked</span></div>
  </div>
</section>
<section class="wrap">
  <h2 class="section-title">Shop by category</h2>
  <div class="cat-tiles">{tiles}</div>
</section>
<section class="wrap">
  <h2 class="section-title">Featured deals</h2>
  <div class="grid featured-grid">{featured}</div>
</section>
<section class="wrap">
  <h2 class="section-title">How buying works</h2>
  <div class="steps">
    <div class="step"><span class="step-n">1</span><div><strong>Browse the catalog</strong><p>Every listing has real photos, the price, and what it would cost new.</p></div></div>
    <div class="step"><span class="step-n">2</span><div><strong>Call or text Cade</strong><p>Ask questions or claim it before someone else does &mdash; each piece is one of a kind.</p></div></div>
    <div class="step"><span class="step-n">3</span><div><strong>Pick up or get delivery</strong><p>See it by appointment at the warehouse, or have it delivered for a charge.</p></div></div>
  </div>
</section>
<section class="wrap" id="catalog">
  <h2 class="section-title">Full catalog</h2>
  <div class="catalog-toolbar">
    <input type="search" id="catalog-search" placeholder="Search appliances..." aria-label="Search appliances">
  </div>
  <div class="filters">{filters}</div>
  <div class="grid" id="catalog-grid">
{cards}
  </div>
  <p class="grid-empty" id="grid-empty" hidden>No items match right now.</p>
</section>
{sold_section}
<section class="visit-band">
  <div class="wrap visit-inner">
    <img src="images/warehouse-2.jpg" alt="Our warehouse stocked with appliances" loading="lazy">
    <div class="visit-copy">
      <h2>Come see it in person</h2>
      <p>Our warehouse is stocked with washers, dryers, refrigerators, ranges and more
      &mdash; all inspected and priced to move.</p>
      <p class="appt-note">{esc(APPT_NOTE)}</p>
      <p class="visit-address">{esc(ADDRESS_SHORT)}<br>{esc(ADDRESS_NOTE)}</p>
      <div class="hero-cta" style="margin-top:16px">
        <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
      </div>
    </div>
  </div>
</section>
<section class="wrap">
  <div class="delivery-band">
    <div>
      <strong>Need it delivered?</strong>
      <p><strong>$50 flat</strong> &mdash; delivered to your door anywhere in Bloomington-Normal, IL.</p>
      <p class="delivery-fine">Outside the area or need installation? Text for a quote &mdash; installation services available for an additional charge. <a href="guides/delivery.html" class="delivery-link">Delivery details &rarr;</a></p>
    </div>
    <a class="btn btn-call" href="{delivery_href}">Text Cade for a quote</a>
  </div>
</section>
{reviews_modal(load_reviews())}"""
    local_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Store",
        "name": PLACEHOLDER_NAME,
        "description": PLACEHOLDER_TAGLINE,
        "telephone": "+13094344800",
        "url": SITE_URL + "/",
        "image": f"{SITE_URL}/images/og-share.png",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "1206 S Adelaide St Suite 7",
            "addressLocality": "Normal",
            "addressRegion": "IL",
            "addressCountry": "US",
        },
        "areaServed": PLACEHOLDER_AREA,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "273",
        },
        "priceRange": "$",
    }, indent=2)
    return page_shell(
        f"{PLACEHOLDER_NAME} | Discount Appliances in {PLACEHOLDER_AREA}",
        f"Shop new and scratch-and-dent washers, dryers, refrigerators, ranges, "
        f"freezers, dishwashers and ovens at liquidation prices in {PLACEHOLDER_AREA}. "
        f"14-day money-back guarantee.",
        body, "catalog",
        og_image="og-share.png", page_url="",
        json_ld=local_ld)


def related_items(item, items, n=4):
    """Up to n active listings similar to `item`: same category first,
    then everything else. Never the item itself."""
    same = [it for it in items
            if it["listing_id"] != item["listing_id"]
            and it.get("status") != "sold"
            and it["category"] == item["category"]]
    rest = [it for it in items
            if it["listing_id"] != item["listing_id"]
            and it.get("status") != "sold"
            and it["category"] != item["category"]]
    return (same + rest)[:n]


def seo_title(item):
    """Title tag for a listing page, kept within ~70 chars for search engines."""
    suffix = f" | {PLACEHOLDER_NAME}"
    base = f"{item['title']}{suffix}"
    if len(base) <= 70:
        return base
    budget = 70 - len(suffix) - 1  # room for the ellipsis
    t = item["title"][:budget].rsplit(" ", 1)[0]
    return f"{t}\u2026{suffix}"


def build_detail(item, descriptions, photo_files, items, photo_of):
    desc = descriptions.get(item["listing_id"], "")
    desc_html = desc_to_html(desc)
    if not desc_html:
        desc_html = ("<p>Contact us for full details, dimensions, and current "
                     "availability on this item.</p>")
    stock_badge = ('<span class="stock-badge">Stock photo &mdash; not the actual unit</span>'
                   if photo_files[0] in STOCK_PHOTOS else "")
    if len(photo_files) > 1:
        main = photo_files[0]
        total = len(photo_files)
        collapsed = total > 5
        thumb_btns = []
        for i, pf in enumerate(photo_files[1:], start=1):
            cls = "thumb"
            extra = ""
            if collapsed and i == 5:
                cls += " thumb-more"
                extra = f' data-remaining="{total - 5}"'
            thumb_btns.append(
                f'<button class="{cls}"{extra} data-full="../images/{esc(pf)}">'
                f'<img src="../images/{esc(pf)}" alt="{esc(item["title"])} - photo {i + 1}"></button>'
            )
        thumbs = "\n".join(thumb_btns)
        gallery = f"""<div class="gallery">{stock_badge}
      <img id="gallery-main" src="../images/{esc(main)}" alt="{esc(item['title'])}">
      <span class="zoom-hint">Tap to zoom</span>
      <div class="thumbs{" collapsed" if collapsed else ""}">{thumbs}</div>
    </div>"""
    else:
        gallery = (f'<div class="gallery">{stock_badge}<img id="gallery-main" src="../images/{esc(photo_files[0])}" '
                   f'alt="{esc(item["title"])}"><span class="zoom-hint">Tap to zoom</span></div>')
    mp_url = item.get("url", "")
    mp_button = (f'<a class="btn btn-fb btn-lg" href="{esc(mp_url)}">View this listing on Facebook Marketplace</a>'
                 if mp_url else "")
    cond = "Scratch & Dent" if DAMAGE_RE.search(desc) else item.get("condition", "New")
    sold = item.get("status") == "sold"
    sold_banner = ('<div class="sold-banner">This item has sold &mdash; '
                   '<a href="../index.html">browse the current catalog</a></div>'
                   if sold else "")
    one_only = ("" if sold else
                '<p class="one-only">One only &mdash; when it&rsquo;s gone, it&rsquo;s gone.</p>')
    ask_body = urllib.parse.quote(
        f"Hi Cade, is this still available? {item['title']} ({item['price']})")
    ask_href = f"sms:{SMS_PHONE}?&body={ask_body}"
    dropped = (item.get("prev_price_num") or 0) > (item.get("price_num") or 0)
    drop_line = (f'<p class="price-drop">Price dropped from {esc(item["prev_price"])}</p>'
                 if dropped and not sold else "")
    cta = ("" if sold else f"""<div class="detail-cta">
      <div class="detail-cta-main">
        <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text about this item: <span data-config="phone"></span></a>
        {mp_button}
      </div>
      <div class="detail-cta-sub">
        <a class="btn btn-ghost" href="{ask_href}">Is this still available?</a>
        <button type="button" class="btn btn-ghost" id="share-listing">Share this listing</button>
      </div>
    </div>""")
    body = f"""<div class="wrap detail">
  <p class="breadcrumb"><a href="../index.html">&larr; Back to catalog</a></p>
  {sold_banner}
  {gallery}
  <div class="detail-info">
    <span class="badge">{esc(item['category'])}</span>
    <h1>{esc(item['title'])}</h1>
    {retail_html(item['listing_id'], item.get('price_num', 0), size="lg")}
    <p class="price price-lg">{esc(item['price'])}</p>
    {drop_line}
    {savings_html(item['listing_id'], item.get('price_num', 0))}
    {one_only}
    <div class="description" id="listing-desc">{desc_html}</div>
    <button type="button" class="desc-toggle" id="desc-toggle" hidden>View more</button>
    <dl class="facts">
      <div><dt>Condition</dt><dd>{esc(cond)}</dd></div>
      <div><dt>Category</dt><dd>{esc(item['category'])}</dd></div>
      <div><dt>Price</dt><dd>{esc(item['price'])}</dd></div>
    </dl>
    {cta}
    <p class="appt-note">{esc(APPT_NOTE)}</p>
    <p class="guarantee-note">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies<br><span class="warranty-note">{esc(WARRANTY_NOTE)}</span></p>
  </div>
</div>"""
    related = related_items(item, items)
    related_html = ""
    if related:
        cards = "\n".join(card_html(it, photo_of[it["listing_id"]][0], prefix="../")
                          for it in related)
        related_html = f"""<section class="wrap">
  <h2 class="section-title">Similar listings</h2>
  <div class="grid">
{cards}
  </div>
</section>"""
    promo_html = ("" if sold else """<section class="wrap">
  <div class="bundle-promo">
    <div>
      <strong>Save up to 15% by bundling</strong>
      <p>Combine this with other appliances and unlock bundle discounts automatically.</p>
    </div>
    <a class="btn btn-bundle btn-lg" href="../bundle.html">Build a bundle</a>
  </div>
</section>""")
    body = body + promo_html + related_html
    product_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": item["title"],
        "image": f"{SITE_URL}/images/{photo_files[0]}",
        "description": meta_description(item, desc),
        "offers": {
            "@type": "Offer",
            "price": item.get("price_num", 0),
            "priceCurrency": "USD",
            "availability": ("https://schema.org/OutOfStock" if sold
                             else "https://schema.org/InStock"),
            "url": f"{SITE_URL}/listings/{item['listing_id']}.html",
        },
    }, indent=2)
    return page_shell(
        seo_title(item),
        meta_description(item, desc),
        body, "catalog", prefix="../",
        og_image=photo_files[0],
        page_url=f"listings/{item['listing_id']}.html",
        json_ld=product_ld, noindex=sold)


def build_about():
    body = f"""<div class="wrap prose">
  <h1>About us</h1>
  <p data-config="aboutText">{esc(PLACEHOLDER_ABOUT)}</p>
  <h2>Meet Cade</h2>
  <div class="owner">
    <img src="images/cade.jpg" alt="Cade McClellan, owner of Cade's Liquidation" loading="lazy">
    <div>
      <p>I&rsquo;m <strong>Cade McClellan</strong> &mdash; I&rsquo;ve lived in Bloomington, Illinois
      practically my whole life, and I&rsquo;m currently at ISU working toward my Bachelor of Science
      degree. I&rsquo;ve always had an entrepreneur mindset and a real fascination with businesses
      and having my own.</p>
      <p>Growing up I did every side hustle I could get my hands on &mdash; mowing grass, working on
      cars, computer programming. When I graduated high school in 2023, I went out on a limb and bought
      my first pallets of liquidation, had them shipped to my parents&rsquo; house, and set up shop
      under a carport in the backyard.</p>
      <p>Over the past three years I&rsquo;ve kept building the business while going to college full
      time. The plan is to turn it into a full-time store after graduation.</p>
    </div>
  </div>
  <figure class="about-photo">
    <img src="images/warehouse-1.jpg" alt="Inside our appliance warehouse" loading="lazy">
    <figcaption>Inside the warehouse &mdash; new inventory arrives regularly.</figcaption>
  </figure>
  <p>We specialize in <strong>scratch-and-dent</strong> appliances: brand-new units with
  small cosmetic dings or dents (usually on the sides, where you'll never see them)
  sold at a fraction of retail. We also carry new in-box and gently used appliances.</p>
  <h2>What we sell</h2>
  <ul>
    <li>Washers &amp; dryers (top-load, front-load, gas and electric)</li>
    <li>Refrigerators (French door, side-by-side, top-freezer)</li>
    <li>Ranges (gas and electric, including models with Air Fry)</li>
    <li>Chest freezers</li>
    <li>Dishwashers</li>
    <li>Wall ovens and double ovens</li>
  </ul>
  <h2>How buying works</h2>
  <p>Browse the catalog, find something you like, and get in touch. <strong>{esc(APPT_NOTE)}</strong>
  We&rsquo;re located at {esc(ADDRESS_SHORT)} (back parking lot, Suite 7, behind Popejoy).
  Every sale includes our 14-day money-back guarantee. Delivery is available for a charge, and sales tax
  applies. Serving <span data-config="serviceArea">{esc(PLACEHOLDER_AREA)}</span> and
  surrounding areas.</p>
  <div class="hero-cta">
    <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
    <a class="btn btn-fb btn-lg" data-config-href="facebookGroupUrl" hidden>Facebook group: <span data-config="facebookGroupName"></span></a>
  </div>
</div>"""
    return page_shell(
        f"About | {PLACEHOLDER_NAME}",
        f"About {PLACEHOLDER_NAME}: new, scratch-and-dent and used appliances "
        f"at liquidation prices in {PLACEHOLDER_AREA}.",
        body, "about",
        og_image="og-share.png", page_url="about.html")


def build_guide(g, items, photo_of):
    slug = g["slug"]
    sections = "\n".join(
        f"<h2>{h}</h2>\n{body}" for h, body in g["sections"])
    listings_html = ""
    if g.get("category"):
        cats = [g["category"]]
        if g["category"] in ("Washers", "Dryers"):
            cats.append("Washers & Dryers")
        cat_items = [it for it in items if it["category"] in cats]
        if cat_items:
            cards = "\n".join(
                card_html(it, photo_of[it["listing_id"]][0], prefix="../")
                for it in cat_items)
            listings_html = f"""<h2>Current {esc(g["category"]).lower()} in stock</h2>
<p>Live inventory &mdash; when it's gone, it's gone.</p>
<div class="grid">
{cards}
</div>"""
        else:
            listings_html = (f"<h2>Current {esc(g['category']).lower()} in stock</h2>"
                             "<p>Nothing in this category at the moment &mdash; "
                             '<a href="../index.html#catalog">check the full catalog</a> '
                             "or text us and we'll keep an eye out.</p>")
    others = [o for o in GUIDES if o["slug"] != slug]
    more = "\n".join(
        f'<a href="{o["slug"]}.html">{esc(o["h1"])}</a>'
        for o in others)
    cta = ("""<div class="guide-cta">
      <strong>Found what you need?</strong>
      <p>Every unit is tested before it's listed and backed by a 14-day money-back guarantee.</p>
      <div class="hero-cta">
        <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
        <a class="btn btn-bundle btn-lg" href="../bundle.html">Build a bundle &amp; save</a>
      </div>
    </div>""" if g.get("cta") else "")
    body = f"""<div class="wrap guide">
  <p class="breadcrumb"><a href="../index.html">&larr; Back to home</a></p>
  <h1>{esc(g["h1"])}</h1>
  <div class="guide-intro">{g["intro"]}</div>
  {sections}
  {listings_html}
  {cta}
  <div class="more-guides">
    <strong>More buying guides</strong>
    <nav>{more}</nav>
  </div>
</div>"""
    return page_shell(g["title"], g["meta"], body, "", prefix="../",
                      og_image="og-share.png", page_url=f"guides/{slug}.html")


def build_faq():
    faqs = [
        ("What is your return policy?",
         "Every appliance comes with a 14-day money-back guarantee. If something "
         "isn't right, let us know within 14 days and we'll make it right."),
        ("Do you deliver?",
         "Yes — $50 flat delivery to your door anywhere in Bloomington-Normal, IL. "
         "Outside the area, contact us for a quote. Installation services are also "
         "available for an additional charge — ask for pricing."),
        ("Does sales tax apply?",
         "Yes, sales tax applies to all purchases."),
        ("What does \"scratch-and-dent\" mean?",
         "These are brand-new appliances with minor cosmetic imperfections — "
         "usually small dings or dents on the sides. They work like new and are "
         "priced well below retail because of the cosmetic flaws."),
        ("Is there a warranty?",
         WARRANTY_NOTE + " Some listings include a manufacturer warranty — check "
         "the item description for details."),
        ("Do I need an appointment to come see something?",
         APPT_NOTE),
        ("What condition are the appliances in?",
         "Most of our inventory is new (including scratch-and-dent). We also carry "
         "select gently used items, always clearly marked with their condition."),
        ("How do I buy an item?",
         "Find an appliance in the catalog and contact us. We'll confirm "
         "availability and arrange pickup or delivery."),
        ("Where are you located?",
         f"We serve {PLACEHOLDER_AREA} and the surrounding areas. Contact us for "
         "pickup details."),
    ]
    items_html = "\n".join(
        f"<details><summary>{esc(q)}</summary><p>{a}</p></details>"
        for q, a in faqs
    )
    # escape answers that contain the placeholder area already handled above
    body = f"""<div class="wrap prose">
  <h1>FAQ &amp; Policies</h1>
{items_html}
</div>"""
    return page_shell(
        f"FAQ & Policies | {PLACEHOLDER_NAME}",
        "Policies: 14-day money-back guarantee, delivery available for a charge, "
        "sales tax applies. Answers about scratch-and-dent appliances.",
        body, "faq",
        og_image="og-share.png", page_url="faq.html")


def build_bundle(items, photo_of, descriptions):
    data = [{
        "id": it["listing_id"],
        "title": it["title"],
        "price": it["price"],
        "price_num": it.get("price_num", 0),
        "category": it["category"],
        "photo": photo_of[it["listing_id"]][0],
        "retail": RETAIL_PRICES.get(it["listing_id"]),
        "fuel": it.get("fuel"),
        "color": it.get("color"),
        "description": descriptions.get(it["listing_id"], ""),
        "condition": ("Scratch & Dent"
                      if DAMAGE_RE.search(descriptions.get(it["listing_id"], ""))
                      else it.get("condition", "New")),
    } for it in items]
    cats = sorted({it["category"] for it in items})
    chips = "\n".join(
        f'<button class="bfilter{" active" if c == "All" else ""}" data-filter="{c.lower()}">{c}</button>'
        for c in ["All"] + cats)
    body = f"""<div class="wrap">
  <h1>Bundle Builder</h1>
  <p class="bundle-intro">Tap the appliances you want and bundle them for an automatic discount. Popular combos: a kitchen set (fridge + range + dishwasher) or a laundry pair (washer + dryer).</p>
  <div class="bundle-tiers" id="bundle-tiers"></div>
  <div class="bundle-layout">
    <div class="bundle-main">
      <div class="bundle-toolbar">
        <input type="search" id="bundle-search" placeholder="Search appliances..." aria-label="Search appliances">
        <div class="bundle-filters">{chips}</div>
      </div>
      <div class="grid bundle-grid" id="bundle-grid"></div>
      <p class="grid-empty" id="bundle-empty" hidden>No items match your search.</p>
    </div>
    <aside class="bundle-aside" id="bundle-summary" aria-live="polite"></aside>
  </div>
</div>
<div class="bundle-bar" id="bundle-bar" hidden>
  <span id="bundle-bar-text"></span>
  <a href="#bundle-summary" class="btn btn-call">Review bundle</a>
</div>
<script>var BUNDLE_ITEMS = {json.dumps(data)};</script>
<script src="bundle.js?v={ASSET_VER}"></script>"""
    return page_shell(
        f"Bundle Builder | {PLACEHOLDER_NAME}",
        f"Build your own appliance bundle at {PLACEHOLDER_NAME} and save: "
        f"bundle discounts on washers, dryers, refrigerators, ranges and more "
        f"in {PLACEHOLDER_AREA}.",
        body, "bundles",
        og_image="og-share.png", page_url="bundle.html")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def main():
    items, descriptions = load_data()
    active = [it for it in items if it.get("status") != "sold"]
    sold = [it for it in items if it.get("status") == "sold"]
    print(f"Loaded {len(items)} listings ({len(active)} active, {len(sold)} sold), "
          f"{len(descriptions)} descriptions.")
    copy_photos(items)
    photo_of = {it["listing_id"]: [os.path.basename(p) for p in resolve_photos(it)]
                for it in items}

    os.makedirs(LISTINGS_DIR, exist_ok=True)
    write(os.path.join(OUT_DIR, "index.html"), build_index(active, photo_of, sold))
    for it in items:
        write(os.path.join(LISTINGS_DIR, f"{it['listing_id']}.html"),
              build_detail(it, descriptions, photo_of[it["listing_id"]],
                           active, photo_of))
    write(os.path.join(OUT_DIR, "about.html"), build_about())
    write(os.path.join(OUT_DIR, "faq.html"), build_faq())
    write(os.path.join(OUT_DIR, "bundle.html"), build_bundle(active, photo_of, descriptions))
    guides_dir = os.path.join(OUT_DIR, "guides")
    for g in GUIDES:
        write(os.path.join(guides_dir, f"{g['slug']}.html"),
              build_guide(g, active, photo_of))

    # sitemap.xml (active listings only) + robots.txt
    urls = (["", "about.html", "faq.html", "bundle.html"]
            + [f"guides/{g['slug']}.html" for g in GUIDES]
            + [f"listings/{it['listing_id']}.html" for it in active])
    sitemap = ('<?xml version="1.0" encoding="utf-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>" for u in urls)
               + "\n</urlset>\n")
    write(os.path.join(OUT_DIR, "sitemap.xml"), sitemap)
    write(os.path.join(OUT_DIR, "robots.txt"),
          f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Wrote index.html, about.html, faq.html, sitemap.xml, robots.txt, "
          f"{len(items)} listing pages ({len(sold)} sold).")


if __name__ == "__main__":
    main()
