"""Static site generator for Dr. Zico's website (v1).

Run:  python3 _build/build.py   (from the site root)
Output: one .html file per page in the site root, plus sitemap.xml, robots.txt
and assets/js/conditions.js. Edit content in _build/*.py, never in the output.

Next.js mapping: layout() -> app/layout.tsx, header()/footer() -> components,
each page_*() -> app/<slug>/page.tsx, SERVICES -> content/services.ts.
"""
import hashlib, json, os, re, html
from icons import icon, PORTRAIT_ART
from content_services import SERVICES
from images import img_attrs, largest, make_og_image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://neurosurgeonzico-ismaazam.com"
VERSION = "v1"

DOC = dict(
    name="Dr. Md. Isma Azam (Zico)", short="Dr. Zico",
    degrees="MBBS (DMC), BCS (Health), MRCS (England), MS (Neurosurgery)",
    phone_popular="09666 787801", phone_popular_intl="+8809666787801",
    phone_malibag="01927 333000", phone_malibag2="01830 279952",
    pa="(+88) 01716033364", pa_intl="+8801716033364",
    continental_hotline="10666",
    fb="https://www.facebook.com/isme.azam.37",
    yt="https://www.youtube.com/channel/UCeLQ_qqrxTXSDeMszqG8tDA",
    li="https://www.linkedin.com/in/md-isma-azam-zico-b11b6a19a/",
)
SV = {s["slug"]: s for s in SERVICES}
def total(s): return sum(n for sec in s["sections"] for _, n in sec["items"])
ALL_TOTAL = sum(total(s) for s in SERVICES)
SPINE_SLUGS = ["plid-lumbar-disc-surgery", "spine-surgery", "spinal-tumor-surgery", "spinal-tb-potts-disease"]
SPINE_TOTAL = sum(total(SV[s]) for s in SPINE_SLUGS)
BRAIN_TOTAL = ALL_TOTAL - SPINE_TOTAL
assert (ALL_TOTAL, SPINE_TOTAL, BRAIN_TOTAL) == (5010, 2647, 2363), (ALL_TOTAL, SPINE_TOTAL, BRAIN_TOTAL)

AC = ' aria-current="page"'
LBN = ' lang="bn"'
def fmt(n): return f"{n:,}"
def esc(s): return html.escape(s, quote=True)
IMAGES = []  # (page, file, size, label, what to shoot) -> written to IMAGES.md
with open(os.path.join(ROOT, "_build", "happy_patients.json"), encoding="utf-8") as f:
    HAPPY_PATIENTS = json.load(f)
with open(os.path.join(ROOT, "_build", "operating_theatre.json"), encoding="utf-8") as f:
    OPERATING_THEATRE = json.load(f)

# Temporary sample photos from Unsplash (free Unsplash License). Shown only while the real
# file is missing from assets/img/. Every sample carries a visible "Sample photo" badge.
UNS = "https://images.unsplash.com/"
SAMPLES = {
    "dr-zico-portrait.png": "photo-1645066928295-2506defde470",
    "dr-zico-about.jpg": "photo-1637059824899-a441006a6875",
    "ot-team-microscope.jpg": "photo-1579684385127-1ef15d508118",
    "team-photo.jpg": "photo-1516841273335-e39b37888115",
    "chamber-continental.jpg": "photo-1580615631392-aeb060d526e4",
    "chamber-popular-dhanmondi.jpg": "photo-1597807037496-c56a1d8bc29a",
    "chamber-malibag.jpg": "photo-1615770922480-0b9ae80afeba",
    "patient-1.jpg": "photo-1631217868264-e5b90bb7e133",
    "patient-2.jpg": "photo-1581056771107-24ca5f033842",
    "patient-3.jpg": "photo-1666886573531-48d2e3c2b684",
    "patient-4.jpg": "photo-1653491950066-bec107ee0536",
    "patient-5.jpg": "photo-1758691461935-202e2ef6b69f",
    "patient-6.jpg": "photo-1758691463198-dc663b8a64e4",
    "patient-7.jpg": "photo-1631217868264-e5b90bb7e133",
    "patient-8.jpg": "photo-1581056771107-24ca5f033842",
    "patient-story-1.jpg": "photo-1631217868264-e5b90bb7e133",
    "patient-story-2.jpg": "photo-1581056771107-24ca5f033842",
    "patient-story-3.jpg": "photo-1666886573531-48d2e3c2b684",
    "video-1-thumb.jpg": "photo-1758691462668-046fd85ceac9",
    "video-2-thumb.jpg": "photo-1758691461935-202e2ef6b69f",
    "gallery-ot-wide.jpg": "photo-1579684453423-f84349ef60b0",
    "gallery-exoscope.jpg": "photo-1551601651-2a8555f1a136",
    "gallery-microscope.jpg": "photo-1640876777012-bdb00a6323e2",
    "gallery-team.jpg": "photo-1504813184591-01572f98c85f",
    "gallery-teaching.jpg": "photo-1758691463198-dc663b8a64e4",
    "gallery-surgery-2.jpg": "photo-1740953448394-86122e98c1be",
    "gallery-surgery-3.jpg": "photo-1715634430473-c5891ff16103",
    "gallery-ward.jpg": "photo-1653491950066-bec107ee0536",
    "blog-komor-byatha-cover.jpg": "photo-1701826510629-051bb954fb8f",
    "plid-lumbar-disc-surgery-hero.jpg": "photo-1540205895360-4ad4cffb3aa8",
    "spine-surgery-hero.jpg": "photo-1763198302249-db661c45bf7d",
    "brain-tumor-surgery-hero.jpg": "photo-1631563019676-dade0dbdb8fc",
    "hydrocephalus-chiari-hero.jpg": "photo-1666214280165-20e3d73d70bf",
    "brain-aneurysm-stroke-surgery-hero.jpg": "photo-1740953448394-86122e98c1be",
    "spinal-tumor-surgery-hero.jpg": "photo-1763198302535-265c44183bcb",
    "spinal-tb-potts-disease-hero.jpg": "photo-1763198302745-57cb94135f11",
    "head-injury-cranioplasty-hero.jpg": "photo-1715634430473-c5891ff16103",
    "trigeminal-neuralgia-mvd-hero.jpg": "photo-1725399633872-32ba508b0607",
}
# Real photos of Dr. Zico given by the client (remote for now; save them into assets/img/ with these names)
REAL_REMOTE = {
    "dr-zico-portrait.png": "https://uhlbd.com/unitedhospitalapi/public/DoctorProfileImg/202510110749dr%20zico%20sir.jpg",
    "dr-zico-about.jpg": "https://old.populardiagnostic.com/public/doctor-image-from-software/5181-985493155.png",
    "ot-team-microscope.jpg": "https://scontent.fdac24-2.fna.fbcdn.net/v/t39.30808-6/511806396_3517139568418034_937724590642429314_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1536&ctp=s2048x1536&_nc_cat=108&ccb=1-7&_nc_sid=833d8c&_nc_ohc=CgXGbH0DDPcQ7kNvwFfrpT6&_nc_oc=AdrS0PC4qA4q6-eU4o_EIbx7K3Kh32qr06w6Cacoz2eRpSN4K64hm2RbsfFguqn5SO8&_nc_zt=23&_nc_ht=scontent.fdac24-2.fna&_nc_gid=jmkuJAud-HPj4Vfn7D64OA&_nc_ss=7b2a8&oh=00_AQOZatorLAzU80auQx-Eekq5-yw6F3B3z5mIdONft9Qsaw&oe=6ABFEDF5",
}
SPINE_SAMPLES = ["photo-1763198302249-db661c45bf7d", "photo-1763198302535-265c44183bcb", "photo-1763198302745-57cb94135f11", "photo-1769204978162-55d6fdb408ce"]
BRAIN_SAMPLES = ["photo-1725399633872-32ba508b0607", "photo-1679639539537-0d2e452890f7", "photo-1631563019676-dade0dbdb8fc", "photo-1758691462668-046fd85ceac9"]
_rot = {"spine": 0, "brain": 0}
def sample_for(path, w):
    file = path.rsplit("/", 1)[-1]  # samples are keyed by file name, folders do not matter
    if file in REAL_REMOTE:
        return REAL_REMOTE[file]
    sid = SAMPLES.get(file)
    if not sid:
        spine = file.startswith(("plid", "spine", "spinal")) or any(k in file for k in ("case-plid", "case-acdf", "case-spondylo", "case-fracture"))
        pool = SPINE_SAMPLES if spine else BRAIN_SAMPLES
        k = "spine" if spine else "brain"
        sid = pool[_rot[k] % len(pool)]; _rot[k] += 1
        SAMPLES[file] = sid
    return f"{UNS}{sid}?auto=format&fit=crop&w={min(w, 1800)}&q=70"
# ---- Image folders inside assets/img/ ----
# before-after/                    scans for the before/after cases (case-<id>-before.jpg / -after.jpg)
# services/<service-slug>/         every photo for one service page (hero, section images, photo carousel)
# happy-patient/, operating-theatre/  patient and OT photos (order in _build/*.json)
BA_DIR = "before-after"
def svc_img(slug, name):
    """Path (inside assets/img/) of an image that belongs to one service page."""
    return f"services/{slug}/{slug}-{name}"

# "sizes" hints: how wide each kind of image is shown, so the browser picks the smallest good file
SZ_HALF = "(max-width: 760px) 100vw, 45vw"
SZ_CARD = "(max-width: 560px) 86vw, (max-width: 1000px) 45vw, 300px"
SZ_FULL = "100vw"

def ph(file, w, h, label, desc, alt, page, cls="", caption="", sizes=SZ_HALF):
    """Image slot. Shows assets/img/<file> if it exists, otherwise a labelled placeholder.
    To fill a slot: save the photo with exactly this file name in assets/img/. No rebuild needed."""
    if not any(r[1] == file for r in IMAGES):
        IMAGES.append((page, file, f"{w}x{h}", label, desc))
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    smp = sample_for(file, w)
    kind = "real" if file.rsplit("/", 1)[-1] in REAL_REMOTE else "sample"
    missing_sample = kind != "real" and not os.path.isfile(os.path.join(ROOT, "assets", "img", file))
    return (f'<figure class="ph {cls}{" is-sample" if missing_sample else ""}" style="aspect-ratio:{w}/{h}"><div class="ph-inner" aria-hidden="true">{icon("image")}'
            f'<strong>{label}</strong><span class="ph-file">assets/img/{file}</span><span class="ph-desc">{w} x {h} px · {desc}</span></div>'
            + (f'<img {img_attrs(file, sizes)} data-sample="{esc(smp)}" data-kind="{kind}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async" onerror="dzImg(this)">'
               if os.path.isfile(os.path.join(ROOT, "assets", "img", file)) else
               f'<img src="{esc(smp)}" data-tried="1" data-kind="{kind}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async" onerror="dzImg(this)">')
            + f'{cap}</figure>')

def local_photo(file, w, h, label, alt, page, cls="", frame="ph is-real", sizes=SZ_HALF, eager=False):
    """A supplied local photo, without a remote sample fallback."""
    assert os.path.isfile(os.path.join(ROOT, "assets", "img", file)), file
    if not any(row[1] == file for row in IMAGES):
        IMAGES.append((page, file, f"{w}x{h}", label, alt))
    return (f'<figure class="{frame} {cls}" style="aspect-ratio:{w}/{h}">'
            f'<img {img_attrs(file, sizes)} data-kind="real" alt="{esc(alt)}" width="{w}" height="{h}" '
            + ('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"') + ' decoding="async"></figure>')


def operating_theatre_photos(page, lightbox=False):
    cards = []
    for photo in OPERATING_THEATRE:
        image = local_photo(photo["file"], photo["width"], photo["height"], photo["title"], photo["alt"], "About / Gallery", frame="ot-photo-frame")
        if lightbox:
            image = f'<button class="lb-item" type="button" data-lightbox aria-label="Open photo: {esc(photo["title"])}">{image}</button>'
        cards.append(image)
    return "".join(cards)


def v(text, note):  # an item that still needs the doctor's confirmation
    return f'<span class="verify" tabindex="0" data-note="{esc(note)}">{text}</span>'

# ------------------------------------------------------------------ schema
PHYSICIAN_ID = SITE_URL + "/#physician"
def physician_schema():
    return {
        "@context": "https://schema.org", "@type": "Physician", "@id": PHYSICIAN_ID,
        "name": DOC["name"], "alternateName": ["Dr. Zico", "Dr. Isma Azam Zico", "ডাঃ ইসমা আজম জিকো"],
        "url": SITE_URL + "/", "medicalSpecialty": "Neurosurgery",
        "image": f"{SITE_URL}/assets/img/{largest('dr-zico-portrait.png')}",
        "description": "Neurosurgeon in Dhaka treating brain and spine conditions: PLID, cervical spine, brain tumors, aneurysm, hydrocephalus.",
        "telephone": DOC["pa_intl"],
        "worksFor": {"@type": "Hospital", "name": "Continental Hospital", "address": {"@type": "PostalAddress", "streetAddress": "Plot 15, Road 71, Gulshan 2", "addressLocality": "Dhaka", "postalCode": "1212", "addressCountry": "BD"}},
        "address": {"@type": "PostalAddress", "streetAddress": "House 16, Road 2, Dhanmondi R/A", "addressLocality": "Dhaka", "postalCode": "1205", "addressCountry": "BD"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Monday", "Wednesday"], "opens": "22:00", "closes": "23:59"}],
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Dhaka Medical College"}, {"@type": "CollegeOrUniversity", "name": "Bangabandhu Sheikh Mujib Medical University"}],
        "sameAs": [DOC["fb"], DOC["yt"], DOC["li"]],
    }
def breadcrumb_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + "/" + (u if u != "index.html" else "")} for i, (n, u) in enumerate(items)]}
def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}} for q, a, _ in faqs]}
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

# ------------------------------------------------------------------ layout
NAV = [("home", "Home", "index.html"), ("services", "Services", "services.html"), ("about", "About", "about.html"),
       ("gallery", "Gallery", "gallery.html"), ("appointment", "Chambers", "appointment.html"), ("faq", "FAQ", "faq.html"), ("blog", "Blog", "blog.html")]

# Share image per page (Facebook, WhatsApp, LinkedIn). Default: og-image.jpg, made by make_og_image().
OG_IMAGES = {}  # page file -> (image inside assets/img, width, height, alt)
OG_DEFAULT = ("og-image.jpg", 1200, 630, "Dr. Md. Isma Azam (Zico), neurosurgeon in Dhaka")

def head(title, desc, file, schema):
    canon = SITE_URL + "/" + ("" if file == "index.html" else file)
    og_file, og_w, og_h, og_alt = OG_IMAGES.get(file, OG_DEFAULT)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="en_BD">
<meta property="og:locale:alternate" content="bn_BD">
<meta name="theme-color" content="#0A3A63">
<meta property="og:image" content="{SITE_URL}/assets/img/{og_file}">
<meta property="og:image:width" content="{og_w}">
<meta property="og:image:height" content="{og_h}">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" href="assets/img/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="assets/fonts/spectral-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/public-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/public-sans-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/public-sans-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>/* fonts are served from this site (assets/fonts), no Google Fonts request */@font-face{{font-family:"Spectral";font-style:normal;font-weight:500;font-display:swap;src:url(assets/fonts/spectral-latin-500-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Spectral";font-style:normal;font-weight:600;font-display:swap;src:url(assets/fonts/spectral-latin-600-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Spectral";font-style:normal;font-weight:700;font-display:swap;src:url(assets/fonts/spectral-latin-700-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Public Sans";font-style:normal;font-weight:400;font-display:swap;src:url(assets/fonts/public-sans-latin-400-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Public Sans";font-style:normal;font-weight:500;font-display:swap;src:url(assets/fonts/public-sans-latin-500-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Public Sans";font-style:normal;font-weight:600;font-display:swap;src:url(assets/fonts/public-sans-latin-600-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Public Sans";font-style:normal;font-weight:700;font-display:swap;src:url(assets/fonts/public-sans-latin-700-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}@font-face{{font-family:"Hind Siliguri";font-style:normal;font-weight:400;font-display:swap;src:url(assets/fonts/hind-siliguri-bengali-400-normal.woff2) format("woff2");unicode-range:U+0951-0952, U+0964-0965, U+0980-09FE, U+1CD0, U+1CD2, U+1CD5-1CD6, U+1CD8, U+1CE1, U+1CEA, U+1CED, U+1CF2, U+1CF5-1CF7, U+200C-200D, U+20B9, U+25CC, U+A8F1}}@font-face{{font-family:"Hind Siliguri";font-style:normal;font-weight:500;font-display:swap;src:url(assets/fonts/hind-siliguri-bengali-500-normal.woff2) format("woff2");unicode-range:U+0951-0952, U+0964-0965, U+0980-09FE, U+1CD0, U+1CD2, U+1CD5-1CD6, U+1CD8, U+1CE1, U+1CEA, U+1CED, U+1CF2, U+1CF5-1CF7, U+200C-200D, U+20B9, U+25CC, U+A8F1}}@font-face{{font-family:"Hind Siliguri";font-style:normal;font-weight:600;font-display:swap;src:url(assets/fonts/hind-siliguri-bengali-600-normal.woff2) format("woff2");unicode-range:U+0951-0952, U+0964-0965, U+0980-09FE, U+1CD0, U+1CD2, U+1CD5-1CD6, U+1CD8, U+1CE1, U+1CEA, U+1CED, U+1CF2, U+1CF5-1CF7, U+200C-200D, U+20B9, U+25CC, U+A8F1}}@font-face{{font-family:"IBM Plex Mono";font-style:normal;font-weight:500;font-display:swap;src:url(assets/fonts/ibm-plex-mono-latin-500-normal.woff2) format("woff2");unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}}</style>
<link rel="stylesheet" href="assets/css/style.css">
<script>/* image fallback: real file -> sample photo -> labelled placeholder */function dzImg(i){{if(i.dataset.sample&&!i.dataset.tried){{i.dataset.tried="1";if(i.dataset.kind!=="real")i.parentNode.classList.add("is-sample");i.src=i.dataset.sample;}}else{{i.parentNode.classList.remove("is-sample");i.remove();}}}}</script>
{''.join(ld(s) for s in schema)}
</head>"""

def header(active):
    menu_items = "".join(
        f'<a href="{s["slug"]}.html"><span class="ic">{icon(s["icon"])}</span><span><strong>{esc(s["name"])}</strong><span lang="bn">{esc(s["bn_name"])}</span></span></a>'
        for s in SERVICES)
    links = []
    for key, label, href in NAV:
        if key == "faq":
            continue  # FAQ lives in the drawer and footer to keep the desktop bar short
        cur = ' aria-current="page"' if key == active else ""
        if key == "services":
            act = " is-active" if active in ("services", "service") else ""
            links.append(f'<li class="has-menu{act}"><button class="nav-trigger" type="button" aria-expanded="false" aria-controls="svc-menu">Services <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>'
                         f'<div class="menu" id="svc-menu" hidden>{menu_items}<a class="menu-all" href="services.html">All services and conditions</a></div></li>')
        else:
            links.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    drawer_sub = "".join(f'<li><a href="{s["slug"]}.html">{esc(s["name"])}</a></li>' for s in SERVICES)
    drawer_links = "".join(
        (f'<li><a href="{h}"{AC if k == active else ""}>{l}</a></li>' if k != "services"
         else f'<li><a href="services.html"{AC if active == "services" else ""}>Services</a></li><li><ul class="drawer-sub">{drawer_sub}</ul></li>')
        for k, l, h in NAV)
    return f"""<body class="draft">
<a class="skip" href="#main">Skip to main content</a>
<div class="draft-bar" role="region" aria-label="Draft notice"><div class="wrap"><span><strong>Draft {VERSION}.</strong> Items highlighted in yellow still need Dr. Zico's confirmation. Hover or focus one to see what to check.</span><button type="button" data-draft-toggle>Hide highlights</button></div></div>
<div class="topbar"><div class="wrap"><span>Appointment (personal assistant): <a class="pa" href="tel:{DOC['pa_intl']}">{DOC['pa']}</a> · Popular Dhanmondi serial: <a href="tel:{DOC['phone_popular_intl']}">{DOC['phone_popular']}</a> · Continental hotline: <a href="tel:{DOC['continental_hotline']}">{DOC['continental_hotline']}</a></span><span class="emerg">{icon('alert')} Emergency? Go to the nearest hospital emergency department.</span></div></div>
<header class="site-header"><div class="wrap">
 <a class="brand" href="index.html" aria-label="Dr. Zico, neurosurgeon, home"><img class="brand-logo" {img_attrs("logo.png", "200px", 480)} alt="Dr. Zico logo" width="793" height="219"><span class="vh">Dr. Md. Isma Azam (Zico), Neurosurgeon, Brain &amp; Spine</span></a>
 <nav class="nav" aria-label="Main"><ul>{''.join(links)}</ul></nav>
 <div class="header-tools">
  <a class="header-phone" href="tel:{DOC['pa_intl']}"><span>Appointment</span><b>{DOC['pa']}</b></a>
  <button class="icon-btn" type="button" data-theme-toggle aria-label="Switch colour theme">{icon('moon', 'i-moon')}{icon('sun', 'i-sun')}</button>
  <a class="btn btn-primary header-cta" href="appointment.html#book">{icon('calendar')} Book appointment</a>
  <button class="menu-toggle" type="button" data-drawer-open aria-controls="drawer" aria-expanded="false" aria-label="Open menu">{icon('menu')}</button>
 </div>
</div></header>
<div class="drawer" id="drawer" hidden><div class="drawer-panel" role="dialog" aria-modal="true" aria-label="Menu">
 <div class="drawer-head"><span class="brand-name">Dr. Zico</span><button class="menu-toggle" type="button" data-drawer-close aria-label="Close menu">{icon('close')}</button></div>
 <nav aria-label="Mobile"><ul>{drawer_links}</ul></nav>
 <a class="btn btn-primary" href="appointment.html#book">{icon('calendar')} Book appointment</a>
 <a class="btn btn-ghost" href="tel:{DOC['pa_intl']}">{icon('phone')} Call {DOC['pa']}</a>
 <p class="small muted">Popular Dhanmondi serial: <a href="tel:{DOC['phone_popular_intl']}">{DOC['phone_popular']}</a><br>Continental hotline: <a href="tel:{DOC['continental_hotline']}">{DOC['continental_hotline']}</a></p>
</div></div>
<main id="main" tabindex="-1">"""

def contact_widget():
    hospitals = [
        ("continental", "Continental Hospital, Gulshan 2", "chamber-continental.jpg", DOC["continental_hotline"], DOC["continental_hotline"], "Hospital hotline"),
        ("popular", "Popular Diagnostic Centre, Dhanmondi", "chamber-popular-dhanmondi.jpg", DOC["phone_popular_intl"], DOC["phone_popular"], "Serial and appointment"),
        ("malibag", "Dr. Sirajul Islam Medical College & Hospital, Malibag", "chamber-malibag.jpg", "+8801927333000", DOC["phone_malibag"], "Appointment; call to confirm hours"),
    ]
    rows = "".join(
        f'<article class="contact-hospital"><img {img_attrs(image, "(max-width: 760px) 90vw, 360px")} alt="{esc(name)}" width="1200" height="675" loading="lazy" decoding="async">'
        f'<div class="contact-hospital-info"><h3>{esc(name)}</h3><p class="small muted">{esc(note)}</p>'
        f'<div class="contact-actions"><a class="btn btn-primary" href="tel:{phone}">{icon("phone")} {esc(display)}</a>'
        f'<a class="btn btn-ghost" href="appointment.html?chamber={key}#book">{icon("calendar")} Appointment</a></div></div></article>'
        for key, name, image, phone, display, note in hospitals)
    return f"""<button class="floating-call" type="button" data-contact-open aria-haspopup="dialog" aria-controls="contact-modal" aria-label="Call / Book: call a hospital or book an appointment">{icon('phone')}<span>Call / Book</span></button>
<dialog class="contact-modal" id="contact-modal" aria-labelledby="contact-title" aria-describedby="contact-intro">
 <div class="contact-heading"><div><span class="eyebrow">Appointments</span><h2 id="contact-title">Call or book a visit</h2></div><button class="icon-btn" type="button" data-contact-close aria-label="Close appointment options" autofocus>{icon('close')}</button></div>
 <p class="muted" id="contact-intro">Choose your hospital to call or request an appointment.</p>
 <p class="small bn" lang="bn">হাসপাতালে সরাসরি কল করুন অথবা অ্যাপয়েন্টমেন্টের ফর্ম পূরণ করুন।</p>
 <div class="contact-hospitals">{rows}</div>
 <div class="contact-assistant"><span class="small muted">Need help choosing a chamber?</span><a href="tel:{DOC['pa_intl']}">{icon('phone')} Personal assistant: {DOC['pa']}</a></div>
</dialog>"""


def footer():
    svc = "".join(f'<li><a href="{s["slug"]}.html">{esc(s["name"])}</a></li>' for s in SERVICES)
    return f"""</main>
<footer class="site-footer"><div class="wrap">
 <div class="footer-grid">
  <div class="stack-sm"><a class="brand" href="index.html"><img class="brand-logo" {img_attrs("logo.png", "200px", 480)} alt="Dr. Zico logo" width="793" height="219" loading="lazy"><span class="vh">Dr. Md. Isma Azam (Zico), Neurosurgeon in Dhaka</span></a>
   <p class="muted small">{DOC['degrees']}</p>
   <p class="small"><a href="{DOC['fb']}" rel="noopener" target="_blank">Facebook</a> · <a href="{DOC['yt']}" rel="noopener" target="_blank">YouTube</a> · <a href="{DOC['li']}" rel="noopener" target="_blank">LinkedIn</a></p></div>
  <div><h2>Services</h2><ul>{svc}</ul></div>
  <div><h2>Chambers</h2><ul>
   <li><strong>Continental Hospital, Gulshan 2</strong><br><span class="muted">Plot 15, Road 71, Gulshan 2, Dhaka 1212</span><br><span class="muted">Sat to Thu · 8:30 AM to 4:00 PM</span><br><a class="num" href="tel:{DOC['continental_hotline']}">Hotline {DOC['continental_hotline']}</a></li>
   <li><strong>Popular Diagnostic Centre, Dhanmondi</strong><br><span class="muted">House 16, Road 2, Dhanmondi R/A, Dhaka 1205</span><br><span class="muted">Sat, Mon, Wed · 10:00 PM to 12:00 AM</span><br><a class="num" href="tel:{DOC['phone_popular_intl']}">{DOC['phone_popular']}</a></li>
   <li><strong>Dr. Sirajul Islam Medical College &amp; Hospital, Malibag</strong><br><span class="muted">12/3 New Circular Road, Malibag, Dhaka</span><br><span class="muted">{v('Hours: call to confirm', 'Two different schedules are published. Confirm the current Malibag days and time.')}</span><br><a class="num" href="tel:+8801927333000">{DOC['phone_malibag']}</a></li>
  </ul></div>
  <div><h2>Patients</h2><ul><li><a href="appointment.html#book">Book appointment</a></li><li><a href="services.html#finder">Find your condition</a></li><li><a href="gallery.html">Patient gallery</a></li><li><a href="faq.html">Questions and answers</a></li><li><a href="blog.html">Health articles (Bangla)</a></li><li><a href="about.html#case-log">Surgical case log</a></li></ul></div>
 </div>
 <p class="notice" style="margin-top:32px">Information on this website is for general education and does not replace a consultation. Every patient is different; decisions about surgery are made after examination and review of scans. In an emergency, go to the nearest hospital emergency department.</p>
 <div class="footer-base"><span>© <span data-year>2026</span> Dr. Md. Isma Azam (Zico).</span><span>Appointment: <a class="num" href="tel:{DOC['pa_intl']}">{DOC['pa']}</a></span></div>
</div></footer>
<div class="mobile-cta" aria-label="Quick actions"><button class="btn btn-ghost" type="button" data-contact-open aria-haspopup="dialog" aria-controls="contact-modal">{icon('phone')} Call</button><a class="btn btn-primary" href="appointment.html#book">{icon('calendar')} Book</a></div>
{contact_widget()}
<button class="to-top" type="button" aria-label="Back to top">{icon('up')}</button>
<script src="assets/js/conditions.js" defer></script>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""

def layout(file, title, desc, active, body, schema):
    return head(title, desc, file, [physician_schema()] + schema) + "\n" + header(active) + "\n" + body + "\n" + footer()

def crumbs(items):
    lis = "".join((f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{esc(n)}</li>') for i, (n, u) in enumerate(items))
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'

def faq_block(faqs, fid="faq", heading="Questions patients ask", show_filter=False):
    items = "".join(f'<details><summary{LBN if lang == "bn" else ""}>{esc(q)}</summary><div class="ans">{a}</div></details>' for q, a, lang in faqs)
    filt = (f'<div class="faq-tools"><label class="sr-only" for="faq-q">Search questions</label><input id="faq-q" type="search" placeholder="Search questions, e.g. serial, PLID, খরচ" data-faq-filter="{fid}-list" aria-describedby="faq-count"><span id="faq-count" class="small muted" aria-live="polite"></span></div>' if show_filter else "")
    return f'<section class="block" id="{fid}"><div class="block-head"><div><h2>{heading}</h2><span class="bn-sub" lang="bn">সাধারণ প্রশ্ন ও উত্তর</span></div></div>{filt}<div class="faq" id="{fid}-list">{items}</div></section>'

def cta_band(concern=None):
    href = "appointment.html" + (f"?concern={concern}" if concern else "") + "#book"
    return f"""<div class="cta-band"><div><h2>Talk to Dr. Zico about your scans</h2><p>Bring your MRI or CT films and reports. He will explain what they show and whether you need surgery.</p><p lang="bn">অ্যাপয়েন্টমেন্টের জন্য কল করুন: {DOC['pa']}</p></div>
<div class="btn-row"><a class="btn btn-primary" href="{href}">{icon('calendar')} Book appointment</a><a class="btn btn-ghost" href="tel:{DOC['pa_intl']}">{icon('phone')} {DOC['pa']}</a></div></div>"""

def svc_card(s):
    return f"""<a class="svc-card" href="{s['slug']}.html"><div class="top"><span class="ic">{icon(s['icon'])}</span><span class="n">n = {fmt(total(s))}</span></div>
<h3>{esc(s['name'])}</h3><span class="bn" lang="bn">{esc(s['bn_name'])}</span><p>{esc(s['short'])}</p><span class="more">Learn more {icon('arrow')}</span></a>"""

def chamber_cards(page):
    return f"""<div class="grid-3c">
<article class="chamber">{local_photo('chamber-continental.jpg', 1200, 675, 'Continental Hospital building', 'Continental Hospital, Gulshan 2, Dhaka', page, 'ph--sm', eager=(page == 'Appointment'))}<span class="status" data-chamber-status="continental">Sat to Thu</span><h3>Continental Hospital, Gulshan 2</h3>
<dl><dt>Address</dt><dd>Plot 15, Road 71, Gulshan 2, Dhaka 1212</dd><dt>Days</dt><dd>Saturday to Thursday</dd><dt>Time</dt><dd>8:30 AM to 4:00 PM</dd><dt>Role</dt><dd>Associate Consultant, Neuro Surgery</dd></dl>
<div><span class="small muted">Hospital hotline</span><br><a class="phone" href="tel:{DOC['continental_hotline']}">{DOC['continental_hotline']}</a></div>
<div class="btn-row"><a class="btn btn-brand" href="appointment.html?chamber=continental#book">{icon('calendar')} Request appointment</a><a class="btn btn-ghost" href="https://www.google.com/maps/search/?api=1&amp;query=Continental+Hospital+Gulshan+2+Dhaka" target="_blank" rel="noopener">{icon('pin')} Map</a></div></article>
<article class="chamber">{local_photo('chamber-popular-dhanmondi.jpg', 1200, 675, 'Popular Diagnostic, Dhanmondi', 'Popular Diagnostic Centre building in Dhanmondi, Dhaka', page, 'ph--sm', eager=(page == 'Appointment'))}<span class="status" data-chamber-status="popular">Sat, Mon, Wed</span><h3>Popular Diagnostic Centre, Dhanmondi</h3>
<dl><dt>Address</dt><dd>House 16, Road 2, Dhanmondi R/A, Dhaka 1205</dd><dt>Days</dt><dd>Saturday, Monday, Wednesday</dd><dt>Time</dt><dd>10:00 PM to 12:00 AM</dd></dl>
<div><span class="small muted">Serial (appointment)</span><br><a class="phone" href="tel:{DOC['phone_popular_intl']}">{DOC['phone_popular']}</a></div>
<div class="btn-row"><a class="btn btn-brand" href="appointment.html?chamber=popular#book">{icon('calendar')} Request serial</a><a class="btn btn-ghost" href="https://www.google.com/maps/search/?api=1&amp;query=Popular+Diagnostic+Centre+Dhanmondi+Dhaka" target="_blank" rel="noopener">{icon('pin')} Map</a></div></article>
<article class="chamber">{local_photo('chamber-malibag.jpg', 1200, 675, 'Dr. Sirajul Islam MCH, Malibag', 'Dr. Sirajul Islam Medical College and Hospital building in Malibag, Dhaka', page, 'ph--sm', eager=(page == 'Appointment'))}<span class="status" data-chamber-status="malibag">Call to confirm hours</span><h3>Dr. Sirajul Islam Medical College &amp; Hospital, Malibag</h3>
<dl><dt>Address</dt><dd>12/3 New Circular Road, Malibag (near Mouchak Market), Dhaka</dd><dt>Days</dt><dd>{v('Call to confirm', 'Published schedules differ: daily except Friday 8 to 10 PM, or Sat to Thu 6 to 8 PM.')}</dd></dl>
<div><span class="small muted">Appointment</span><br><a class="phone" href="tel:+8801927333000">{DOC['phone_malibag']}</a> · <a class="phone" href="tel:+8801830279952">{DOC['phone_malibag2']}</a></div>
<div class="btn-row"><a class="btn btn-brand" href="appointment.html?chamber=malibag#book">{icon('calendar')} Request serial</a><a class="btn btn-ghost" href="https://www.google.com/maps/search/?api=1&amp;query=Dr.+Sirajul+Islam+Medical+College+Hospital+Malibag" target="_blank" rel="noopener">{icon('pin')} Map</a></div></article>
</div>"""

BRING = """<ul><li>All MRI and CT films and their reports, oldest to newest</li><li>Previous prescriptions and discharge papers</li><li>A list of the medicines you take, including blood thinners</li><li>Blood test reports (sugar, creatinine) if you have them</li><li>A family member who knows your history</li></ul>"""

# ------------------------------------------------------------------ general FAQ
GENERAL_FAQ = [
    ("What does a neurosurgeon treat?", "<p>A neurosurgeon operates on the brain, spine and nerves: slipped discs, neck and spinal cord problems, brain and spinal tumors, aneurysms, hydrocephalus, head and spine injuries, and nerve pain such as trigeminal neuralgia. Many patients seen by a neurosurgeon do not need an operation.</p>", "en"),
    ("Neurologist or neurosurgeon: whom should I see first?", "<p>A neurologist treats nervous system diseases with medicines (for example epilepsy, migraine, stroke, Parkinson's). A neurosurgeon treats conditions that may need an operation. If an MRI shows a disc prolapse, a tumor, fluid on the brain or a spine injury, seeing a neurosurgeon is appropriate. <a href=\"blog-komor-byatha-kon-doctor.html\">Read our Bangla guide</a>.</p>", "en"),
    ("How do I get a serial for Dr. Zico at Popular Diagnostic Dhanmondi?", f"<p>Call {DOC['phone_popular']} and ask for a serial for Dr. Md. Isma Azam (Zico), Neurosurgery. The Dhanmondi chamber runs on Saturday, Monday and Wednesday from 10:00 PM to 12:00 AM. For Continental Hospital, Gulshan (Saturday to Thursday, 8:30 AM to 4:00 PM), call the hotline 10666. You can also call his personal assistant on {DOC['pa']}, or <a href=\"appointment.html#book\">send an appointment request</a> and the team will call you.</p>", "en"),
    ("What should I bring to the consultation?", f"<div>{BRING}</div>", "en"),
    ("How do I choose the best neurosurgeon in Dhaka for my problem?", "<p>Ask how many operations the surgeon has done for your exact condition, which hospital and equipment will be used, who will look after you after surgery, and whether all options, including not operating, have been explained. Dr. Zico publishes his own case log so patients can see his experience.</p>", "en"),
    ("Is every spine problem treated with surgery?", "<p>No. Most back and neck pain improves with medicines, physiotherapy and time. Surgery is advised for nerve or spinal cord compression that causes weakness, severe pain that does not settle, instability, tumors or infection.</p>", "en"),
    ("When is a brain or spine problem an emergency?", "<p>Go to an emergency department for a sudden severe headache, loss of consciousness, a first seizure, sudden weakness or loss of speech, loss of bladder or bowel control with back pain, or weakness after a fall or accident.</p>", "en"),
    ("নিউরো সার্জন কোন কোন রোগের চিকিৎসা করেন?", "<p lang=\"bn\">নিউরোসার্জন মস্তিষ্ক, মেরুদণ্ড ও নার্ভের রোগের চিকিৎসা ও অপারেশন করেন, যেমন: কোমর ব্যথা ও PLID, ঘাড়ের ডিস্ক, ব্রেইন টিউমার, মাথায় পানি জমা, মস্তিষ্কে রক্তক্ষরণ, মাথায় ও মেরুদণ্ডে আঘাত এবং মুখে বিদ্যুতের মতো ব্যথা।</p>", "bn"),
    ("ডাঃ জিকোর সিরিয়াল কিভাবে নেবো?", f"<p lang=\"bn\">পপুলার ডায়াগনস্টিক সেন্টার, ধানমন্ডিতে সিরিয়ালের জন্য কল করুন {DOC['phone_popular']} নম্বরে। চেম্বার শনি, সোম ও বুধবার রাত ১০টা থেকে ১২টা। কন্টিনেন্টাল হাসপাতাল, গুলশান ২-এ (শনি থেকে বৃহস্পতি, সকাল ৮:৩০ থেকে বিকাল ৪টা) হটলাইন ১০৬৬৬। মালিবাগে ডাঃ সিরাজুল ইসলাম মেডিকেল কলেজ হাসপাতালের জন্য কল করুন {DOC['phone_malibag']}। ব্যক্তিগত সহকারী: {DOC['pa']}।</p>", "bn"),
    ("নিউরোসার্জন দেখাতে কী কী রিপোর্ট সাথে আনতে হবে?", "<p lang=\"bn\">সব MRI ও CT স্ক্যানের ফিল্ম ও রিপোর্ট, আগের প্রেসক্রিপশন, ডিসচার্জ পেপার এবং যে ওষুধ খাচ্ছেন তার তালিকা সাথে আনুন।</p>", "bn"),
]

# ------------------------------------------------------------------ before / after cases
# NEWEST FIRST: add a new case as the first line of this list so it shows first on Home and Gallery.
# Each case: (id, category, title, bangla title, service page, note). Images: assets/img/before-after/case-<id>-before.jpg / -after.jpg
CASES = [
    ("cpa-axial", "brain", "CP angle tumour (axial view)", "সিপি অ্যাঙ্গেল টিউমার", "brain-tumor-surgery.html#cp-angle", "Contrast MRI of the head before and after surgery. The large tumour at the cerebellopontine angle, beside the brainstem, is not seen after the operation."),
    ("cpa-hydro", "brain", "CP angle tumour with hydrocephalus", "সিপি অ্যাঙ্গেল টিউমার ও মাথায় পানি জমা", "brain-tumor-surgery.html#cp-angle", "Front-view MRI before and after surgery. Before: a CP angle tumour with enlarged fluid spaces in the brain. After: the tumour is removed and the fluid spaces are smaller."),
    ("suprasellar", "brain", "Large sellar and suprasellar tumour", "পিটুইটারি এলাকার বড় টিউমার", "brain-tumor-surgery.html#pituitary", "A large tumour in and above the pituitary area. MRI before surgery and CT scan after surgery."),
    ("pituitary-sag", "brain", "Pituitary macroadenoma (side view)", "পিটুইটারি ম্যাক্রোঅ্যাডেনোমা", "brain-tumor-surgery.html#pituitary", "Pituitary MRI (side view) before and after surgery. The tumour is not seen after the operation."),
    ("pituitary-cor", "brain", "Pituitary macroadenoma (front view)", "পিটুইটারি ম্যাক্রোঅ্যাডেনোমা", "brain-tumor-surgery.html#pituitary", "Pituitary MRI (front view) before and after surgery. The tumour between the two main arteries of the brain is not seen after the operation."),
    ("spine-fracture", "spine", "Spine fracture fixation", "মেরুদণ্ডের হাড় ভাঙার অপারেশন", "spine-surgery.html#spine-trauma", "Fracture where the upper and lower back meet. CT scan before surgery, and X-ray after the spine was fixed with screws and rods."),
    ("pituitary", "brain", "Pituitary tumour", "পিটুইটারি টিউমার", "brain-tumor-surgery.html#pituitary", "Head MRI before and after surgery. The tumour at the base of the brain is not seen after the operation."),
    ("cervical-tumor", "spine", "Cervical spine tumour", "ঘাড়ের মেরুদণ্ডের টিউমার", "spinal-tumor-surgery.html#spinal-cord-tumors", "Neck MRI before and after surgery. A large tumour before the operation and a much smaller one after."),
    ("bypass", "brain", "Brain bypass surgery", "ব্রেইন বাইপাস সার্জারি", "brain-aneurysm-stroke-surgery.html#bypass", "Brain blood-vessel scan before and after bypass surgery."),
    ("large-tumor", "brain", "Large brain tumour", "বড় ব্রেইন টিউমার", "brain-tumor-surgery.html", "Head scans before and after removal of a large brain tumour (MRI before, CT after)."),
    ("cerebellar", "brain", "Cerebellar tumour", "সেরিবেলামের টিউমার", "brain-tumor-surgery.html", "Brain MRI before and after surgery for a tumour at the back of the brain (cerebellum)."),
    ("meningioma", "brain", "Meningioma", "মেনিনজিওমা", "brain-tumor-surgery.html#meningioma", "MRI before and after removal of a large tumour on the surface of the brain."),
    ("deep-tumor", "brain", "Deep brain tumour", "মস্তিষ্কের গভীরের টিউমার", "brain-tumor-surgery.html", "Brain MRI before and after surgery. The deep tumour seen before is not seen after."),
    ("cpa", "brain", "Cerebellopontine angle tumour", "সিপি অ্যাঙ্গেল টিউমার", "brain-tumor-surgery.html#cp-angle", "Brain MRI before and after surgery for a tumour at the back of the brain, near the brainstem."),
    ("skullbase", "brain", "Skull base tumour", "খুলির তলদেশের টিউমার", "brain-tumor-surgery.html#skull-base", "MRI before and after surgery for a tumour at the base of the skull."),
]
CAT_LABEL = {"spine": "Spine", "brain": "Brain", "children": "Children"}

def ba_card(c, page):
    cid, cat, title, bn, url, note = c
    sp = "spine" if cat == "spine" else "brain"
    before = ph(f"{BA_DIR}/case-{cid}-before.jpg", 1200, 900, "Before: " + title, note + " (before)", "Before surgery: " + title, "Gallery", "ph--fill ph--sm")
    after = ph(f"{BA_DIR}/case-{cid}-after.jpg", 1200, 900, "After: " + title, note + " (after)", "After surgery: " + title, "Gallery", "ph--fill ph--sm")
    return f"""<article class="ba-card" data-cat="{cat}">
 <div class="ba" style="--pos:50%"><div class="ba-layer ba-after">{after}</div><div class="ba-layer ba-before">{before}</div>
  <span class="ba-tag ba-tag--b">Before</span><span class="ba-tag ba-tag--a">After</span><span class="ba-handle" aria-hidden="true"></span>
  <input class="ba-range" type="range" min="0" max="100" value="50" aria-label="Compare before and after: {esc(title)}"></div>
 <div class="ba-body"><span class="tag">{CAT_LABEL[cat]}</span><h3>{esc(title)}</h3><span class="bn small" lang="bn">{esc(bn)}</span>
 <p class="small muted">{v(esc(note), 'Dr. Zico to confirm the diagnosis and the result for this case before the site goes live.')}</p>
 <a class="small" href="{url}">About this treatment</a></div>
</article>"""

def ba_carousel(cases, page):
    cards = "".join(ba_card(c, page) for c in cases)
    return f"""<div class="carousel carousel--ba" data-carousel data-autoplay="4500">
 <div class="car-track" tabindex="0" aria-label="Before and after cases, scroll sideways">{cards}</div>
 <div class="car-nav"><button class="icon-btn" type="button" data-car-prev aria-label="Previous case">{icon('arrow', 'flip')}</button><button class="icon-btn" type="button" data-car-next aria-label="Next case">{icon('arrow')}</button></div>
</div>"""

# YouTube videos (checked 28 Sep 2026). To add one: append (video ID, title, source). Order = carousel order.
VIDEOS = [
    ("5FYfW_5LRYA", "What is PLID?", "Neurosurgeon Dr. Zico"),
    ("cuQPs4OXC9g", "PLID অপারেশনের পরে প্যারালাইসিস হবে না", "Neurosurgeon Dr. Zico"),
    ("GFPPSTFczhk", "Brain tumor", "Continental Hospital PLC"),
    ("I7vxjL0vqmc", "Dr. Md. Isma Azam Zico", "Continental Hospital PLC"),
]
def video_card(i, vid, title, src, page):
    f = f"video-{i}-thumb.jpg"
    REAL_REMOTE[f] = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    lang = ' lang="bn"' if any('\u0980' <= ch <= '\u09ff' for ch in title) else ''
    return (f'<a class="video-card" href="https://www.youtube.com/watch?v={vid}" data-video="{vid}" data-title="{esc(title)}" target="_blank" rel="noopener">'
            f'<div class="vc-thumb">{ph(f, 1280, 720, f"Video {i} thumbnail", "Optional: your own thumbnail. If missing, the YouTube thumbnail is used", "Video: " + title, page, "ph--sm")}'
            f'<span class="play">{icon("play")}</span></div><strong{lang}>{esc(title)}</strong><span class="small muted">{esc(src)} · YouTube</span></a>')
def video_carousel(page):
    cards = "".join(video_card(i, *v_, page) for i, v_ in enumerate(VIDEOS, 1))
    return f"""<div class="carousel carousel--videos" data-carousel data-autoplay="5000">
 <div class="car-track" tabindex="0" aria-label="Videos, scroll sideways">{cards}</div>
 <div class="car-nav"><button class="icon-btn" type="button" data-car-prev aria-label="Previous video">{icon('arrow', 'flip')}</button><button class="icon-btn" type="button" data-car-next aria-label="Next video">{icon('arrow')}</button></div>
</div>
<dialog class="video-modal" id="video-modal" aria-label="Video player"><div class="vm-box"><button class="icon-btn vm-close" type="button" data-vm-close aria-label="Close video">{icon('close')}</button><div class="vm-frame"></div><p class="vm-title"></p></div></dialog>"""

# Facebook feed: paste the Cloudflare Worker address here (see FB-FEED-SETUP.md). Empty = section hidden on the live site.
FB_FEED_URL = ""

# ---- Real patient photo carousels at the end of a service page ----
# To add one for another service: save the photos as assets/img/services/<slug>/<slug>-case-01.jpg, -02.jpg ... then add an entry here.
SERVICE_GALLERIES = {
    "plid-lumbar-disc-surgery": dict(count=18, h2="PLID surgery: small incision photos", bn="PLID অপারেশনের ছোট ক্ষতের ছবি",
        intro="Photos of the small incision after PLID surgery, taken at different stages of healing.", alt="PLID incision photo"),
    # Spine surgery photos come from SERVICE_CASES below (one list feeds both the case blocks and this carousel).
    "spine-surgery": dict(h2="Spine surgery: scans and photos from Dr. Zico's cases", bn="মেরুদণ্ডের অপারেশনের স্ক্যান ও ছবি",
        intro="X-rays, MRI and CT scans, and photos from four of Dr. Zico's neck (cervical) spine cases. No patient names are shown.",
        photos="cases"),
}
SEC_ALT = {("plid-lumbar-disc-surgery", "what-is-plid"): "View inside the operation site during PLID surgery by Dr. Zico",
           ("spine-surgery", "cervical"): "Neck X-ray after cervical disc surgery by Dr. Zico, showing the plate, screws and spacers",
           ("spine-surgery", "spine-trauma"): "Neck X-ray after AAD surgery by Dr. Zico, showing the screws at the top of the neck"}

# Pages that show only real photos: an image slot without a real file is left out (no sample photo).
# hero.jpg and <section>.jpg in the service folder are crops made from the case photos.
REAL_ONLY_SERVICES = {"spine-surgery"}
LAST_REVIEWED = "2026-10-31"  # change when a page's medical content is updated

# Procedures named in Dr. Zico's shared cases (schema.org MedicalProcedure, helps Google and AI answers)
CASE_PROCEDURES = {
    "spine-surgery": [
        {"@type": "MedicalProcedure", "name": "Anterior cervical discectomy and fusion (ACDF)", "procedureType": "https://schema.org/SurgicalProcedure", "bodyLocation": "Cervical spine (neck)"},
        {"@type": "MedicalProcedure", "name": "Single-level ACDF", "procedureType": "https://schema.org/SurgicalProcedure", "bodyLocation": "Cervical spine (neck)"},
        {"@type": "MedicalProcedure", "name": "Atlanto-axial (C1-C2) fixation for atlanto-axial dislocation (AAD)", "procedureType": "https://schema.org/SurgicalProcedure", "bodyLocation": "Craniovertebral junction"},
    ],
}

def page_images_schema(s):
    """image / primaryImageOfPage / mentions for a service page that has real photos."""
    slug = s["slug"]
    if slug not in REAL_ONLY_SERVICES: return {}
    hero = svc_img(slug, "hero.jpg")
    photos = [{"@type": "ImageObject", "contentUrl": f"{SITE_URL}/assets/img/{largest(svc_img(slug, f))}", "caption": f"{grp}: {what}"}
              for f, w, h, grp, what in case_photos(slug)]
    out = {"primaryImageOfPage": {"@type": "ImageObject", "contentUrl": f"{SITE_URL}/assets/img/{hero}", "caption": HERO_ALT[slug]},
           "image": [f"{SITE_URL}/assets/img/{hero}"] + [p["contentUrl"] for p in photos]}
    if slug in CASE_PROCEDURES: out["mentions"] = CASE_PROCEDURES[slug]
    return out
HERO_ALT = {"spine-surgery": "Neck X-ray after cervical spine surgery by Dr. Zico, showing the plate and screws"}

# Real cases shown inside a section of a service page. Names in "title" are Dr. Zico's own labels.
# photos: (file name inside the service folder, width, height, what the image shows)
SERVICE_CASES = {
    "spine-surgery": [
        dict(section="cervical", title="Cervical spine surgery", bn="ঘাড়ের মেরুদণ্ডের অপারেশন", cover=("cervical-01.jpg", "40% 66%"),
             text="Surgery from the front of the neck, with the spine held in line by a plate and screws.",
             photos=[("cervical-01.jpg", 1200, 1600, "X-ray of the neck with plate and screws"),
                     ("cervical-02.jpg", 1200, 1600, "MRI of the neck"),
                     ("cervical-03.jpg", 1200, 1600, "Neck incision after surgery")]),
        dict(section="cervical", title="Cervical disc surgery", bn="ঘাড়ের ডিস্কের অপারেশন", cover=("cervical-disc-03.jpg", "50% 40%"),
             text="ACDF: the damaged discs are removed from the front of the neck and replaced with spacers (cages), held with a plate and screws.",
             photos=[("cervical-disc-01.jpg", 1374, 1600, "X-ray of the neck with plate, screws and spacers"),
                     ("cervical-disc-02.jpg", 1200, 1600, "MRI of the neck"),
                     ("cervical-disc-03.jpg", 1536, 1209, "Healed neck scar")]),
        dict(section="cervical", title="Cervical disc surgery, single level", bn="ঘাড়ের ডিস্কের অপারেশন, একটি লেভেল", cover=("cervical-disc-single-level-01.jpg", "60% 45%"),
             text="ACDF at one disc level only: one disc is removed and replaced with a spacer, held with a small plate.",
             photos=[("cervical-disc-single-level-01.jpg", 1600, 1200, "X-ray taken during the operation"),
                     ("cervical-disc-single-level-02.jpg", 1600, 1200, "Photo taken during the operation"),
                     ("cervical-disc-single-level-03.jpg", 1200, 1600, "MRI of the neck")]),
        dict(section="spine-trauma", title="AAD (atlanto-axial dislocation)", bn="এএডি (অ্যাটলান্টো-অ্যাক্সিয়াল ডিসলোকেশন)", cover=("aad-02.jpg", "50% 50%"),
             text="In AAD the first two bones of the neck (C1 and C2) slip out of line and can press on the spinal cord at the top of the neck. Surgery brings them back into line and fixes them with screws.",
             photos=[("aad-01.jpg", 1200, 1600, "X-ray of the upper neck with screws"),
                     ("aad-02.jpg", 1600, 1571, "CT scan showing the screws"),
                     ("aad-03.jpg", 1353, 1600, "CT scan showing the screws"),
                     ("aad-04.jpg", 1344, 1600, "MRI of the upper neck")]),
    ],
}
def case_photos(slug):
    """All case photos of a service as (file, w, h, case title, what)."""
    return [(f, w, h, c["title"], what) for c in SERVICE_CASES.get(slug, []) for f, w, h, what in c["photos"]]

def case_key(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

def case_blocks(slug, section_id):
    """Dr. Zico's own cases for one section, as short text cards. Photos stay in the carousel at the end
    of the page; each card links to its first photo there."""
    cards = []
    for c in SERVICE_CASES.get(slug, []):
        if c["section"] != section_id: continue
        n = len(c["photos"])
        key = case_key(c["title"])
        cf, pos = c["cover"]
        _, cw, ch, cwhat = next(x for x in c["photos"] if x[0] == cf)
        img = (f'<a class="case-img" href="#photos" data-goto-case="{key}" aria-label="See the {n} photos from this case: {esc(c["title"])}">'
               f'<img {img_attrs(svc_img(slug, cf), "(max-width: 560px) 92vw, 300px")} alt="{esc(c["title"])} by Dr. Zico: {esc(cwhat)}" '
               f'width="{cw}" height="{ch}" style="object-position:{pos}" loading="lazy" decoding="async"><span class="case-count">{icon("image")} {n} photos</span></a>')
        cards.append(f'<article class="case-card">{img}<div class="case-body"><h3>{esc(c["title"])}</h3><span class="bn small" lang="bn">{c["bn"]}</span>'
                     f'<p class="small">{esc(c["text"])}</p>'
                     f'<a class="case-link small" href="#photos" data-goto-case="{key}">{icon("image")} See the {n} photos from this case</a></div></article>')
    if not cards: return ""
    return f'<div class="case-cards"><h3 class="case-cards-title">Cases Dr. Zico has shared</h3><div class="case-grid">{"".join(cards)}</div></div>'

def service_gallery(s):
    g = SERVICE_GALLERIES.get(s["slug"])
    if not g: return ""
    if "photos" in g:  # named photos with a case label, shown whole (scans must not be cropped)
        photos = case_photos(s["slug"]) if g["photos"] == "cases" else g["photos"]
        n = len(photos)
        for f, *_ in photos:
            assert os.path.isfile(os.path.join(ROOT, "assets", "img", svc_img(s["slug"], f))), f
        cards = "".join(
            f'<button class="car-photo car-photo--whole" type="button" data-lightbox data-case="{case_key(grp)}" aria-label="Open photo {i} of {n}: {esc(grp)}">'
            f'<img {img_attrs(svc_img(s["slug"], f), SZ_CARD)} alt="{esc(grp)} by Dr. Zico: {esc(what)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<span class="car-cap">{esc(grp)}</span></button>'
            for i, (f, w, h, grp, what) in enumerate(photos, 1))
    else:
        cards = "".join(
            f'<button class="car-photo" type="button" data-lightbox aria-label="Open photo {i} of {g["count"]}">'
            f'<img {img_attrs(svc_img(s["slug"], f"case-{i:02d}.jpg"), SZ_CARD)} alt="{esc(g["alt"])} {i}" width="750" height="1000" loading="lazy" decoding="async"></button>'
            for i in range(1, g["count"] + 1))
    return (f'<section class="block" id="photos"><div class="block-head"><div><h2>{esc(g["h2"])}</h2><span class="bn-sub" lang="bn">{g["bn"]}</span></div></div>'
            f'<p class="muted">{esc(g["intro"])}</p>'
            f'<div class="carousel carousel--photos" data-carousel data-autoplay="3500">'
            f'<div class="car-track" tabindex="0" aria-label="Photos, scroll sideways">{cards}</div>'
            f'<div class="car-nav"><button class="icon-btn" type="button" data-car-prev aria-label="Previous photo">{icon("arrow", "flip")}</button><button class="icon-btn" type="button" data-car-next aria-label="Next photo">{icon("arrow")}</button></div></div>'
            f'<dialog class="lightbox" id="lightbox" aria-label="Photo viewer"><button class="icon-btn lb-close" type="button" data-lb-close aria-label="Close">{icon("close")}</button><img alt=""><p class="lb-cap"></p></dialog></section>')

def happy_patient_carousel():
    """Shared real patient photos for Home and Gallery; order lives in the JSON file."""
    cards = []
    for i, photo in enumerate(HAPPY_PATIENTS, 1):
        file, w, h, alt = photo["file"], photo["width"], photo["height"], photo["alt"]
        if not any(row[1] == file for row in IMAGES):
            IMAGES.append(("Home / Gallery", file, f"{w}x{h}", f"Patient photo {i:02d}", alt))
        cards.append(
            f'<button class="car-photo" type="button" data-lightbox aria-label="Open patient photo {i} of {len(HAPPY_PATIENTS)}">'
            f'<img {img_attrs(file, SZ_CARD)} alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></button>')
    return (
        '<div class="carousel carousel--photos carousel--patients" data-carousel data-autoplay="3500" '
        'role="region" aria-roledescription="carousel" aria-label="Patient photos">'
        '<div class="car-track" tabindex="0" aria-label="Patient photos; swipe or use the left and right arrow keys">'
        + "".join(cards) + '</div>'
        '<div class="car-nav"><button class="icon-btn" type="button" data-car-prev aria-label="Previous patient photo">'
        + icon("arrow", "flip") + '</button><button class="icon-btn" type="button" data-car-next aria-label="Next patient photo">'
        + icon("arrow") + '</button></div></div>')


# ------------------------------------------------------------------ pages
def page_home():
    top = [("PLID (lumbar disc)", 1443, "plid-lumbar-disc-surgery.html"), ("ACDF (neck disc)", 459, "spine-surgery.html#cervical"),
           ("Pituitary macroadenoma", 329, "brain-tumor-surgery.html#pituitary"), ("Aneurysm clipping", 295, "brain-aneurysm-stroke-surgery.html#aneurysm"),
           ("Meningioma", 276, "brain-tumor-surgery.html#meningioma")]
    ledger = "".join(f'<li><a href="{u}">{n}</a><span class="dots"></span><span class="n">{fmt(c)}</span></li>' for n, c, u in top)
    cards = "".join(svc_card(s) for s in SERVICES)
    faqs = GENERAL_FAQ[:5] + GENERAL_FAQ[7:9]
    tech = [("scope", "Operating microscope", "Used for disc, neck, aneurysm and tumor surgery, including more than 450 microscopic ACDF operations."),
            ("brain", "Endoscopic surgery", "Pituitary tumors removed through the nose with no cut on the head, and ETV for hydrocephalus without a shunt."),
            ("spine", "Minimally invasive spine (MISS)", "Screws placed through small cuts for suitable spondylolisthesis patients (MISS TLIF)."),
            ("shield", "EXOSCOPE", v("High-definition 3D exoscope for fine microsurgery.", "Confirm which hospital(s) he uses the EXOSCOPE at.")),
            ("users", "A complete team", "Neurosurgery and anaesthesia consultants, specialists and trained OT nurses work on every case.")]
    techs = "".join(f'<div class="box"><span class="ic" style="width:40px;height:40px;border-radius:10px;background:var(--brand-soft);color:var(--brand);display:grid;place-items:center">{icon(i)}</span><h3>{t}</h3><p class="small muted">{d}</p></div>' for i, t, d in tech)
    body = f"""
<section class="hero hero--bleed"><div class="hero-grid">
 <div class="hero-text">
  <span class="eyebrow">Neurosurgeon in Dhaka · Brain and Spine Surgeon</span>
  <h1 style="margin-top:14px">Neurosurgeon in Dhaka: Dr. Md. Isma Azam (Zico)<span class="bn-line" lang="bn">নিউরো সার্জন ঢাকা · ব্রেইন ও স্পাইন সার্জন</span></h1>
  <p class="lead">A brain and spine surgeon in Dhaka treating patients from across Bangladesh, from slipped discs and neck problems to brain tumors, aneurysms and hydrocephalus. His own case log records <strong class="num">{fmt(ALL_TOTAL)}</strong> operations.</p>
  <div class="creds"><span class="chip">{icon('cap')} MBBS (DMC)</span><span class="chip">{icon('cap')} MRCS (England)</span><span class="chip">{icon('cap')} MS (Neurosurgery)</span><span class="chip">{icon('cap')} BCS (Health)</span></div>
  <div class="btn-row"><a class="btn btn-primary" href="appointment.html#book">{icon('calendar')} Book appointment</a><a class="btn btn-ghost" href="tel:{DOC['pa_intl']}">{icon('phone')} Call {DOC['pa']}</a></div>
  <div class="small muted" style="margin-top:14px;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center"><span>Continental, Gulshan: <span class="status" data-chamber-status="continental">Sat to Thu · 8:30 AM to 4 PM</span></span><span>Popular, Dhanmondi: <span class="status" data-chamber-status="popular">Sat, Mon, Wed · 10 PM to 12 AM</span></span></div>
 </div>
 <div class="hero-media">
  {local_photo('dr-zico-portrait.png', 1212, 1297, 'Dr. Zico portrait (cut-out)', 'Dr. Md. Isma Azam (Zico), neurosurgeon in Dhaka, in a white coat', 'Home', 'ph--fill').replace('loading="lazy"', 'loading="eager" fetchpriority="high"')}
  <div class="ledger ledger--float" aria-label="Surgical case log summary"><div class="ledger-head"><h2>Surgical case log</h2><span class="ledger-total">{fmt(ALL_TOTAL)}</span></div><ol>{ledger}</ol><div class="ledger-foot"><a href="about.html#case-log">See all 72 procedures</a></div></div>
 </div>
</div></section>

<section class="stats-band" aria-label="Key numbers"><div class="wrap"><div class="stats stats--band">
 <div class="stat"><b>{fmt(ALL_TOTAL)}</b><span>operations in his case log</span></div>
 <div class="stat"><b>{fmt(SPINE_TOTAL)}</b><span>spine operations</span></div>
 <div class="stat"><b>{fmt(BRAIN_TOTAL)}</b><span>brain operations</span></div>
 <div class="stat"><b>{fmt(total(SV["brain-tumor-surgery"]))}</b><span>brain tumor operations</span></div>
 <div class="stat"><b>295</b><span>aneurysm clippings</span></div>
</div></div></section>

<section class="section" id="finder"><div class="wrap split split--even">
 <div class="section-head"><span class="eyebrow">Find your problem</span><h2>What brings you to a neurosurgeon?</h2><p class="muted">Type a symptom or diagnosis in English or Bangla, such as "back pain", "কোমর ব্যথা", "pituitary" or "মাথায় পানি জমা", to go straight to the right page.</p></div>
 <div class="finder" data-finder data-limit="7">
  <label for="finder-home">Search conditions and symptoms</label>
  <div class="finder-input">{icon('search')}<input id="finder-home" type="search" autocomplete="off" placeholder="e.g. slipped disc, ঘাড় ব্যথা, aneurysm"></div>
  <div class="chips"><button type="button" data-q="কোমর ব্যথা">কোমর ব্যথা</button><button type="button" data-q="ঘাড় ব্যথা">ঘাড় ব্যথা</button><button type="button" data-q="brain tumor">Brain tumor</button><button type="button" data-q="মাথায় পানি জমা">মাথায় পানি জমা</button><button type="button" data-q="pituitary">Pituitary</button><button type="button" data-q="মুখে">মুখে ব্যথা</button></div>
  <ul class="finder-results" aria-live="polite"></ul><p class="finder-empty" hidden>No match yet. Try a simpler word, or <a href="services.html">see all services</a>.</p>
 </div>
</div></section>

<section class="section section--tint" id="services"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Services</span><h2>Brain and spine surgery services</h2><p class="muted">Nine areas of care, each with its own page explaining symptoms, when surgery is needed and what to expect. The number on each card is Dr. Zico's own operation count.</p></div>
 <div class="grid grid-3">{cards}</div>
</div></section>

<section class="bleed bleed--ot" aria-label="In the operating theatre">
 {local_photo('ot-team-microscope.jpg', 1800, 1350, 'In the operating theatre', 'Dr. Zico and the surgical team with a microscope and surgical monitor in the operating theatre', 'Home', 'ph--fill')}
 <div class="bleed-caption"><div class="wrap"><div class="caption-card"><span class="eyebrow">In the operating theatre</span><p>Brain and spine surgery happens in millimetres. Every operation is done under the microscope or endoscope with a full neurosurgery and anaesthesia team.</p></div></div></div>
</section>

<section class="section" id="technology"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Technology</span><h2>Precise tools for delicate surgery</h2><p class="muted">The tools behind Dr. Zico's operations at Continental Hospital, Gulshan 2 and Dr. Sirajul Islam Medical College &amp; Hospital.</p></div>
 <div class="grid grid-3">{techs}</div>
</div></section>

<section class="half-bleed section--tint" id="team">
 <div class="hb-media">{ph('team-photo.jpg', 1536, 2048, 'Team photo', 'Dr. Zico with neurosurgery and anaesthesia consultants, specialists and OT nurses', 'Dr. Zico with his surgical team', 'Home', 'ph--fill')}</div>
 <div class="hb-text"><div class="stack"><span class="eyebrow">Team</span><h2>The team behind every operation</h2><p class="muted">Brain and spine surgery is team work. Each operation involves neurosurgery and anaesthesia consultants, specialists and trained OT nurses, and the same team follows patients through recovery.</p>
 <div class="bn-box" lang="bn"><h3>আমাদের টিম</h3><p>প্রতিটি অপারেশনে নিউরোসার্জারি ও অ্যানেস্থেসিয়া কনসালট্যান্ট, বিশেষজ্ঞ ডাক্তার ও প্রশিক্ষিত OT নার্স একসাথে কাজ করেন।</p></div></div></div>
</section>

<section class="section" id="patients"><div class="wrap">
 <div class="section-head section-head--row"><div class="stack-sm"><span class="eyebrow">Our patients</span><h2>Back to everyday life</h2><p class="muted">Patients and families after treatment, shared with their written permission.</p><p class="small bn" lang="bn">আমাদের রোগীরা: চিকিৎসার পর স্বাভাবিক জীবনে</p></div><a class="btn btn-ghost" href="gallery.html#patients">{icon('image')} View patient photos</a></div>
 {happy_patient_carousel()}
 <dialog class="lightbox" id="lightbox" aria-label="Patient photo viewer"><button class="icon-btn lb-close" type="button" data-lb-close aria-label="Close">{icon('close')}</button><img alt=""><p class="lb-cap"></p></dialog>
</div></section>

<section class="section section--tint" id="before-after"><div class="wrap">
 <div class="section-head section-head--row"><div class="stack-sm"><span class="eyebrow">Before and after</span><h2>Results from real operations</h2><p class="muted">Scans and photos before and after surgery. Drag the handle to compare. All images are shared with written consent, with names removed.</p></div>
 <a class="btn btn-ghost" href="gallery.html">{icon('image')} Open patient gallery</a></div>
 {ba_carousel(CASES, 'Home')}
</div></section>

<section class="section" id="videos"><div class="wrap">
 <div class="section-head section-head--row"><div class="stack-sm"><span class="eyebrow">Videos</span><h2>Dr. Zico explains</h2><p class="muted">Short videos on common brain and spine problems. Tap a video to play it here.</p></div>
 <a class="btn btn-ghost" href="{DOC['yt']}" target="_blank" rel="noopener">{icon('play')} YouTube channel</a></div>
 {video_carousel('Home')}
</div></section>

<section class="section section--tint" id="facebook"><div class="wrap">
 <div class="section-head section-head--row"><div class="stack-sm"><span class="eyebrow">Facebook</span><h2>Latest from Facebook</h2><p class="muted">Recent posts, photos and videos from Dr. Zico's Facebook page. They update by themselves.</p></div>
 <a class="btn btn-ghost" href="{DOC['fb']}" target="_blank" rel="noopener">Visit Facebook page</a></div>
 <div id="fb-feed" class="fb-feed" data-feed="{FB_FEED_URL}" data-page="{DOC['fb']}">
  <p class="fb-sample-note small">Sample cards for preview. They are replaced by real Facebook posts once the feed is connected, and this section stays hidden on the live site until then.</p>
  <div class="fb-grid" aria-live="polite">{''.join('<div class="fb-card fb-skel" aria-hidden="true"><div class="fb-media"></div><div class="fb-body"><span></span><span></span></div></div>' for _ in range(8))}</div>
  <script src="assets/js/fb-feed.js" defer></script>
  <noscript><p><a href="{DOC['fb']}" target="_blank" rel="noopener">See the latest posts on Facebook</a></p></noscript>
 </div>
</div></section>

<section class="section" id="chambers"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Chambers</span><h2>Where to see Dr. Zico</h2><p class="muted">If you searched for a "neurosurgeon near me" in Dhaka: Dr. Zico sees patients at Continental Hospital in Gulshan during the day, and at two evening chambers in Dhanmondi and Malibag for people who work during the day.</p></div>
 {chamber_cards('Home')}
</div></section>

<section class="section"><div class="wrap split">
 <div class="stack">
  {faq_block(faqs, "home-faq")}
  <p><a href="faq.html">See all questions</a></p>
 </div>
 <aside class="stack">
  <div class="bn-box" lang="bn"><h3>বাংলায়: ডাঃ ইসমা আজম জিকো</h3><p>ডাঃ মোঃ ইসমা আজম (জিকো) ঢাকার একজন নিউরোসার্জন, অর্থাৎ ব্রেইন ও স্পাইন সার্জন। কোমর ব্যথা ও PLID, ঘাড়ের ডিস্ক, ব্রেইন টিউমার, মাথায় পানি জমা, মস্তিষ্কে রক্তক্ষরণ, মাথায় ও মেরুদণ্ডে আঘাতের চিকিৎসা ও অপারেশন করেন। ব্রেইনের ডাক্তার ঢাকায় খুঁজছেন? কন্টিনেন্টাল হাসপাতাল, গুলশান ২-এ শনি থেকে বৃহস্পতি সকাল ৮:৩০ থেকে বিকাল ৪টা, আর পপুলার ডায়াগনস্টিক সেন্টার, ধানমন্ডিতে শনি, সোম ও বুধবার রাত ১০টা থেকে ১২টা রোগী দেখেন। অ্যাপয়েন্টমেন্ট: {DOC['pa']}।</p></div>
  <a class="post-card" href="blog-komor-byatha-kon-doctor.html">{ph('blog-komor-byatha-cover.jpg', 1600, 900, 'Blog cover', 'Illustration: person holding lower back, spine highlighted (Canva)', 'Illustration of lower back pain', 'Blog', 'ph--sm')}<span class="tag">Bangla article</span><h3 lang="bn">কোমর ব্যথা হলে কোন ডাক্তার দেখাবেন: নিউরোলজিস্ট না নিউরোসার্জন?</h3><p class="small muted">When back pain needs a neurosurgeon, and when it does not.</p></a>
 </aside>
</div></section>

<section class="cta-full"><div class="wrap">{cta_band()}</div></section>
"""
    schema = [faq_schema(faqs), {"@context": "https://schema.org", "@type": "WebSite", "name": "Dr. Md. Isma Azam (Zico), Neurosurgeon", "url": SITE_URL + "/", "inLanguage": ["en", "bn"]}]
    return layout("index.html", "Neurosurgeon in Dhaka | Dr. Md. Isma Azam (Zico) | Brain & Spine Surgeon",
                  "Neurosurgeon in Dhaka, Bangladesh: Dr. Md. Isma Azam (Zico), brain and spine surgeon. 5,010 operations: PLID, ACDF, brain tumor, aneurysm, hydrocephalus. Chamber: Popular Dhanmondi.",
                  "home", body, schema)

def page_service(s):
    t = total(s)
    if s["slug"] in REAL_ONLY_SERVICES:
        OG_IMAGES[s["slug"] + ".html"] = (svc_img(s["slug"], "hero.jpg"), 1200, 750, HERO_ALT[s["slug"]])
        hero_img = local_photo(svc_img(s["slug"], "hero.jpg"), 1200, 750, s["name"] + ": main image", HERO_ALT[s["slug"]], s["name"], "ph--sm",
                               sizes="(max-width: 760px) 100vw, 440px", eager=True)
    else:
        hero_img = ph(svc_img(s['slug'], 'hero.jpg'), 1600, 1000, s['name'] + ': main image', 'OT photo of this operation (no patient face) or a clean medical illustration made in Canva', s['name'] + ' by Dr. Zico', s['name'], 'ph--sm')
    toc = "".join(f'<li><a href="#{sec["id"]}"><span>{esc(sec["h2"].split(":")[0].split("(")[0].strip())}</span><span class="num">{fmt(sum(n for _, n in sec["items"]))}</span></a></li>' for sec in s["sections"])
    toc = (f'<li><a href="#overview"><span>Overview</span></a></li>' if s.get("overview") else "") + toc + '<li><a href="#before"><span>Before your visit</span></a></li><li><a href="#faq"><span>Questions</span></a></li>' + ('<li><a href="#photos"><span>Photos</span></a></li>' if s["slug"] in SERVICE_GALLERIES else "")
    blocks = []
    if s.get("overview"):
        blocks.append(f'<section class="block" id="overview"><div class="block-head"><div><h2>Overview</h2></div></div><div class="prose">{s["overview"]}</div></section>')
    for sec in s["sections"]:
        n = sum(c for _, c in sec["items"])
        bd = ("<div class=\"breakdown\">" + "".join(f"<span>{esc(l)} <b>{fmt(c)}</b></span>" for l, c in sec["items"]) + "</div>") if len(sec["items"]) > 1 else ""
        short = re.sub(r"\s*\(.*?\)", "", sec["h2"]).split(":")[0]
        fig_file = svc_img(s["slug"], sec["id"] + ".jpg")
        if s["slug"] in REAL_ONLY_SERVICES:
            sec_fig = (local_photo(fig_file, 1200, 900, "Real photo: " + short, SEC_ALT[(s["slug"], sec["id"])], s["name"], "ph--sm")
                       if os.path.isfile(os.path.join(ROOT, "assets", "img", fig_file)) else "")
        else:
          sec_fig = ph(fig_file, 1200, 900, "Illustration: " + short,
                     "Simple anatomical illustration of this condition (Canva). No real scans with patient names",
                     SEC_ALT.get((s["slug"], sec["id"])) or re.sub(r"<[^>]+>", "", sec["h2"]), s["name"], "ph--sm")
        sym = "".join(f"<li>{x}</li>" for x in sec["symptoms"])
        sur = "".join(f"<li>{x}</li>" for x in sec["surgery"])
        blocks.append(f"""<section class="block" id="{sec['id']}">
<div class="block-head"><div><h2>{sec['h2']}</h2><span class="bn-sub" lang="bn">{sec['bn']}</span></div><span class="count-pill">{fmt(n)}<small>operations</small></span></div>
{bd}{f'<div class="figure-row"><div class="prose">{sec["intro"]}</div>{sec_fig}</div>' if sec_fig else f'<div class="prose">{sec["intro"]}</div>'}
<div class="cols"><div class="box"><h3>Common symptoms</h3><ul>{sym}</ul></div><div class="box"><h3>When surgery is considered</h3><ul>{sur}</ul></div></div>
<div class="prose"><h3>How Dr. Zico treats it</h3>{sec['how']}</div>
{case_blocks(s["slug"], sec["id"])}<div class="bn-box" lang="bn"><h3>{sec['bn_title']}</h3><p>{sec['bn_text']}</p></div>
</section>""")
    if s.get("recovery"):
        blocks.append(f'<section class="block" id="recovery"><div class="block-head"><div><h2>Recovery and what to expect</h2></div></div><div class="prose">{s["recovery"]}</div></section>')
    blocks.append(f"""<section class="block" id="before"><div class="block-head"><div><h2>Before your consultation</h2><span class="bn-sub" lang="bn">চেম্বারে যা সাথে আনবেন</span></div></div>
<div class="cols"><div class="box"><h3>Bring with you</h3>{BRING}</div><div class="box"><h3>How to book</h3><ol class="small" style="padding-left:1.2em"><li>Call his personal assistant on <a href="tel:{DOC['pa_intl']}">{DOC['pa']}</a>, the Popular Dhanmondi serial line <a href="tel:{DOC['phone_popular_intl']}">{DOC['phone_popular']}</a> or the Continental hotline {DOC['continental_hotline']}, or <a href="appointment.html?concern={s['concern']}#book">send a request online</a>.</li><li>Come to your chamber on the booked day with your films and reports.</li><li>Dr. Zico examines you, reviews your scans and explains your options.</li></ol></div></div></section>""")
    blocks.append(faq_block(s["faq"]))
    rel = "".join(svc_card(SV[r]) for r in s["related"])
    blocks.append(f'<section class="block"><div class="block-head"><div><h2>Related services</h2></div></div><div class="grid grid-3">{rel}</div></section>')
    blocks.append(service_gallery(s))
    emerg = f'<div class="emergency" role="note">{icon("alert")}<p>{s["emergency"]}</p></div>' if s.get("emergency") else ""
    body = f"""{crumbs([("Home", "index.html"), ("Services", "services.html"), (s['name'], s['slug'] + '.html')])}
<section class="page-hero"><div class="wrap split">
 <div><span class="eyebrow">Neurosurgery service</span><h1 style="margin-top:12px">{esc(s['h1'])}<span class="bn-line" lang="bn">{esc(s['bn_h1'])}</span></h1><p class="lead" style="margin-top:18px">{s['lead']}</p>
 <div class="btn-row" style="margin-top:24px"><a class="btn btn-primary" href="appointment.html?concern={s['concern']}#book">{icon('calendar')} Book appointment</a><a class="btn btn-ghost" href="tel:{DOC['pa_intl']}">{icon('phone')} {DOC['pa']}</a></div></div>
 <aside class="hero-card">{hero_img}<span class="eyebrow">From Dr. Zico's case log</span><span class="big-n">{fmt(t)}</span><span class="muted small">{esc(s['name'])} operations performed</span>
 <div class="breakdown">{''.join(f'<span>{esc(sec["h2"].split(":")[0].split("(")[0].strip())} <b>{fmt(sum(n for _, n in sec["items"]))}</b></span>' for sec in s['sections'])}</div>{emerg}</aside>
</div></section>
<div class="wrap page-layout">
 <aside class="toc"><nav aria-label="On this page"><h2>On this page</h2><ol>{toc}</ol><a class="btn btn-primary toc-cta" href="appointment.html?concern={s['concern']}#book">Book appointment</a></nav></aside>
 <div class="content">{''.join(blocks)}{cta_band(s['concern'])}<p class="notice">This page explains common conditions in general terms and is not a diagnosis. Treatment is decided after Dr. Zico examines you and reviews your scans.</p></div>
</div>"""
    schema = [
        dict({"@context": "https://schema.org", "@type": "MedicalWebPage", "name": s["h1"], "url": f"{SITE_URL}/{s['slug']}.html", "inLanguage": ["en", "bn"],
         "description": s["desc"], "lastReviewed": LAST_REVIEWED, "dateModified": LAST_REVIEWED,
         "about": [{"@type": "MedicalCondition", "name": re.sub(r"<[^>]+>", "", sec["h2"])} for sec in s["sections"]],
         "mainEntity": {"@id": PHYSICIAN_ID}}, **page_images_schema(s)),
        breadcrumb_schema([("Home", "index.html"), ("Services", "services.html"), (s["name"], s["slug"] + ".html")]),
        faq_schema(s["faq"]),
    ]
    return layout(s["slug"] + ".html", s["title"], s["desc"], "service", body, schema)

def page_services():
    cards = "".join(svc_card(s) for s in SERVICES)
    lists = "".join(
        f'<div class="box"><h3><a href="{s["slug"]}.html">{esc(s["name"])}</a> <span class="num muted small">{fmt(total(s))}</span></h3><ul>' +
        "".join(f'<li><a href="{s["slug"]}.html#{sec["id"]}">{esc(sec["h2"])}</a> <span class="num muted">{fmt(sum(n for _, n in sec["items"]))}</span></li>' for sec in s["sections"]) + "</ul></div>"
        for s in SERVICES)
    body = f"""{crumbs([("Home", "index.html"), ("Services", "services.html")])}
<section class="page-hero"><div class="wrap split">
 <div><span class="eyebrow">Services</span><h1 style="margin-top:12px">Neurosurgery Services in Dhaka<span class="bn-line" lang="bn">নিউরোসার্জারি: মস্তিষ্ক ও মেরুদণ্ডের চিকিৎসা</span></h1><p class="lead" style="margin-top:18px">Every condition Dr. Zico treats, grouped into nine services, with his operation count for each.</p></div>
 <div class="finder" data-finder data-limit="8" id="finder"><label for="finder-svc">Search conditions and symptoms</label><div class="finder-input">{icon('search')}<input id="finder-svc" type="search" autocomplete="off" placeholder="e.g. সায়াটিকা, meningioma, spine fracture"></div>
 <div class="chips"><button type="button" data-q="জলমাথা">জলমাথা</button><button type="button" data-q="sciatica">Sciatica</button><button type="button" data-q="stroke">Stroke</button><button type="button" data-q="যক্ষ্মা">মেরুদণ্ডের যক্ষ্মা</button></div>
 <ul class="finder-results" aria-live="polite"></ul><p class="finder-empty" hidden>No match yet. Try another word or browse the list below.</p></div>
</div></section>
<section class="section"><div class="wrap"><div class="grid grid-3">{cards}</div></div></section>
<section class="section section--tint"><div class="wrap"><div class="section-head"><span class="eyebrow">All conditions</span><h2>Every condition, with case numbers</h2></div><div class="grid grid-3">{lists}</div></div></section>
<section class="cta-full"><div class="wrap">{cta_band()}</div></section>"""
    return layout("services.html", "Neurosurgery Services in Dhaka | Brain & Spine Surgery | Dr. Zico",
                  "All neurosurgery services by Dr. Md. Isma Azam (Zico) in Dhaka: PLID, spine surgery, brain tumor, hydrocephalus, aneurysm, spinal tumor, spinal TB, head injury, trigeminal neuralgia.",
                  "services", body, [breadcrumb_schema([("Home", "index.html"), ("Services", "services.html")])])

def page_about():
    rows = ""
    for s in SERVICES:
        rows += f'<tr class="grp"><td>{esc(s["name"])}</td><td class="n">{fmt(total(s))}</td></tr>'
        for sec in s["sections"]:
            for l, c in sec["items"]:
                rows += f"<tr><td>{esc(l)}</td><td class=\"n\">{fmt(c)}</td></tr>"
    rows += f'<tr class="grp"><td>Total</td><td class="n">{fmt(ALL_TOTAL)}</td></tr>'
    body = f"""{crumbs([("Home", "index.html"), ("About", "about.html")])}
<section class="page-hero"><div class="wrap split">
 <div><span class="eyebrow">About</span><h1 style="margin-top:12px">Dr. Md. Isma Azam (Zico), Neurosurgeon<span class="bn-line" lang="bn">ডাঃ মোঃ ইসমা আজম (জিকো), নিউরোসার্জন</span></h1>
 <p class="lead" style="margin-top:18px">A brain and spine surgeon trained at Dhaka Medical College, the Royal College of Surgeons of England and Bangladesh's national medical university, with a case log of {fmt(ALL_TOTAL)} operations.</p>
 <div class="creds"><span class="chip">{icon('cap')} {DOC['degrees']}</span></div></div>
 <div class="about-portrait" style="max-width:380px;width:100%">{ph('dr-zico-about.jpg', 1200, 1500, 'Dr. Zico portrait (About)', 'Second portrait: at the desk, in scrubs, or with the microscope', 'Dr. Md. Isma Azam (Zico)', 'About')}</div>
</div></section>
<div class="wrap page-layout">
 <aside class="toc"><nav aria-label="On this page"><h2>On this page</h2><ol><li><a href="#profile">Profile</a></li><li><a href="#training">Training and career</a></li><li><a href="#technology">Technology and team</a></li><li><a href="#gallery">Gallery</a></li><li><a href="#case-log">Case log</a></li></ol><a class="btn btn-primary toc-cta" href="appointment.html#book">Book appointment</a></nav></aside>
 <div class="content">
  <section class="block" id="profile"><div class="block-head"><div><h2>Profile</h2></div></div><div class="prose">
   <p>Dr. Md. Isma Azam, known to patients as Dr. Zico, is a neurosurgeon in Dhaka who treats the full range of brain and spine conditions. His largest areas of work are lumbar disc (PLID) surgery, microscopic neck surgery (ACDF), brain tumors including endoscopic pituitary surgery, aneurysm surgery and hydrocephalus.</p>
   <p>He is Associate Consultant, Neuro Surgery at Continental Hospital (formerly United Hospital), Gulshan 2, and previously served as Assistant Professor of Neurosurgery at Dhaka Medical College Hospital. His hospital lists more than 5,000 surgeries across his career; the case log below lists {fmt(ALL_TOTAL)} by procedure.</p>
   <p>He believes patients should understand their scans and their choices. Many people he sees do not need an operation, and he says so.</p>
  </div><div class="bn-box" lang="bn"><h3>বাংলায়</h3><p>ডাঃ মোঃ ইসমা আজম (জিকো) ঢাকা মেডিকেল কলেজ থেকে MBBS, ইংল্যান্ডের রয়্যাল কলেজ অব সার্জনস থেকে MRCS এবং নিউরোসার্জারিতে MS করেছেন। তিনি কোমর ব্যথা ও PLID, ঘাড়ের ডিস্ক, ব্রেইন টিউমার, অ্যানিউরিজম ও মাথায় পানি জমার অপারেশন করেন।</p></div></section>

  <section class="block" id="training"><div class="block-head"><div><h2>Training and career</h2></div></div>
  <ol class="timeline">
   <li><span class="when">2007</span><div class="what">MBBS, Dhaka Medical College</div></li>
   <li><span class="when">29th BCS</span><div class="what">BCS (Health), Government health service</div></li>
   <li><span class="when">2010 to 2012</span><div class="what">Assistant Surgeon, Kazipur, Sirajganj</div></li>
   <li><span class="when">2011</span><div class="what">MRCS, Royal College of Surgeons of England</div></li>
   <li><span class="when">2012 to 2013</span><div class="what">Assistant Registrar, Surgery, Sir Salimullah Medical College</div></li>
   <li><span class="when">2013 to 2014</span><div class="what">Assistant Registrar, Orthopaedics and Traumatology, Sir Salimullah Medical College</div></li>
   <li><span class="when">2017 to 2023</span><div class="what">Registrar, Department of Neurosurgery, Dhaka Medical College Hospital</div></li>
   <li><span class="when">2019</span><div class="what">MS (Neurosurgery), Bangabandhu Sheikh Mujib Medical University (now Bangladesh Medical University)</div></li>
   <li><span class="when">{v('Feb 2023 to Sep 2025', 'Dates from Continental Hospital; his Facebook still shows this post as current. Confirm.')}</span><div class="what">Assistant Professor of Neurosurgery, Dhaka Medical College Hospital</div></li>
   <li><span class="when">Current</span><div class="what">Associate Consultant, Neuro Surgery, Continental Hospital (formerly United Hospital), Gulshan 2</div></li>
  </ol>
  <div class="box"><h3>Memberships</h3><ul><li>{v('Member, AO Spine (Asia Pacific)', 'From directories. Confirm.')}</li><li>Executive Member, Neurospine Society Bangladesh</li><li>Executive Member, DMC Alumni Trust</li></ul></div>
  </section>

  <section class="block" id="technology"><div class="block-head"><div><h2>Technology and team</h2><span class="bn-sub" lang="bn">আধুনিক যন্ত্র ও দক্ষ টিম</span></div></div><div class="prose">
   <p>Dr. Zico operates with the operating microscope, neuro-endoscope and {v('EXOSCOPE, a high-definition 3D camera system for ultra-fine microsurgery', 'Confirm where the EXOSCOPE is available.')}. He uses keyhole and minimally invasive approaches when they are safe for the patient. Each operation involves a team of neurosurgery and anaesthesia consultants, specialists and trained OT nurses.</p></div></section>

  <section class="block" id="gallery"><div class="block-head"><div><h2>Gallery</h2><span class="bn-sub" lang="bn">ছবিতে কাজ</span></div></div>
  <div class="gallery gallery--ot">{operating_theatre_photos('About')}</div></section>

  <section class="block" id="case-log"><div class="block-head"><div><h2>Surgical case log</h2><span class="bn-sub" lang="bn">অপারেশনের হিসাব</span></div><span class="count-pill">{fmt(ALL_TOTAL)}<small>total</small></span></div>
  <p class="muted">Numbers as recorded by Dr. Zico. {v('Figures current to September 2026.', 'Confirm the date the list was last updated, and the missing meningioma sub-type numbers (clinoidal, cavernous sinus).')}</p>
  <div class="logbook-wrap"><table class="logbook"><thead><tr><th scope="col">Procedure or condition</th><th scope="col" style="text-align:right">Operations</th></tr></thead><tbody>{rows}</tbody></table></div></section>
  {cta_band()}
 </div>
</div>"""
    return layout("about.html", "About Dr. Md. Isma Azam (Zico) | Neurosurgeon, MRCS, MS",
                  "Dr. Md. Isma Azam (Zico): MBBS (DMC), MRCS (England), MS (Neurosurgery). Training, career and full surgical case log of 5,010 brain and spine operations.",
                  "about", body, [breadcrumb_schema([("Home", "index.html"), ("About", "about.html")])])

def page_appointment():
    opts = "".join(f'<option value="{s["concern"]}">{esc(s["name"])}</option>' for s in SERVICES)
    body = f"""{crumbs([("Home", "index.html"), ("Chambers and appointment", "appointment.html")])}
<section class="page-hero"><div class="wrap">
 <span class="eyebrow">Chambers and appointment</span><h1 style="margin-top:12px">Book an Appointment with Dr. Zico<span class="bn-line" lang="bn">সিরিয়াল ও চেম্বারের তথ্য</span></h1>
 <p class="lead" style="margin-top:18px">Dr. Zico sees patients at three places in Dhaka. The quickest way to book is to call his personal assistant on <a href="tel:{DOC['pa_intl']}">{DOC['pa']}</a> or the chamber directly. You can also send a request below.</p>
</div></section>
<section class="section" id="chambers"><div class="wrap"><h2 class="vh">Dr. Zico's chambers</h2>{chamber_cards('Appointment')}</div></section>
<section class="section section--tint" id="book"><div class="wrap split" data-wa="{DOC['pa_intl'].lstrip('+')}">
 <div>
  <form class="bk" id="booking-form" novalidate>
   <div class="bk-head"><h2>Request a serial on WhatsApp</h2>
    <p class="muted">Takes less than a minute. Your details go to Dr. Zico's assistant on WhatsApp, who will reply with your serial and time.</p>
    <p class="bk-bn small" lang="bn">ফর্মটি পূরণ করে পাঠালে ডাঃ জিকোর সহকারীর হোয়াটসঅ্যাপে চলে যাবে, তিনি সিরিয়াল জানিয়ে দেবেন।</p></div>
   <div class="bk-step"><span class="bk-label" id="bk-ch-label"><b>1</b> Choose a chamber</span>
    <div class="bk-chambers" role="radiogroup" aria-labelledby="bk-ch-label">
     <label class="bk-ch"><input type="radio" name="chamber" value="continental"><span class="bk-ch-box"><strong>Continental Hospital</strong><span>Gulshan 2</span><span class="bk-when">Sat to Thu, 8:30 AM to 4 PM</span></span></label>
     <label class="bk-ch"><input type="radio" name="chamber" value="popular" checked><span class="bk-ch-box"><strong>Popular Diagnostic</strong><span>Dhanmondi</span><span class="bk-when">Sat, Mon, Wed, 10 PM to 12 AM</span></span></label>
     <label class="bk-ch"><input type="radio" name="chamber" value="malibag"><span class="bk-ch-box"><strong>Dr. Sirajul Islam MCH</strong><span>Malibag</span><span class="bk-when">Day and time confirmed on WhatsApp</span></span></label>
    </div></div>
   <div class="bk-step"><span class="bk-label" id="bk-day-label"><b>2</b> Preferred day <em>(optional)</em></span>
    <div class="bk-days" id="bk-days" role="radiogroup" aria-labelledby="bk-day-label"></div></div>
   <div class="bk-step"><span class="bk-label"><b>3</b> Patient details</span>
    <div class="bk-grid">
     <div class="bk-field"><label for="b-name">Patient's name</label><input id="b-name" name="name" autocomplete="name" placeholder="Full name" required><span class="bk-err" id="b-name-err" hidden></span></div>
     <div class="bk-field"><label for="b-phone">Mobile number</label><input id="b-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="01XXXXXXXXX" required><span class="bk-err" id="b-phone-err" hidden></span></div>
     <div class="bk-field"><label for="b-concern">Problem <em>(optional)</em></label><select id="b-concern" name="concern"><option value="">Choose if you know</option>{opts}<option value="unsure">Not sure</option></select></div>
     <div class="bk-field"><label for="b-notes">Short note <em>(optional)</em></label><input id="b-notes" name="notes" maxlength="200" placeholder="e.g. back pain for 2 months, have MRI"></div>
    </div></div>
   <button class="bk-send" type="submit"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.2c0-.1-.2-.2-.4-.3Z"/></svg> Send on WhatsApp</button>
   <p class="bk-alt small">Prefer to call? <a href="tel:{DOC['pa_intl']}">{DOC['pa']}</a> (personal assistant)</p>
  </form>
  <div class="bk-done" id="booking-success" tabindex="-1" hidden>
   <div class="bk-done-ic" aria-hidden="true">{icon('check')}</div>
   <h2>WhatsApp is open</h2>
   <p>Your message to Dr. Zico's assistant is ready. <strong>Press Send in WhatsApp</strong> to finish. The assistant will reply with your serial.</p>
   <p class="small muted" lang="bn">হোয়াটসঅ্যাপে মেসেজ তৈরি আছে, শুধু Send চাপুন।</p>
   <div class="btn-row"><a class="btn btn-primary" id="bk-reopen" href="#" target="_blank" rel="noopener">Open WhatsApp again</a><button class="btn btn-ghost" type="button" id="b-again">Edit details</button></div>
   <p class="small muted">WhatsApp not installed? Call <a href="tel:{DOC['pa_intl']}">{DOC['pa']}</a>.</p>
  </div>
 </div>
 <aside class="stack">
  <div class="box"><h3 class="box-title">{icon('file')} Bring with you</h3>{BRING}</div>
  <div class="box"><h3>How the serial works</h3><ol class="steps-list small"><li>Call the chamber number, or send a request here.</li><li>The chamber gives you a serial number and time.</li><li>Arrive a little early with your films and reports.</li></ol></div>
  <div class="bn-box" lang="bn"><h3>সিরিয়াল নিতে</h3><p>ব্যক্তিগত সহকারী: {DOC['pa']}। কন্টিনেন্টাল হাসপাতাল (শনি থেকে বৃহস্পতি, সকাল ৮:৩০ থেকে বিকাল ৪টা): হটলাইন ১০৬৬৬। পপুলার ডায়াগনস্টিক সেন্টার, ধানমন্ডি: {DOC['phone_popular']} (শনি, সোম, বুধ, রাত ১০টা থেকে ১২টা)। সব MRI/CT রিপোর্ট সাথে আনুন।</p></div>
 </aside>
</div></section>"""
    return layout("appointment.html", "Book Appointment | Dr. Zico Neurosurgeon | Popular Dhanmondi Serial",
                  "Get a serial for Dr. Md. Isma Azam (Zico), neurosurgeon: Popular Diagnostic Centre Dhanmondi, Sat, Mon, Wed 10 PM to 12 AM, call 09666 787801. Chamber in Malibag too.",
                  "appointment", body, [breadcrumb_schema([("Home", "index.html"), ("Chambers and appointment", "appointment.html")])])

def page_gallery():
    chips = "".join(f'<button type="button" data-filter="{k}" aria-pressed="false">{l}</button>' for k, l in [("all", "All"), ("spine", "Spine"), ("brain", "Brain")]).replace('data-filter="all" aria-pressed="false"', 'data-filter="all" aria-pressed="true"', 1)
    cases = "".join(ba_card(c, "Gallery") for c in CASES)
    pics = operating_theatre_photos("Gallery", lightbox=True)
    body = f"""{crumbs([("Home", "index.html"), ("Patient gallery", "gallery.html")])}
<section class="page-hero"><div class="wrap"><span class="eyebrow">Patient gallery</span><h1 style="margin-top:12px">Before and After: Patient Gallery<span class="bn-line" lang="bn">রোগীদের অপারেশনের আগে ও পরে</span></h1>
<p class="lead" style="margin-top:18px">Scans and photos from Dr. Zico's operations, shared with patients' written consent and with names removed. Drag the handle on each image to compare before and after.</p></div></section>
<section class="section" id="cases"><div class="wrap">
 <div class="filter-bar" role="group" aria-label="Filter cases">{chips}<span class="small muted" id="filter-count" aria-live="polite"></span></div>
 <div class="ba-grid" data-filter-scope>{cases}</div>
 <p class="notice" style="margin-top:24px">Results differ from patient to patient. These images show individual cases and are not a promise of the same result.</p>
</div></section>
<section class="section" id="patients"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Our patients</span><h2>Back to everyday life</h2><p class="muted">Patients and families with Dr. Zico. Tap any photo to see the full image.</p><p class="small bn" lang="bn">আমাদের রোগীদের ছবি: বড় করে দেখতে ছবিতে চাপ দিন।</p></div>
 {happy_patient_carousel()}
</div></section>
<section class="section section--tint" id="photos"><div class="wrap">
 <div class="section-head"><span class="eyebrow">Photo gallery</span><h2>In the operating theatre and the ward</h2><p class="muted">Tap any photo to see it larger.</p></div>
 <div class="gallery gallery--lb gallery--ot">{pics}</div>
</div></section>
<dialog class="lightbox" id="lightbox" aria-label="Photo viewer"><button class="icon-btn lb-close" type="button" data-lb-close aria-label="Close">{icon('close')}</button><img alt=""><p class="lb-cap"></p></dialog>
<section class="cta-full"><div class="wrap">{cta_band()}</div></section>"""
    return layout("gallery.html", "Patient Gallery: Before and After Surgery | Dr. Zico Neurosurgeon",
                  "Before and after scans and photos from brain and spine operations by Dr. Md. Isma Azam (Zico), neurosurgeon in Dhaka, shared with patient consent.",
                  "gallery", body, [breadcrumb_schema([("Home", "index.html"), ("Patient gallery", "gallery.html")])])

def page_faq():
    links = "".join(f'<li><a href="{s["slug"]}.html#faq">{esc(s["name"])}</a></li>' for s in SERVICES)
    body = f"""{crumbs([("Home", "index.html"), ("FAQ", "faq.html")])}
<section class="page-hero"><div class="wrap"><span class="eyebrow">FAQ</span><h1 style="margin-top:12px">Questions About Seeing a Neurosurgeon<span class="bn-line" lang="bn">নিউরোসার্জন নিয়ে সাধারণ প্রশ্ন</span></h1><p class="lead" style="margin-top:18px">Answers to what patients most often ask before their first visit.</p></div></section>
<div class="wrap page-layout">
 <aside class="toc"><nav aria-label="Questions by service"><h2>Questions by service</h2><ol>{links}</ol><a class="btn btn-primary toc-cta" href="appointment.html#book">Book appointment</a></nav></aside>
 <div class="content">{faq_block(GENERAL_FAQ, "faq", "Common questions", show_filter=True)}{cta_band()}</div>
</div>"""
    return layout("faq.html", "Neurosurgeon FAQ | Serial, Reports, Fees | Dr. Zico Dhaka",
                  "Common questions about seeing a neurosurgeon in Dhaka: neurologist vs neurosurgeon, how to get a serial, what reports to bring, when it is an emergency. Bangla and English.",
                  "faq", body, [faq_schema(GENERAL_FAQ), breadcrumb_schema([("Home", "index.html"), ("FAQ", "faq.html")])])

UPCOMING = ["ডিস্ক প্রলাপস (PLID) কি অপারেশন ছাড়া ভালো হয়?", "ব্রেইন টিউমারের প্রাথমিক লক্ষণ কী কী?", "মাথায় পানি জমা (হাইড্রোসেফালাস) কেন হয়, শান্ট অপারেশন কী?",
            "ঘাড় ব্যথা ও হাত ঝিনঝিন: সার্ভাইক্যাল স্পন্ডাইলোসিসের চিকিৎসা", "নাক দিয়ে পিটুইটারি টিউমার অপারেশন: কীভাবে হয়?", "EXOSCOPE কী, নিউরোসার্জারিতে কেন দরকার?"]

def page_blog():
    up = "".join(f'<li lang="bn">{esc(t)}</li>' for t in UPCOMING)
    body = f"""{crumbs([("Home", "index.html"), ("Blog", "blog.html")])}
<section class="page-hero"><div class="wrap"><span class="eyebrow">Blog</span><h1 style="margin-top:12px">Brain and Spine Health Articles<span class="bn-line" lang="bn">মস্তিষ্ক ও মেরুদণ্ডের স্বাস্থ্য নিয়ে লেখা</span></h1><p class="lead" style="margin-top:18px">Plain-language articles, mostly in Bangla, answering the questions patients ask in the chamber.</p></div></section>
<section class="section"><div class="wrap split">
 <div class="grid"><a class="post-card" href="blog-komor-byatha-kon-doctor.html">{ph('blog-komor-byatha-cover.jpg', 1600, 900, 'Blog cover', 'Illustration: person holding lower back, spine highlighted (Canva)', 'Illustration of lower back pain', 'Blog', 'ph--sm')}<span class="tag">Spine · বাংলা</span><h3 lang="bn">কোমর ব্যথা হলে কোন ডাক্তার দেখাবেন: নিউরোলজিস্ট না নিউরোসার্জন?</h3><p class="small muted" lang="bn">কখন নিউরোসার্জন দরকার, আর কখন দরকার নেই, সহজ ভাষায়।</p><span class="more small" style="color:var(--brand);font-weight:700">Read article</span></a></div>
 <aside><div class="box"><h3>Coming next</h3><ul class="upcoming">{up}</ul></div></aside>
</div></section>"""
    return layout("blog.html", "Brain & Spine Health Articles in Bangla | Dr. Zico Neurosurgeon",
                  "Bangla articles on back pain, PLID, brain tumor, hydrocephalus and neurosurgery by the team of Dr. Md. Isma Azam (Zico), neurosurgeon in Dhaka.",
                  "blog", body, [breadcrumb_schema([("Home", "index.html"), ("Blog", "blog.html")])])

def page_article():
    body = f"""{crumbs([("Home", "index.html"), ("Blog", "blog.html"), ("কোমর ব্যথা: কোন ডাক্তার?", "blog-komor-byatha-kon-doctor.html")])}
<article class="section"><div class="wrap"><div class="article" lang="bn">
 <span class="eyebrow">মেরুদণ্ড · কোমর ব্যথা</span>
 <h1>কোমর ব্যথা হলে কোন ডাক্তার দেখাবেন: নিউরোলজিস্ট না নিউরোসার্জন?</h1>
 <p class="byline">{v('ডাঃ মোঃ ইসমা আজম (জিকো) কর্তৃক পর্যালোচিত', 'Have Dr. Zico read and approve this article before publishing.')}</p>
 {ph('blog-komor-byatha-cover.jpg', 1600, 900, 'Blog cover', 'Illustration: person holding lower back, spine highlighted (Canva)', 'কোমর ব্যথার চিত্র', 'Blog')}
 <p>কোমর ব্যথা হয়নি এমন মানুষ খুঁজে পাওয়া কঠিন। কিন্তু ব্যথা হলে প্রথম প্রশ্ন আসে: কোন ডাক্তার দেখাবো? অর্থোপেডিক, নিউরোলজিস্ট, নিউরোসার্জন, নাকি ফিজিওথেরাপিস্ট? এই লেখায় সহজ ভাষায় বুঝিয়ে বলা হলো।</p>
 <h2>নিউরোলজিস্ট আর নিউরোসার্জনের পার্থক্য</h2>
 <p><strong>নিউরোলজিস্ট</strong> স্নায়ুরোগ বিশেষজ্ঞ, যিনি ওষুধ দিয়ে চিকিৎসা করেন: যেমন মৃগী, মাইগ্রেন, স্ট্রোক বা পারকিনসন্স। <strong>নিউরোসার্জন</strong> মস্তিষ্ক, মেরুদণ্ড ও নার্ভের সেই সমস্যাগুলোর চিকিৎসা করেন যেখানে অপারেশন লাগতে পারে: যেমন ডিস্ক প্রলাপস বা PLID, ঘাড়ের রগে চাপ, টিউমার বা আঘাত। তবে নিউরোসার্জনের কাছে আসা অনেক রোগীরই অপারেশন লাগে না।</p>
 <table><thead><tr><th>যখন এমন হয়</th><th>যাকে দেখাবেন</th></tr></thead><tbody>
  <tr><td>হঠাৎ কোমরে টান, পায়ে ব্যথা নেই</td><td>প্রথমে সাধারণ চিকিৎসক বা ফিজিওথেরাপি</td></tr>
  <tr><td>কোমর ব্যথা ও পায়ে ঝিনঝিন, সায়াটিকা</td><td>নিউরোসার্জন বা স্পাইন সার্জন</td></tr>
  <tr><td>পা দুর্বল হয়ে যাচ্ছে, পায়ের পাতা ঝুলে যাচ্ছে</td><td>দ্রুত নিউরোসার্জন</td></tr>
  <tr><td>প্রস্রাব-পায়খানার নিয়ন্ত্রণ চলে যাচ্ছে</td><td>এখনই হাসপাতালের জরুরি বিভাগে</td></tr>
 </tbody></table>
 <h2>কোমর ব্যথার সাধারণ কারণ</h2>
 <p>বেশিরভাগ কোমর ব্যথা মাংসপেশির টান থেকে হয় এবং কয়েক সপ্তাহে নিজেই সেরে যায়। ব্যথা যখন কোমর থেকে পা পর্যন্ত নামে, সাথে ঝিনঝিন বা অবশ ভাব থাকে, তখন সাধারণত ডিস্ক সরে গিয়ে নার্ভে চাপ দিচ্ছে। একে বলে <a href="plid-lumbar-disc-surgery.html">PLID বা ডিস্ক প্রলাপস</a>। মেরুদণ্ডের হাড় সরে যাওয়া (<a href="spine-surgery.html#spondylolisthesis">স্পন্ডাইলোলিসথেসিস</a>) বা <a href="spinal-tb-potts-disease.html">মেরুদণ্ডের যক্ষ্মাও</a> কোমর ব্যথার কারণ হতে পারে।</p>
 <h2>কখন দেরি করা যাবে না</h2>
 <ul><li>পা ক্রমশ দুর্বল হয়ে যাওয়া</li><li>প্রস্রাব বা পায়খানা আটকে যাওয়া বা নিয়ন্ত্রণ না থাকা</li><li>যৌনাঙ্গের চারপাশ অবশ লাগা</li><li>জ্বর, ওজন কমা বা রাতে বেশি ব্যথার সাথে কোমর ব্যথা</li></ul>
 <p>এসব লক্ষণ থাকলে দ্রুত নিউরোসার্জন দেখান বা জরুরি বিভাগে যান।</p>
 <h2>ডাক্তার দেখানোর আগে যা করবেন</h2>
 <p>আগের সব MRI বা CT স্ক্যানের ফিল্ম ও রিপোর্ট, প্রেসক্রিপশন এবং যে ওষুধ খাচ্ছেন তার তালিকা সাথে রাখুন। ব্যথা কবে শুরু হয়েছে, কোন দিকে নামে, কী করলে বাড়ে বা কমে, তা লিখে আনলে ডাক্তারের জন্য সুবিধা হয়।</p>
 <h2>অপারেশন কি লাগবেই?</h2>
 <p>না। PLID-এর বেশিরভাগ রোগী ওষুধ, বিশ্রাম ও ফিজিওথেরাপিতে ভালো হন। অপারেশন লাগে যখন ৬ সপ্তাহ চিকিৎসার পরও পায়ের ব্যথা কমে না, দুর্বলতা বাড়ে বা প্রস্রাব-পায়খানার নিয়ন্ত্রণ চলে যায়।</p>
 <div class="bn-box"><h3>ডাঃ জিকোর চেম্বার</h3><p>কন্টিনেন্টাল হাসপাতাল, গুলশান ২: শনি থেকে বৃহস্পতি সকাল ৮:৩০ থেকে বিকাল ৪টা (হটলাইন ১০৬৬৬)। পপুলার ডায়াগনস্টিক সেন্টার, ধানমন্ডি: শনি, সোম ও বুধবার রাত ১০টা থেকে ১২টা। অ্যাপয়েন্টমেন্ট: {DOC['pa']}। <a href="appointment.html?concern=plid#book">অনলাইনে অনুরোধ পাঠান</a>।</p></div>
 <p class="notice">এই লেখা সাধারণ তথ্যের জন্য; এটি ডাক্তারের পরামর্শের বিকল্প নয়।</p>
</div></div></article>"""
    schema = [{"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": "কোমর ব্যথা হলে কোন ডাক্তার দেখাবেন: নিউরোলজিস্ট না নিউরোসার্জন?", "inLanguage": "bn", "url": SITE_URL + "/blog-komor-byatha-kon-doctor.html", "about": {"@type": "MedicalCondition", "name": "Low back pain"}},
              breadcrumb_schema([("Home", "index.html"), ("Blog", "blog.html"), ("কোমর ব্যথা: কোন ডাক্তার?", "blog-komor-byatha-kon-doctor.html")])]
    html_out = layout("blog-komor-byatha-kon-doctor.html", "কোমর ব্যথা হলে কোন ডাক্তার দেখাবেন? নিউরোলজিস্ট না নিউরোসার্জন",
                      "কোমর ব্যথা ও পায়ে ঝিনঝিন হলে কোন ডাক্তার দেখাবেন, কখন নিউরোসার্জন দরকার এবং কখন জরুরি বিভাগে যেতে হবে। সহজ বাংলায়।",
                      "blog", body, schema)
    return html_out.replace('<html lang="en">', '<html lang="bn">', 1)

# ------------------------------------------------------------------ finder data
ALIASES = {
    "what-is-plid": "slipped disc disc prolapse sciatica back pain leg pain komor betha কোমর ব্যথা কোমড় ব্যথা সায়াটিকা পায়ে ঝিনঝিন ডিস্ক সরে যাওয়া lumbar",
    "cervical": "neck pain ghar betha ঘাড় ব্যথা হাত ঝিনঝিন myelopathy cervical spondylosis ঘাড়ের রগ neck disc",
    "spondylolisthesis": "slipped vertebra miss tlif screw ফুটা করে স্ক্রু কোমরের হাড় সরে যাওয়া",
    "spine-trauma": "spine fracture accident fall spinal cord injury মেরুদণ্ডের হাড় ভাঙা মেরুদণ্ডে আঘাত atlantoaxial",
    "children-spine": "spina bifida baby back swelling নবজাতক শিশু",
    "thoracic": "middle back pain পিঠের মাঝখানে ব্যথা",
    "overview": "",
    "pituitary": "pituitary vision loss চোখে কম দেখা hormone endoscopic nose নাক দিয়ে",
    "meningioma": "meningioma মেনিনজিওমা brain tumor",
    "glioma": "glioma গ্লায়োমা brain tumor seizure খিঁচুনি",
    "cp-angle": "acoustic neuroma hearing loss কানে কম শোনা মাথা ঘোরা vestibular schwannoma",
    "skull-base": "eye bulging orbit চোখের পেছনে টিউমার chordoma",
    "children-posterior-fossa": "child brain tumor শিশুর ব্রেইন টিউমার medulloblastoma vomiting",
    "ventricular-cavernoma": "cavernoma colloid cyst ক্যাভারনোমা",
    "metastasis": "cancer spread ক্যান্সার",
    "hydrocephalus": "water on brain mathay pani joma মাথায় পানি জমা জলমাথা shunt শান্ট ETV NPH শিশুর মাথা বড়",
    "chiari": "chiari কিয়ারি",
    "aneurysm": "aneurysm bleeding brain hemorrhage stroke মস্তিষ্কে রক্তক্ষরণ হঠাৎ তীব্র মাথাব্যথা ব্রেন স্ট্রোক",
    "avm": "avm bleeding seizure",
    "bypass": "brain bypass বাইপাস moyamoya",
    "carotid": "carotid stroke prevention tia স্ট্রোক",
    "spinal-cord-tumors": "spinal cord tumor schwannoma মেরুদণ্ডে টিউমার",
    "bone-tumors": "chordoma tailbone pain",
    "spine-metastasis": "myeloma cancer spine",
    "potts": "spinal tb tuberculosis যক্ষ্মা টিবি pott hump কুঁজ",
    "epidural-abscess": "abscess pus fever পুঁজ",
    "head-injury": "head injury accident blood clot মাথায় আঘাত রক্ত জমাট subdural",
    "cranioplasty": "skull repair খুলি",
    "trigeminal-neuralgia": "face pain electric shock মুখে বিদ্যুতের মতো ব্যথা মুখে ব্যথা tooth pain mvd",
}
def conditions():
    out = []
    for s in SERVICES:
        for sec in s["sections"]:
            out.append({"en": re.sub(r"\s*\(.*?\)", "", sec["h2"]).split(":")[0].strip(), "bn": sec["bn"], "alt": ALIASES.get(sec["id"], "") + " " + " ".join(l for l, _ in sec["items"]),
                        "url": f'{s["slug"]}.html#{sec["id"]}', "page": s["name"]})
    return out

# ------------------------------------------------------------------ write
def write(name, content):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(content)

def page_images(html_text):
    """Real images a built page shows (largest optimized copy), for the image sitemap."""
    out = []
    for m in re.finditer(r'<img [^>]*?(?:data-full|src)="assets/img/([^"]+)"[^>]*>', html_text):
        tag, f = m.group(0), m.group(1)
        if "data-full=" in tag: f = re.search(r'data-full="assets/img/([^"]+)"', tag).group(1)
        if "logo" in f or f.endswith(".svg") or not os.path.isfile(os.path.join(ROOT, "assets", "img", f)): continue
        alt = re.search(r'alt="([^"]*)"', tag)
        if f not in [x for x, _ in out]: out.append((f, html.unescape(alt.group(1)) if alt else ""))
    return out

HTACCESS = r"""# Dr. Zico website: rules for Hostinger (LiteSpeed / Apache). Generated by _build/build.py.
Options -MultiViews -Indexes
DirectoryIndex index.html
RewriteEngine On

# Old addresses with .html go to the clean address (301): /about.html -> /about, /index.html -> /
RewriteCond %{THE_REQUEST} \s/+index\.html[\s?] [NC]
RewriteRule ^ / [R=301,L]
RewriteCond %{THE_REQUEST} \s/+(.+?)\.html[\s?] [NC]
RewriteRule ^ /%1 [R=301,L,NE]

# A trailing slash goes to the address without it (keeps image and CSS paths working): /about/ -> /about
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.+)/$ /$1 [R=301,L]

# Clean address is served from the .html file: /about -> about.html
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^(.+?)/?$ $1.html [L]

# NOT INDEXED YET: Google is told not to index the site until launch.
# At launch, delete the 3 lines below (IfModule ... /IfModule), rebuild and push.
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow"
</IfModule>

# Hide build tools and notes from visitors
RewriteRule ^(_build|fb-feed-worker)(/|$) - [F,L]
RewriteRule ^[^/]+\.md$ - [F,L]

# Browser cache: CSS/JS carry ?v= versions, so they can be cached for a year; images for a week
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 0 seconds"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType text/javascript "access plus 1 year"
  ExpiresByType image/webp "access plus 7 days"
  ExpiresByType image/jpeg "access plus 7 days"
  ExpiresByType image/png "access plus 7 days"
  ExpiresByType image/svg+xml "access plus 7 days"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType image/x-icon "access plus 7 days"
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript application/json image/svg+xml application/xml
</IfModule>
"""

def main():
    make_og_image()
    pages = {"index.html": page_home(), "services.html": page_services(), "about.html": page_about(),
             "appointment.html": page_appointment(), "gallery.html": page_gallery(), "faq.html": page_faq(), "blog.html": page_blog(),
             "blog-komor-byatha-kon-doctor.html": page_article()}
    for s in SERVICES:
        pages[s["slug"] + ".html"] = page_service(s)
    os.makedirs(os.path.join(ROOT, "assets/js"), exist_ok=True)
    write("assets/js/conditions.js", "/* generated by _build/build.py */\nwindow.DZ_CONDITIONS = " + json.dumps(conditions(), ensure_ascii=False, indent=1) + ";\n")
    # Cache busting: every CSS/JS link gets ?v=<file hash>, so after a change all browsers load the new file
    # instead of an old cached copy (an old cached style.css is what broke the Spine page layout).
    def versioned(c):
        for a in ("assets/css/style.css", "assets/js/conditions.js", "assets/js/main.js", "assets/js/fb-feed.js"):
            with open(os.path.join(ROOT, a), "rb") as fh:
                c = c.replace(f'"{a}"', f'"{a}?v={hashlib.md5(fh.read()).hexdigest()[:10]}"')
        return c
    # Clean URLs: links, canonical, schema and sitemap use /about instead of /about.html.
    # Netlify serves about.html for /about automatically; the .html files stay as they are.
    names = [n[:-5] for n in pages if n != "index.html"]
    def clean_urls(c):
        for n in names:
            c = re.sub(r'(href=")' + re.escape(n) + r'\.html(?=["?#])', r"\g<1>" + n, c)
            c = c.replace(f"{SITE_URL}/{n}.html", f"{SITE_URL}/{n}")
        c = re.sub(r'href="index\.html(?=["?#])', 'href="/', c)
        return c.replace(f"{SITE_URL}/index.html", f"{SITE_URL}/")
    for n, c in pages.items():
        assert "\u2014" not in c, f"em dash in {n}"
        pages[n] = c = clean_urls(versioned(c))
        write(n, c)
    def url_entry(n, c):
        imgs = "".join(f"<image:image><image:loc>{SITE_URL}/assets/img/{f}</image:loc></image:image>" for f, _ in page_images(c)[:1000])
        return f"<url><loc>{SITE_URL}/{'' if n == 'index.html' else n[:-5]}</loc><lastmod>{LAST_REVIEWED}</lastmod>{imgs}</url>"
    urls = "".join(url_entry(n, c) for n, c in pages.items())
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{urls}</urlset>\n')
    # Hostinger (LiteSpeed/Apache) rules: clean URLs, https, cache. See HTACCESS below.
    write(".htaccess", HTACCESS)
    IMAGES.append(("All pages (social share)", "og-image.jpg", "1200x630", "Social share image", "Shown when the site is shared on Facebook/WhatsApp: portrait + name + Neurosurgeon"))
    rows = "\n".join(f"| {pg} | `assets/img/{f}` | {sz} | {lb} | {d} |" for pg, f, sz, lb, d in IMAGES)
    write("IMAGES.md", "# Image list\n\nSave each photo in `assets/img/` with exactly this file name. It replaces the placeholder automatically, no rebuild needed. Use JPG or WebP, compressed under about 300 KB.\n\nFolders: `assets/img/before-after/` holds the before/after scans, `assets/img/services/<service>/` holds every photo for that service page (one folder per service), `assets/img/operating-theatre/` the OT photos. Patient photos are grouped in `assets/img/happy-patient/`. Their order, source filenames, dimensions and alt text are in `_build/happy_patients.json`; they appear in the Home and Gallery patient carousels.\n\n| Page | File | Size (px) | What | What to shoot or make |\n|---|---|---|---|---|\n" + rows + f"\n\nTotal: {len(IMAGES)} images.\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"built {len(pages)} pages, total cases {ALL_TOTAL}")

if __name__ == "__main__":
    main()
