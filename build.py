#!/usr/bin/env python3
"""
Builds the inner pages of the Angelos C. Painting Inc. site from a shared
header/footer shell so the chrome stays identical across pages.

Run:  python3 build.py
Edits to the header, footer, top bar or mobile call bar should be made HERE
and rebuilt, otherwise the pages will drift apart.

index.html's BODY is hand-maintained, but its header is not: the file carries
<!-- HEADER:START --> / <!-- HEADER:END --> markers and this script rewrites
whatever sits between them, so the nav (including the Services and Areas
dropdowns) can never drift from the inner pages.

Nav dropdown contents are data-driven:
  SERVICES        -> the Services dropdown
  FEATURED_TOWNS  -> the "Popular towns" columns in the Areas dropdown
  COUNTIES        -> the "Counties" column in the Areas dropdown
Add a town to FEATURED_TOWNS and it appears in the menu; its link resolves
because every town on areas.html gets an id from town_slug().

Photo galleries are data-driven too: each service has a folder under
images/ourwork/ and a generated our-work-<folder>.html page that is built by
SCANNING that folder. To add photos, drop the files into the folder and re-run
this script. Name files like  interior-painting-13.jpg  (lowercase, hyphens,
trailing number) because the filename becomes the photo's alt text.
"""

import io, os, re, sys

CDN = "https://assets.cdn.filesafe.space/9COp2d5jFrBGXiysHCUm/media/"
IMG = {
    "logo":     CDN + "69dd23744753e162ccd8365d.png",
    "badge":    CDN + "69dd6703e34cc263fb7f5f3a.png",
    "bath":     CDN + "69dd17f3ef1dbfe76e00d2ee.png",
    "paint":    CDN + "69dd1829caf24b80a0e6d243.png",
    "drywall":  CDN + "69dd1850376904eac21a330a.png",
    "map":      CDN + "69dd6ef8ef1dbfe76e1746eb.png",
    "p1":       CDN + "69dd2e49e68d42fa04a32ff9.webp",
    "p2":       CDN + "69dd2e4802cd38b17c3a3b0c.webp",
    "p3":       CDN + "69dd2e49caf24b80a0eceb03.webp",
    "p4":       CDN + "69dd2e48caf24b80a0eceaf3.webp",
    "p5":       CDN + "69dd2e484753e162ccdb0c41.webp",
    "p6":       CDN + "69dd2e49e68d42fa04a33022.webp",
    "p7":       CDN + "69dd2e4902cd38b17c3a3b24.webp",
    "p8":       CDN + "69dd2e4ae68d42fa04a3304c.webp",
}

HERE = os.path.dirname(os.path.abspath(__file__))

# Cover photo for each service (16:10, shown on the service cards). Files live in
# images/services/ — swap a file there (same name) to change a cover.
SERVICE_IMG = {k: f"images/services/{k}.jpg"
               for k in ("interior", "exterior", "bathroom", "drywall", "flooring", "deck", "handyman")}

# ----------------------------------------------------------------- data ----

SERVICES = [
    ("interior", "Interior Painting", SERVICE_IMG["interior"],
     "Walls, ceilings, trim and doors brought back to life. We move and cover furniture, mask edges, patch and sand before a single drop of paint goes on, and we clean up completely at the end of every day.",
     ["Walls, ceilings, trim, doors and closets",
      "Patching, sanding and priming included",
      "Furniture moved and floors fully protected",
      "Color and sheen guidance if you want it",
      "Occupied homes worked around your schedule"]),
    ("exterior", "Exterior Painting", SERVICE_IMG["exterior"],
     "Siding, trim, porches, railings and detail work. Hudson Valley weather is hard on a house — proper washing, scraping and priming is what separates a finish that lasts from one that peels in two winters.",
     ["Washing, scraping and spot-priming before paint",
      "Siding, trim, soffits, fascia, shutters and doors",
      "Porches, columns and railings",
      "Caulking and minor surface repairs",
      "Landscaping and walkways covered and protected"]),
    ("bathroom", "Shower &amp; Bathroom Remodeling", SERVICE_IMG["bathroom"],
     "A full bathroom refresh handled end to end — demolition, tile, fixtures, vanities and finish work — so you deal with one contractor instead of five.",
     ["Full and partial bathroom remodels",
      "Shower and tub surrounds rebuilt",
      "Tile floors and walls",
      "Vanities, mirrors, lighting and fixtures",
      "Waterproofing and prep done properly"]),
    ("drywall", "Drywall Installation &amp; Repair", SERVICE_IMG["drywall"],
     "New walls, ceiling repairs, water damage, cracks, nail pops and holes. Taped, coated and sanded smooth so the paint that follows looks like the wall was always that way.",
     ["New drywall hung and finished",
      "Water damage and ceiling repairs",
      "Crack, hole and nail-pop patching",
      "Taping, coating and skim coating",
      "Texture matching on existing walls"]),
    ("flooring", "Laminate Floor Installation", SERVICE_IMG["flooring"],
     "Durable, great-looking laminate flooring installed with tight seams, level subfloor prep, clean transitions and proper trim and moulding.",
     ["Subfloor checked and prepped",
      "Laminate and click-lock plank installation",
      "Transitions, thresholds and reducers",
      "Baseboard, quarter-round and shoe moulding",
      "Old flooring removed and hauled out"]),
    ("deck", "Deck &amp; Fence Staining", SERVICE_IMG["deck"],
     "Cleaning, prep and staining that protects outdoor wood from sun, rain and snow — and brings a grey, weathered deck back to something you want to sit on.",
     ["Deck, railing, fence and outdoor wood",
      "Cleaning and stripping of old finish",
      "Sanding and board repairs",
      "Semi-transparent, solid and clear finishes",
      "Sealing to resist moisture and UV"]),
    ("handyman", "Additional Handyman Services", SERVICE_IMG["handyman"],
     "The smaller jobs that come with any project — and the ones that have been on the list for a year. If it's connected to painting or remodeling, ask us.",
     ["Trim, moulding and carpentry repairs",
      "Doors, hardware and fixture swaps",
      "Power washing and surface prep",
      "Punch-list and touch-up work",
      "Commercial property maintenance"]),
]

TOWNS = """Amawalk, Ardsley, Ardsley on Hudson, Armonk, Bedford, Bedford Hills, Briarcliff Manor,
Bronxville, Buchanan, Chappaqua, Cortlandt Manor, Cross River, Croton Falls, Croton on Hudson,
Dobbs Ferry, Eastchester, Elmsford, Goldens Bridge, Granite Springs, Harrison, Hartsdale,
Hastings on Hudson, Hawthorne, Irvington, Jefferson Valley, Katonah, Larchmont, Mamaroneck,
Millwood, Mohegan Lake, Montrose, Mount Kisco, Mount Vernon, New Rochelle, North Salem, Ossining,
Peekskill, Pelham, Pleasantville, Port Chester, Pound Ridge, Purchase, Purdys, Rye, Rye Brook,
Scarsdale, Shrub Oak, Sleepy Hollow, Somers, South Salem, Tarrytown, Thornwood, Tuckahoe, Valhalla,
Waccabuc, West Harrison, White Plains, Yonkers, Yorktown Heights"""
TOWN_LIST = [t.strip() for t in TOWNS.replace("\n", " ").split(",") if t.strip()]


# ---------------------------------------------------------------- shell ----

def head(title, desc, canonical):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://www.angelospropainting.com/{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{IMG['p1']}">
<link rel="icon" href="{IMG['logo']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
"""

ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
ICON_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/></svg>'
ICON_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'

TOPBAR = f"""<div class="topbar">
  <div class="wrap">
    <div class="topbar__items">
      <span class="topbar__item">{ICON_PIN} 29-A Broad Avenue, Ossining, NY 10562</span>
      <span class="topbar__item">{ICON_CLOCK} Available 24/7</span>
    </div>
    <div class="topbar__items">
      <a class="topbar__item" href="tel:+19143843187">{ICON_PHONE} (914) 384-3187</a>
      <a class="topbar__item" href="tel:+19142369110">(914) 236-9110</a>
    </div>
  </div>
</div>
"""

ICON_CARET = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'


def town_slug(name):
    """Town name -> anchor id used on areas.html."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Towns promoted into the Areas dropdown. Everything else stays on areas.html.
FEATURED_TOWNS = [
    "Ossining", "White Plains", "Yonkers", "Scarsdale", "Tarrytown",
    "Chappaqua", "Briarcliff Manor", "Croton on Hudson", "Peekskill",
    "Mount Kisco",
]

COUNTIES = ["Westchester County", "Rockland County", "Orange County", "Putnam County"]


def _services_dd():
    items = "\n            ".join(
        f'<li><a href="services.html#{s}">{n}</a></li>'
        for s, n, _i, _b, _bl in SERVICES)
    return f"""<div class="dd">
          <div class="dd__inner">
            <div class="dd__col">
              <h5>What we do</h5>
              <ul class="dd__list">
            {items}
              </ul>
            </div>
            <div class="dd__foot">
              <a class="dd__all" href="services.html">All services &rarr;</a>
            </div>
          </div>
        </div>"""


def _areas_dd():
    """Three balanced columns: counties, then the featured towns split in half."""
    counties = "\n            ".join(
        f'<li><a href="areas.html#counties">{c}</a></li>' for c in COUNTIES)
    half = (len(FEATURED_TOWNS) + 1) // 2
    col_a, col_b = FEATURED_TOWNS[:half], FEATURED_TOWNS[half:]
    fmt = lambda ts: "\n            ".join(
        f'<li><a href="areas.html#{town_slug(t)}">{t}, NY</a></li>' for t in ts)
    return f"""<div class="dd dd--wide">
          <div class="dd__inner">
            <div class="dd__col">
              <h5>Counties</h5>
              <ul class="dd__list">
            {counties}
              </ul>
            </div>
            <div class="dd__col">
              <h5>Popular towns</h5>
              <ul class="dd__list">
            {fmt(col_a)}
              </ul>
            </div>
            <div class="dd__col">
              <h5 class="dd__spacer">&nbsp;</h5>
              <ul class="dd__list">
            {fmt(col_b)}
              </ul>
            </div>
            <div class="dd__foot">
              <a class="dd__all" href="areas.html">All service areas &rarr;</a>
            </div>
          </div>
        </div>"""


HEADER = f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html">
      <img src="{IMG['logo']}" alt="Angelos C. Painting Inc. Home Improvement">
    </a>
    <nav class="nav" id="primary-nav" aria-label="Primary">
      <a class="nav__link" href="index.html">Home</a>
      <a class="nav__link" href="about.html">About</a>

      <div class="nav__item">
        <a class="nav__link" href="services.html">Services</a>
        <button class="dd-toggle" type="button" aria-expanded="false" aria-label="Show services menu">{ICON_CARET}</button>
        {_services_dd()}
      </div>

      <a class="nav__link" href="gallery.html">Portfolio</a>

      <div class="nav__item">
        <a class="nav__link" href="areas.html">Areas</a>
        <button class="dd-toggle" type="button" aria-expanded="false" aria-label="Show service areas menu">{ICON_CARET}</button>
        {_areas_dd()}
      </div>

      <a class="nav__link" href="contact.html">Contact</a>
      <a class="btn btn--primary" href="contact.html">Free Estimate</a>
    </nav>
    <div class="header-cta">
      <a class="header-phone" href="tel:+19143843187">
        <span>Call for a free estimate</span>
        <strong>(914) 384-3187</strong>
      </a>
      <a class="btn btn--primary" href="contact.html">Free Estimate</a>
      <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="primary-nav">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      </button>
    </div>
  </div>
</header>
"""

def pagehero(crumb, h1, sub, bg=None):
    bg_html = (f'<div class="pagehero__bg"><img src="{bg}" alt="" aria-hidden="true"></div>'
               if bg else "")
    return f"""<section class="pagehero">
  {bg_html}
  <div class="wrap">
    <p class="crumbs"><a href="index.html">Home</a> &nbsp;/&nbsp; {crumb}</p>
    <h1>{h1}</h1>
    <p>{sub}</p>
  </div>
</section>
"""

CTA_BAND = """<section class="cta-band">
  <div class="wrap">
    <div class="cta-band__inner">
      <div>
        <h2>Ready to get your project handled?</h2>
        <p>Tell us what you have in mind and we'll come out for a free, no-obligation estimate. We answer the phone 24/7.</p>
      </div>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html">Request a Free Estimate</a>
        <a class="btn btn--outline-light" href="tel:+19143843187">(914) 384-3187</a>
      </div>
    </div>
  </div>
</section>
"""

SOCIALS = """<div class="socials">
          <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7h-2.5V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.3c-1.2 0-1.6.8-1.6 1.6V12h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12z"/></svg></a>
          <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor" stroke="none"/></svg></a>
          <a href="#" aria-label="YouTube"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 12s0-3.2-.4-4.7a3 3 0 0 0-2.1-2.1C18.9 4.8 12 4.8 12 4.8s-6.9 0-8.5.4a3 3 0 0 0-2.1 2.1C1 8.8 1 12 1 12s0 3.2.4 4.7a3 3 0 0 0 2.1 2.1c1.6.4 8.5.4 8.5.4s6.9 0 8.5-.4a3 3 0 0 0 2.1-2.1C23 15.2 23 12 23 12zM9.8 15.3V8.7l5.7 3.3-5.7 3.3z"/></svg></a>
          <a href="#" aria-label="X"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.2 2h3.3l-7.2 8.3L22.8 22h-6.6l-5.2-6.8L5.1 22H1.8l7.7-8.8L1.5 2h6.8l4.7 6.2L18.2 2zm-1.2 18h1.8L7.1 3.9H5.2L17 20z"/></svg></a>
          <a href="#" aria-label="Houzz"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 2v6.5L18 12v10h-5v-5h-2v5H6V2z"/></svg></a>
        </div>"""

FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{IMG['logo']}" alt="Angelos C. Painting Inc.">
        <p class="footer-tag">Quality work. Fair prices.</p>
        <p>Professional painting and remodeling for residential and commercial clients across the lower Hudson Valley for over 25 years.</p>
        {SOCIALS}
      </div>
      <div>
        <h4>Services</h4>
        <ul class="footer-list">
          <li><a href="services.html#interior">Interior Painting</a></li>
          <li><a href="services.html#exterior">Exterior Painting</a></li>
          <li><a href="services.html#bathroom">Bathroom Remodeling</a></li>
          <li><a href="services.html#drywall">Drywall &amp; Repair</a></li>
          <li><a href="services.html#flooring">Laminate Flooring</a></li>
          <li><a href="services.html#deck">Deck &amp; Fence Staining</a></li>
          <li><a href="services.html#handyman">Handyman Services</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul class="footer-list">
          <li><a href="about.html">About Us</a></li>
          <li><a href="gallery.html">Portfolio</a></li>
          <li><a href="areas.html">Service Areas</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="contact.html">Free Estimate</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul class="footer-list">
          <li>29-A Broad Avenue<br>Ossining, NY 10562</li>
          <li><a href="tel:+19143843187">(914) 384-3187</a></li>
          <li><a href="tel:+19142369110">(914) 236-9110</a></li>
          <li><a href="mailto:angelosphi12@gmail.com">angelosphi12@gmail.com</a></li>
          <li>Available 24/7</li>
          <li>Payment: cash &amp; check</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> Angelos C. Painting Inc. Home Improvement. All rights reserved.</span>
      <span>Ossining, NY &middot; Serving Westchester, Rockland, Orange &amp; Putnam Counties</span>
    </div>
  </div>
</footer>

<div class="callbar">
  <a class="callbar__call" href="tel:+19143843187">{ICON_PHONE} Call Now</a>
  <a class="callbar__quote" href="contact.html">Free Estimate</a>
</div>

<script src="assets/js/main.js"></script>
</body>
</html>
"""

def page(filename, title, desc, hero, body):
    html = head(title, desc, filename) + TOPBAR + HEADER + hero + body + CTA_BAND + FOOTER
    with io.open(os.path.join(HERE, filename), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", filename, len(html), "bytes")




# ---------------------------------------------------------------- about ----

about_body = f"""
<section class="section">
  <div class="wrap">
    <div class="split">
      <div class="split__media split__media--stack">
        <img src="{IMG['p6']}" alt="Finished interior painting work" loading="lazy">
        <img src="{IMG['p7']}" alt="Remodeled bathroom" loading="lazy">
        <img src="{IMG['p8']}" alt="Detail of finish carpentry" loading="lazy">
      </div>
      <div>
        <hr class="rule">
        <p class="eyebrow">Our story</p>
        <h2>Built on craftsmanship and trust</h2>
        <p>Angelos C. Painting Inc. is a professional painting and remodeling company based in Ossining, NY, dedicated to delivering reliable and high-quality services to residential and commercial clients.</p>
        <p>Over more than 25 years, we've built the business one job at a time — on referrals and repeat customers. We combine hands-on expertise with a customer-centered approach to deliver efficient, detail-oriented solutions that enhance property value and increase client satisfaction.</p>
        <p>We're available 24/7 with flexible scheduling and complimentary estimates, serving Rockland, Westchester, Orange and Putnam Counties.</p>
        <div class="btn-row" style="margin-top:1.6rem">
          <a class="btn btn--primary" href="contact.html">Request a Free Estimate</a>
          <a class="btn btn--ghost" href="services.html">Our Services</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    <div class="grid grid--2">
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
        <h3>Our Mission</h3>
        <p>Deliver high-quality painting and remodeling services that enhance spaces and exceed client expectations.</p>
      </div>
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg></div>
        <h3>Our Vision</h3>
        <p>Be recognized as a leading service provider in New York through reliability, consistency, and customer satisfaction.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">What we stand on</p>
      <h2>Our core values</h2>
      <p class="lede">The same four things have driven every job for 25 years.</p>
    </div>
    <div class="grid grid--4">
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 4 6v6c0 5 3.4 9.4 8 10 4.6-.6 8-5 8-10V6l-8-4z"/><path d="m9 12 2 2 4-4"/></svg></div>
        <h3>Quality Craftsmanship</h3>
        <p>Proper prep, quality materials, and finish work we'd accept in our own homes.</p>
      </div>
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></div>
        <h3>Attention to Detail</h3>
        <p>Straight lines, clean edges, and the small things most people only notice when they're wrong.</p>
      </div>
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="M5 7h14"/><path d="m5 7 3 7H2l3-7z"/><path d="m19 7 3 7h-6l3-7z"/></svg></div>
        <h3>Integrity &amp; Transparency</h3>
        <p>A written estimate up front, honest advice about what a job actually needs, and no surprise line items.</p>
      </div>
      <div class="tile">
        <div class="tile__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 1 0-7.8 7.8l8.8 8.8 8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/></svg></div>
        <h3>Customer Satisfaction</h3>
        <p>We walk the finished job with you. It's not done until you say it's done.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--navy">
  <div class="wrap">
    <div class="split">
      <div>
        <hr class="rule">
        <p class="eyebrow">At a glance</p>
        <h2>The essentials</h2>
        <ul class="checklist">
          <li>{ICON_CHECK} Over 25 years of experience</li>
          <li>{ICON_CHECK} Residential &amp; commercial services</li>
          <li>{ICON_CHECK} Free estimates available</li>
          <li>{ICON_CHECK} Available 24/7, flexible scheduling</li>
          <li>{ICON_CHECK} Serving Rockland, Westchester, Orange &amp; Putnam Counties</li>
          <li>{ICON_CHECK} Payment methods: cash and check</li>
        </ul>
      </div>
      <div class="split__media">
        <img src="{IMG['p1']}" alt="Angelos C. Painting project" loading="lazy">
      </div>
    </div>
  </div>
</section>
"""

page("about.html",
     "About Angelos C. Painting Inc. | 25+ Years in Ossining, NY",
     "Angelos C. Painting Inc. is a painting and remodeling company based in Ossining, NY, serving residential and commercial clients across Westchester, Rockland, Orange and Putnam Counties for over 25 years.",
     pagehero("About", "About Angelos C. Painting Inc.",
              "A painting and remodeling company built in Ossining, NY on 25 years of careful work and repeat customers.",
              IMG["p6"]),
     about_body)


# ------------------------------------------------------- our-work pages ----
# One photo-gallery page per service. Photos live in images/ourwork/<folder>/
# and each page is built by SCANNING that folder, so adding a photo is:
#     1. drop the file into the folder   2. python3 build.py   3. commit
# Photos appear in filename order. Name them like  interior-painting-13.jpg
# (lowercase, hyphens, trailing number): the filename becomes the alt text.

try:
    from PIL import Image          # optional: lets us set width/height on every
except ImportError:                # <img> so the page doesn't jump while loading
    Image = None

WORK_ROOT = "images/ourwork"
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")

# service slug (see SERVICES) -> (image folder, gallery page filename)
WORK = {
    "interior": ("interior",    "our-work-interior.html"),
    "exterior": ("exterior",    "our-work-exterior.html"),
    "bathroom": ("shower-bath", "our-work-shower-bath.html"),
    "drywall":  ("drywall",     "our-work-drywall.html"),
    "flooring": ("laminate",    "our-work-laminate.html"),
    "deck":     ("deck-fence",  "our-work-deck-fence.html"),
    "handyman": ("handyman",    "our-work-handyman.html"),
}


def _natural(s):
    """Sort key so photo-2 comes before photo-10."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def _alt_from_filename(fname):
    """power-washing-03.jpg -> 'Power washing project photo 3'."""
    stem = os.path.splitext(fname)[0]
    m = re.match(r"^(.*?)[-_ ]?(\d+)$", stem)
    base, num = (m.group(1), int(m.group(2))) if m else (stem, None)
    label = re.sub(r"[-_]+", " ", base).strip() or "Project"
    label = label[0].upper() + label[1:]
    return f"{label} project photo {num}" if num is not None else label


def work_images(folder):
    """[(src, width, height, alt)] for every image in images/ourwork/<folder>."""
    d = os.path.join(HERE, WORK_ROOT, folder)
    if not os.path.isdir(d):
        return []
    names = sorted((f for f in os.listdir(d) if f.lower().endswith(IMG_EXT)), key=_natural)
    out = []
    for n in names:
        w = h = None
        if Image is not None:
            try:
                with Image.open(os.path.join(d, n)) as im:
                    w, h = im.size
            except Exception:
                pass
        out.append((f"{WORK_ROOT}/{folder}/{n}", w, h, _alt_from_filename(n)))
    return out


def work_page(slug, name, blurb):
    folder, filename = WORK[slug]
    plain = name.replace("&amp;", "and")
    imgs = work_images(folder)
    n = len(imgs)

    if imgs:
        items = "\n      ".join(
            f'<a class="work-item" href="{src}" data-lightbox>'
            f'<img src="{src}" alt="{alt}"'
            + (f' width="{w}" height="{h}"' if w and h else "")
            + ' loading="lazy"></a>'
            for src, w, h, alt in imgs)
        plural = "s" if n != 1 else ""
        grid = (f'<p class="work-count">{n} photo{plural} &middot; tap any photo to enlarge</p>\n'
                f'    <div class="work-grid">\n      {items}\n    </div>')
    else:
        grid = ('<div class="tile center" style="max-width:560px;margin:0 auto">'
                '<h3>Photos coming soon</h3>'
                '<p>We are adding project photos for this service. In the meantime, call '
                '<a href="tel:+19143843187">(914) 384-3187</a> and we can talk through your project.</p></div>')

    others = "\n        ".join(
        f'<a class="chip" href="{WORK[s][1]}">{nm}</a>'
        for s, nm, _i, _b, _bl in SERVICES if s != slug)

    body = f"""
<section class="section">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Our work</p>
      <h2>Project gallery</h2>
      <p class="lede">{blurb}</p>
    </div>
    {grid}
    <div class="btn-row center" style="margin-top:44px">
      <a class="btn btn--primary" href="contact.html">Get a free estimate</a>
      <a class="btn btn--ghost" href="services.html#{slug}">About this service</a>
    </div>
  </div>
</section>

<section class="section section--surface section--tight">
  <div class="wrap center">
    <p class="eyebrow">More of our work</p>
    <div class="county-chips" style="justify-content:center;margin:0">
        {others}
    </div>
  </div>
</section>
"""
    hero = pagehero(f'<a href="gallery.html">Portfolio</a> &nbsp;/&nbsp; {name}', name,
                    "Recent project photos from Angelos C. Painting Inc.")
    page(filename,
         f"{plain} Photos | Angelos C. Painting Inc.",
         f"Project photos for {plain} by Angelos C. Painting Inc., serving Westchester, Rockland, Orange and Putnam Counties, NY.",
         hero, body)


for _slug, _name, _img, _blurb, _bul in SERVICES:
    work_page(_slug, _name, _blurb)


# ------------------------------------------------------------- services ----

svc_cards = []
for slug, name, img, _blurb, _bul in SERVICES:
    svc_cards.append(f"""      <a class="card" href="#{slug}" style="text-decoration:none">
        <div class="card__media"><img src="{img}" alt="{re.sub('&amp;', 'and', name)}" loading="lazy"></div>
        <div class="card__body"><h3>{name}</h3><p>{_blurb[:110].rsplit(' ', 1)[0]}&hellip;</p>
        <span class="card__link">Learn more {ICON_ARROW}</span></div>
      </a>""")

svc_details = []
for i, (slug, name, img, blurb, bullets) in enumerate(SERVICES):
    rev = " split--reverse" if i % 2 else ""
    lis = "\n          ".join(f"<li>{ICON_CHECK} {b}</li>" for b in bullets)
    bg = " section--surface" if i % 2 else ""
    svc_details.append(f"""<section class="section{bg}" id="{slug}">
  <div class="wrap">
    <div class="split{rev}">
      <div class="split__media"><img src="{img}" alt="{re.sub('&amp;', 'and', name)}" loading="lazy"></div>
      <div>
        <hr class="rule">
        <p class="eyebrow">Service {i+1:02d}</p>
        <h2>{name}</h2>
        <p>{blurb}</p>
        <ul class="checklist">
          {lis}
        </ul>
        <div class="btn-row">
          <a class="btn btn--primary" href="contact.html">Get a free estimate</a>
          <a class="btn btn--ghost" href="{WORK[slug][1]}">See our work</a>
        </div>
      </div>
    </div>
  </div>
</section>
""")

services_body = f"""
<section class="section section--tight">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Everything we do</p>
      <h2>Painting &amp; remodeling services</h2>
      <p class="lede">One contractor for the whole job. Jump to any service below, or call (914) 384-3187 and we'll talk it through.</p>
    </div>
    <div class="grid grid--3">
{chr(10).join(svc_cards)}
    </div>
  </div>
</section>

{''.join(svc_details)}

<section class="section section--navy">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">How it works</p>
      <h2>From first call to final walkthrough</h2>
    </div>
    <div class="steps">
      <div class="step"><div class="step__num">01</div><h3>Call or request online</h3><p>Reach us any time at (914) 384-3187, or send your details through the site. We answer 24/7.</p></div>
      <div class="step"><div class="step__num">02</div><h3>Free on-site estimate</h3><p>We look at the actual space, talk through options and colors, and give you a clear written price.</p></div>
      <div class="step"><div class="step__num">03</div><h3>Prep &amp; protection</h3><p>Furniture covered, floors protected, surfaces properly prepped. The prep is where a lasting finish is won.</p></div>
      <div class="step"><div class="step__num">04</div><h3>Finish &amp; walkthrough</h3><p>We complete the work, clean up fully, and walk the job with you before we call it done.</p></div>
    </div>
  </div>
</section>
"""

page("services.html",
     "Painting &amp; Remodeling Services | Angelos C. Painting Inc.",
     "Interior and exterior painting, shower and bathroom remodeling, drywall installation and repair, laminate flooring, deck and fence staining, and handyman services across Westchester County, NY.",
     pagehero("Services", "Our Services",
              "Interior and exterior painting, bathroom remodeling, drywall, flooring, deck staining and handyman work &mdash; all handled by our own crew.",
              IMG["paint"]),
     services_body)


# -------------------------------------------------------------- gallery ----

gal_imgs = [IMG[k] for k in ("p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8")]
gal_figs = "\n      ".join(
    f'<figure><img src="{u}" alt="Angelos C. Painting project {i+1}" loading="lazy"></figure>'
    for i, u in enumerate(gal_imgs))

gallery_body = f"""
<section class="section">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Recent projects</p>
      <h2>Our work across Westchester</h2>
      <p class="lede">Painting and remodeling projects completed for homeowners and businesses across the lower Hudson Valley.</p>
    </div>
    <div class="gallery">
      {gal_figs}
    </div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Before &amp; after</p>
      <h2>See the difference</h2>
      <p class="lede">Swap these pairs for your own before/after shots &mdash; they are the single most persuasive thing on a painting website.</p>
    </div>
    <div class="ba">
      <div class="ba__item">
        <div class="ba__pair">
          <figure><figcaption>Before</figcaption><img src="{IMG['p3']}" alt="Exterior repaint before" loading="lazy"></figure>
          <figure><figcaption>After</figcaption><img src="{IMG['p2']}" alt="Exterior repaint after" loading="lazy"></figure>
        </div>
        <div class="ba__meta"><h3>Exterior repaint</h3><p>Westchester County, NY</p></div>
      </div>
      <div class="ba__item">
        <div class="ba__pair">
          <figure><figcaption>Before</figcaption><img src="{IMG['p8']}" alt="Bathroom remodel before" loading="lazy"></figure>
          <figure><figcaption>After</figcaption><img src="{IMG['bath']}" alt="Bathroom remodel after" loading="lazy"></figure>
        </div>
        <div class="ba__meta"><h3>Shower &amp; bathroom remodel</h3><p>Ossining, NY</p></div>
      </div>
      <div class="ba__item">
        <div class="ba__pair">
          <figure><figcaption>Before</figcaption><img src="{IMG['p7']}" alt="Interior repaint before" loading="lazy"></figure>
          <figure><figcaption>After</figcaption><img src="{IMG['paint']}" alt="Interior repaint after" loading="lazy"></figure>
        </div>
        <div class="ba__meta"><h3>Interior repaint</h3><p>Westchester County, NY</p></div>
      </div>
    </div>
    <p class="form-note center" style="margin-top:26px">Note for the site owner: the pairs above reuse existing portfolio photos as placeholders. Replace each with a true before and after of the same room or elevation.</p>
  </div>
</section>
"""

page("gallery.html",
     "Portfolio &amp; Before/After Gallery | Angelos C. Painting Inc.",
     "Photos of recent painting and remodeling projects by Angelos C. Painting Inc. across Westchester County and the lower Hudson Valley.",
     pagehero("Portfolio", "Our Portfolio",
              "Recent painting and remodeling projects across Westchester, Rockland, Orange and Putnam Counties.",
              IMG["p5"]),
     gallery_body)


# ---------------------------------------------------------------- areas ----

town_lis = "\n      ".join(f'<li id="{town_slug(t)}">{t}</li>' for t in TOWN_LIST)

areas_body = f"""
<section class="section">
  <div class="wrap">
    <div class="split split--reverse">
      <div class="split__media"><img src="{IMG['map']}" alt="Angelos C. Painting service area map" loading="lazy"></div>
      <div>
        <hr class="rule">
        <p class="eyebrow">Where we work</p>
        <h2>Four counties, 60+ towns</h2>
        <p>Angelos C. Painting Inc. serves Rockland, Westchester, Orange and Putnam Counties from our base at 29-A Broad Avenue in Ossining, NY.</p>
        <p>If your town isn't on the list below, call us anyway &mdash; we regularly travel for larger projects.</p>
        <div class="county-chips" id="counties">
          <span class="chip">Westchester County</span>
          <span class="chip">Rockland County</span>
          <span class="chip">Orange County</span>
          <span class="chip">Putnam County</span>
        </div>
        <a class="btn btn--primary" href="contact.html">Check your address</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Towns &amp; villages</p>
      <h2>Communities we serve</h2>
    </div>
    <ul class="area-cols">
      {town_lis}
    </ul>
  </div>
</section>
"""

page("areas.html",
     "Service Areas | Painting &amp; Remodeling in Westchester County, NY",
     "Angelos C. Painting Inc. serves Rockland, Westchester, Orange and Putnam Counties, NY — including Ossining, White Plains, Yonkers, Scarsdale, Tarrytown, Peekskill and 60+ more towns.",
     pagehero("Service Areas", "Service Areas",
              "Painting and remodeling across Rockland, Westchester, Orange and Putnam Counties, New York.",
              IMG["map"]),
     areas_body)


# -------------------------------------------------------------- contact ----

svc_options = "\n            ".join(
    f'<option>{re.sub("&amp;", "&", n)}</option>' for _s, n, _i, _b, _bl in SERVICES)

contact_body = f"""
<section class="section">
  <div class="wrap">
    <div class="split">
      <div>
        <hr class="rule">
        <p class="eyebrow">Get in touch</p>
        <h2>Request your free estimate</h2>
        <p class="lede">Tell us what you're planning and we'll get back to you to schedule a free, no-obligation on-site estimate. Prefer to talk? We answer the phone 24/7.</p>

        <ul class="contact-list">
          <li>
            <span class="ci">{ICON_PHONE}</span>
            <div><strong>Phone</strong>
              <a href="tel:+19143843187">(914) 384-3187</a><br>
              <a href="tel:+19142369110">(914) 236-9110</a>
            </div>
          </li>
          <li>
            <span class="ci">{ICON_MAIL}</span>
            <div><strong>Email</strong><a href="mailto:angelosphi12@gmail.com">angelosphi12@gmail.com</a></div>
          </li>
          <li>
            <span class="ci">{ICON_PIN}</span>
            <div><strong>Address</strong><span>29-A Broad Avenue, Ossining, NY 10562</span></div>
          </li>
          <li>
            <span class="ci">{ICON_CLOCK}</span>
            <div><strong>Business hours</strong><span>Available 24/7</span></div>
          </li>
        </ul>

        <div class="grid grid--2" style="margin-top:34px;gap:16px">
          <div class="tile"><h3>Over 25 years</h3><p>Serving residential and commercial clients for over 25 years.</p></div>
          <div class="tile"><h3>Payment methods</h3><p>Cash and check accepted.</p></div>
        </div>
      </div>

      <div class="form-card">
        <h3 style="margin-bottom:1rem">Message us</h3>
        <form data-estimate-form="angelosphi12@gmail.com" novalidate>
          <div class="field-row">
            <div class="field">
              <label for="name">Name</label>
              <input id="name" name="name" type="text" autocomplete="name" required>
            </div>
            <div class="field">
              <label for="phone">Phone</label>
              <input id="phone" name="phone" type="tel" autocomplete="tel" required>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="email">Email</label>
              <input id="email" name="email" type="email" autocomplete="email">
            </div>
            <div class="field">
              <label for="town">Town</label>
              <input id="town" name="town" type="text" placeholder="e.g. Ossining, NY">
            </div>
          </div>
          <div class="field">
            <label for="service">Service needed</label>
            <select id="service" name="service">
            <option value="">Select a service&hellip;</option>
            {svc_options}
            <option>Something else</option>
            </select>
          </div>
          <div class="field">
            <label for="message">Project details</label>
            <textarea id="message" name="message" placeholder="Rooms, square footage, timeline, anything else we should know."></textarea>
          </div>
          <label class="consent">
            <input type="checkbox" name="consent" required>
            <span>I confirm that I want to receive content from this company using any contact information I provide.</span>
          </label>
          <button class="btn btn--primary" type="submit" style="width:100%;justify-content:center">Send Your Message</button>
          <p class="form-note">This form is not connected to a mail server yet &mdash; submitting it opens your email app with the details filled in. Wire it to your CRM or form endpoint before launch.</p>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight section--surface">
  <div class="wrap">
    <div class="section-head center">
      <hr class="rule">
      <p class="eyebrow">Find us</p>
      <h2>29-A Broad Avenue, Ossining NY</h2>
    </div>
    <iframe class="map-embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Map to 29 Broad Ave, Ossining, NY 10562"
      src="https://www.google.com/maps?q=29+Broad+Ave+a,+Ossining,+NY+10562&output=embed"></iframe>
  </div>
</section>
"""

page("contact.html",
     "Contact Angelos C. Painting Inc. | Free Estimates, Ossining NY",
     "Call (914) 384-3187 or send a message to request a free painting or remodeling estimate. Angelos C. Painting Inc., 29-A Broad Avenue, Ossining, NY 10562. Available 24/7.",
     pagehero("Contact", "Contact Us",
              "Reach out to request your free estimate or schedule your service. We're available 24/7.",
              IMG["p4"]),
     contact_body)

print("\nBuild complete.")


# --------------------------------------------------------- index sync ----
# index.html is hand-written, but its header must not drift from the one the
# inner pages get. It carries HEADER:START / HEADER:END markers; we rewrite
# whatever sits between them on every build.

def sync_index():
    path = os.path.join(HERE, "index.html")
    if not os.path.exists(path):
        print("index.html not found - skipping header sync")
        return
    src = io.open(path, encoding="utf-8").read()
    a, b = "<!-- HEADER:START -->", "<!-- HEADER:END -->"
    if a not in src or b not in src:
        print("WARNING: index.html has no HEADER markers - header NOT synced")
        return
    pre, _, tail = src.partition(a)
    _, _, post = tail.partition(b)
    out = pre + a + "\n" + HEADER + b + post
    io.open(path, "w", encoding="utf-8").write(out)
    print("synced header into index.html")


sync_index()
