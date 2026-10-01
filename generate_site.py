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
PLACEHOLDER_RATING = "Rated 4.9 stars from 273+ Facebook Marketplace ratings"

FILTERS = ["All", "Washers", "Dryers", "Refrigerators", "Ranges",
           "Freezers", "Dishwashers", "Ovens"]


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
    if not photos:
        photos.append(item["photo"])  # stock fallback, e.g. stock/dryer.jpg
    return photos


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
      <a class="btn btn-call" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
      <a class="btn btn-fb" data-config-href="facebookGroupUrl" hidden>Visit our Facebook group: <span data-config="facebookGroupName"></span></a>
    </div>
  </div>
  <div class="wrap footer-small">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies</div>
</footer>
<script src="{prefix}site.js"></script>"""


def page_shell(title, meta_desc, body, active, prefix=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta_desc)}">
<link rel="stylesheet" href="{prefix}styles.css">
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
    return f"""<article class="card" data-cats="{cats}">
  <a href="listings/{item['listing_id']}.html" class="card-link">
    <div class="card-img"><img src="images/{esc(photo_file)}" alt="{esc(item['title'])}" loading="lazy"></div>
    <div class="card-body">
      <span class="badge">{esc(item['category'])}</span>
      <h3>{esc(item['title'])}</h3>
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
    body = f"""<section class="hero">
  <div class="wrap">
    <h1 data-config="businessName">{esc(PLACEHOLDER_NAME)}</h1>
    <p class="tagline" data-config="tagline">{esc(PLACEHOLDER_TAGLINE)}</p>
    <p class="rating" data-config="ratingText">{esc(PLACEHOLDER_RATING)}</p>
    <p class="service-area">Serving <span data-config="serviceArea">{esc(PLACEHOLDER_AREA)}</span> and surrounding areas</p>
    <div class="hero-cta">
      <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text: <span data-config="phone"></span></a>
      <a class="btn btn-fb btn-lg" data-config-href="facebookGroupUrl" hidden>Facebook group: <span data-config="facebookGroupName"></span></a>
    </div>
  </div>
</section>
<section class="wrap">
  <div class="filters">{filters}</div>
  <div class="grid" id="catalog-grid">
{cards}
  </div>
  <p class="grid-empty" id="grid-empty" hidden>No items in this category right now.</p>
</section>"""
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
    if len(photo_files) > 1:
        main = photo_files[0]
        thumbs = "\n".join(
            f'<button class="thumb{" current" if i == 0 else ""}" data-full="../images/{esc(pf)}">'
            f'<img src="../images/{esc(pf)}" alt="{esc(item["title"])} - photo {i + 1}"></button>'
            for i, pf in enumerate(photo_files)
        )
        gallery = f"""<div class="gallery">
      <img id="gallery-main" src="../images/{esc(main)}" alt="{esc(item['title'])}">
      <div class="thumbs">{thumbs}</div>
    </div>"""
    else:
        gallery = (f'<div class="gallery"><img src="../images/{esc(photo_files[0])}" '
                   f'alt="{esc(item["title"])}"></div>')
    mp_url = item.get("url", "")
    mp_button = (f'<a class="btn btn-fb btn-lg" href="{esc(mp_url)}">View this listing on Facebook Marketplace</a>'
                 if mp_url else "")
    body = f"""<div class="wrap detail">
  <p class="breadcrumb"><a href="../index.html">&larr; Back to catalog</a></p>
  {gallery}
  <div class="detail-info">
    <span class="badge">{esc(item['category'])}</span>
    <h1>{esc(item['title'])}</h1>
    <p class="price price-lg">{esc(item['price'])}</p>
    <div class="description">{desc_html}</div>
    <dl class="facts">
      <div><dt>Condition</dt><dd>{esc(item.get('condition', 'New'))}</dd></div>
      <div><dt>Category</dt><dd>{esc(item['category'])}</dd></div>
      <div><dt>Price</dt><dd>{esc(item['price'])}</dd></div>
    </dl>
    <div class="detail-cta">
      <a class="btn btn-call btn-lg" data-config-href="phoneHref" hidden>Call or text about this item: <span data-config="phone"></span></a>
      <a class="btn btn-fb btn-lg" data-config-href="facebookGroupUrl" hidden>Ask about this item in our Facebook group</a>
      {mp_button}
    </div>
    <p class="guarantee-note">14-day money-back guarantee &middot; Delivery available for a charge &middot; Sales tax applies</p>
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
  <p>Browse the catalog, find something you like, and get in touch. Every sale includes
  our 14-day money-back guarantee. Delivery is available for a charge, and sales tax
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
