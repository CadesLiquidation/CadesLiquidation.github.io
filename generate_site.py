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
PLACEHOLDER_AREA = "Bloomington, IL"
PLACEHOLDER_RATING = "4.9 \u00b7 273+ Facebook Marketplace ratings"

FILTERS = ["All", "Washers", "Dryers", "Refrigerators", "Ranges",
           "Freezers", "Dishwashers", "Ovens"]

# Bump when styles.css / site.js change so browsers fetch the fresh files
ASSET_VER = "14"

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
    "1449538590452959": 1099,  # LG Gas Range w/ Air Fry (LRGN6321Y)
    "1744440383278549": 2598,  # LG Washer+Dryer Set (WM4000HBA + DLEX4000B)
    "1643544697442082": 1850,  # Frigidaire Gallery Fridge (GRMS2773AF)
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
STOCK_PHOTOS = {"washer-dryer-set.jpg", "french-door-fridge.jpg",
                "side-by-side-fridge.jpg", "wall-oven.jpg", "dishwasher.jpg"}

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
    return inventory["items"], descriptions


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
    "stock/gas-range.jpg",
    "stock/chest-freezer.jpg",
    "photos/warehouse-1.jpg",
    "photos/warehouse-2.jpg",
    "photos/photo-31-ge-frenchdoor-hero.jpg",
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
    <a class="brand" href="{prefix}index.html" data-config="businessName">{esc(PLACEHOLDER_NAME)}</a>
    <nav class="main-nav">
      <a href="{prefix}index.html" class="{'active' if active == 'catalog' else ''}">Catalog</a>
      <a href="{prefix}about.html" class="{'active' if active == 'about' else ''}">About</a>
      <a href="{prefix}faq.html" class="{'active' if active == 'faq' else ''}">FAQ</a>
    </nav>
    <a class="btn btn-call" data-config-href="phoneHref" hidden><span data-config="phone">Call us</span></a>
  </div>
</header>"""


def footer(prefix=""):
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
  </div>
  <div class="wrap footer-small">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies &middot; {esc(ADDRESS_SHORT)}</div>
</footer>
<script src="{prefix}site.js?v={ASSET_VER}"></script>"""


def page_shell(title, meta_desc, body, active, prefix=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="stylesheet" href="{prefix}styles.css?v={ASSET_VER}">
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


def card_html(item, photo_file):
    cats = " ".join(filter_keys(item["category"]))
    stock = photo_file in STOCK_PHOTOS
    img_html = (f'<div class="card-img{" stock-photo" if stock else ""}">'
                f'<img src="images/{esc(photo_file)}" alt="{esc(item["title"])}" loading="lazy">'
                + ('<span class="stock-badge">Stock photo &mdash; not the actual unit</span>'
                   if stock else "")
                + "</div>")
    return f"""<article class="card" data-cats="{cats}">
  <a href="listings/{item['listing_id']}.html" class="card-link">
    {img_html}
    <div class="card-body">
      <span class="badge">{esc(item['category'])}</span>
      <h3>{esc(item['title'])}</h3>
      {retail_html(item['listing_id'], item.get('price_num', 0))}
      <p class="price">{esc(item['price'])}</p>
    </div>
  </a>
</article>"""


def build_index(items, photo_of):
    filters = "\n".join(
        f'<button class="filter-btn{" active" if f == "All" else ""}" data-filter="{f.lower()}">{f}</button>'
        for f in FILTERS
    )
    cards = "\n".join(card_html(it, photo_of[it["listing_id"]][0]) for it in items)

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
        f'<img src="images/{img}" alt="{label}" loading="lazy">'
        f"<span>{label}</span></button>"
        for label, img, key in categories
    )

    featured_items = sorted(items, key=lambda it: it.get("price_num", 0), reverse=True)[:3]
    featured = "\n".join(card_html(it, photo_of[it["listing_id"]][0]) for it in featured_items)

    body = f"""<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <p class="eyebrow"><span data-config="serviceArea">{esc(PLACEHOLDER_AREA)}</span> &middot; Scratch-and-dent deals</p>
      <h1 data-config="businessName">{esc(PLACEHOLDER_NAME)}</h1>
      <p class="tagline" data-config="tagline">{esc(PLACEHOLDER_TAGLINE)}</p>
      <button class="rating rating-btn" id="reviews-open" type="button" title="Read customer reviews"><span class="stars">\u2605\u2605\u2605\u2605\u2605</span> <span class="rating-text" data-config="ratingText">{esc(PLACEHOLDER_RATING)}</span></button>
      <div class="hero-cta">
        <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
        <a class="btn btn-fb btn-lg" data-config-href="facebookGroupUrl" hidden>Facebook group: <span data-config="facebookGroupName"></span></a>
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
<section class="wrap" id="catalog">
  <h2 class="section-title">Full catalog</h2>
  <div class="filters">{filters}</div>
  <div class="grid" id="catalog-grid">
{cards}
  </div>
  <p class="grid-empty" id="grid-empty" hidden>No items in this category right now.</p>
</section>
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
{reviews_modal(load_reviews())}"""
    return page_shell(
        f"{PLACEHOLDER_NAME} | New & Scratch-and-Dent Appliances in {PLACEHOLDER_AREA}",
        f"Shop new and scratch-and-dent washers, dryers, refrigerators, ranges, "
        f"freezers, dishwashers and ovens at liquidation prices in {PLACEHOLDER_AREA}. "
        f"14-day money-back guarantee.",
        body, "catalog")


def build_detail(item, descriptions, photo_files):
    desc = descriptions.get(item["listing_id"], "")
    desc_html = desc_to_html(desc)
    if not desc_html:
        desc_html = ("<p>Contact us for full details, dimensions, and current "
                     "availability on this item.</p>")
    stock_badge = ('<span class="stock-badge">Stock photo &mdash; not the actual unit</span>'
                   if photo_files[0] in STOCK_PHOTOS else "")
    if len(photo_files) > 1:
        main = photo_files[0]
        thumbs = "\n".join(
            f'<button class="thumb" data-full="../images/{esc(pf)}">'
            f'<img src="../images/{esc(pf)}" alt="{esc(item["title"])} - photo {i + 1}"></button>'
            for i, pf in enumerate(photo_files[1:], start=1)
        )
        gallery = f"""<div class="gallery">{stock_badge}
      <img id="gallery-main" src="../images/{esc(main)}" alt="{esc(item['title'])}">
      <div class="thumbs">{thumbs}</div>
    </div>"""
    else:
        gallery = (f'<div class="gallery">{stock_badge}<img src="../images/{esc(photo_files[0])}" '
                   f'alt="{esc(item["title"])}"></div>')
    mp_url = item.get("url", "")
    mp_button = (f'<a class="btn btn-fb btn-lg" href="{esc(mp_url)}">View this listing on Facebook Marketplace</a>'
                 if mp_url else "")
    cond = "Scratch & Dent" if DAMAGE_RE.search(desc) else item.get("condition", "New")
    body = f"""<div class="wrap detail">
  <p class="breadcrumb"><a href="../index.html">&larr; Back to catalog</a></p>
  {gallery}
  <div class="detail-info">
    <span class="badge">{esc(item['category'])}</span>
    <h1>{esc(item['title'])}</h1>
    {retail_html(item['listing_id'], item.get('price_num', 0), size="lg")}
    <p class="price price-lg">{esc(item['price'])}</p>
    {savings_html(item['listing_id'], item.get('price_num', 0))}
    <div class="description">{desc_html}</div>
    <dl class="facts">
      <div><dt>Condition</dt><dd>{esc(cond)}</dd></div>
      <div><dt>Category</dt><dd>{esc(item['category'])}</dd></div>
      <div><dt>Price</dt><dd>{esc(item['price'])}</dd></div>
    </dl>
    <div class="detail-cta">
      <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text about this item: <span data-config="phone"></span></a>
      {mp_button}
    </div>
    <p class="appt-note">{esc(APPT_NOTE)}</p>
    <p class="guarantee-note">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies<br><span class="warranty-note">{esc(WARRANTY_NOTE)}</span></p>
  </div>
</div>"""
    return page_shell(
        f"{item['title']} | {item['price']} | {PLACEHOLDER_NAME}",
        meta_description(item, desc),
        body, "catalog", prefix="../")


def build_about():
    body = f"""<div class="wrap prose">
  <h1>About us</h1>
  <p data-config="aboutText">{esc(PLACEHOLDER_ABOUT)}</p>
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
        body, "about")


def build_faq():
    faqs = [
        ("What is your return policy?",
         "Every appliance comes with a 14-day money-back guarantee. If something "
         "isn't right, let us know within 14 days and we'll make it right."),
        ("Do you deliver?",
         "Yes — delivery is available for a charge. The fee depends on distance; "
         "contact us for a quote."),
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
        body, "faq")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def main():
    items, descriptions = load_data()
    print(f"Loaded {len(items)} listings, {len(descriptions)} descriptions.")
    copy_photos(items)
    photo_of = {it["listing_id"]: [os.path.basename(p) for p in resolve_photos(it)]
                for it in items}

    os.makedirs(LISTINGS_DIR, exist_ok=True)
    write(os.path.join(OUT_DIR, "index.html"), build_index(items, photo_of))
    for it in items:
        write(os.path.join(LISTINGS_DIR, f"{it['listing_id']}.html"),
              build_detail(it, descriptions, photo_of[it["listing_id"]]))
    write(os.path.join(OUT_DIR, "about.html"), build_about())
    write(os.path.join(OUT_DIR, "faq.html"), build_faq())
    print(f"Wrote index.html, about.html, faq.html, {len(items)} listing pages.")


if __name__ == "__main__":
    main()
