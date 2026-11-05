# Image optimizer used by build.py.
# You keep the original photos in assets/img/<folder>/ as before. On every build, each photo used on
# the site gets small WebP copies in assets/img/_opt/ (same folder structure), and the pages load
# those through srcset, so a phone downloads a small file and a desktop a larger one.
# Copies are only re-made when the original is newer. Never edit files in _opt by hand.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
OPT = "_opt"
WIDTHS = (480, 960, 1600)
QUALITY = 78

try:
    from PIL import Image
except ImportError:  # without Pillow the site still builds, using the original files
    Image = None

def _opt_name(file, w):
    base, _ = os.path.splitext(file)
    return f"{OPT}/{base}-{w}.webp"

def variants(file):
    """[(path inside assets/img, width)] for one original image, smallest first. Empty if not possible."""
    src = os.path.join(IMG, file)
    if Image is None or not os.path.isfile(src) or file.endswith(".svg"):
        return []
    with Image.open(src) as im:
        ow, oh = im.size
        widths = [w for w in WIDTHS if w < ow] + [min(ow, WIDTHS[-1])]
        widths = sorted(set(widths))
        out = []
        for w in widths:
            name = _opt_name(file, w)
            dst = os.path.join(IMG, name)
            if not (os.path.isfile(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                h = round(oh * w / ow)
                frame = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                frame = frame.resize((w, h), Image.LANCZOS) if w != ow else frame
                frame.save(dst, "WEBP", quality=QUALITY, method=5)
            out.append((name, w))
    return out

def img_attrs(file, sizes, largest=1600):
    """src/srcset/sizes/data-full attributes for an original image (falls back to the original)."""
    v = variants(file)
    if not v:
        return f'src="assets/img/{file}"'
    usable = [x for x in v if x[1] <= largest] or v[:1]
    src = usable[-1][0] if len(usable) == 1 else next((n for n, w in usable if w >= 960), usable[-1][0])
    srcset = ", ".join(f"assets/img/{n} {w}w" for n, w in v)
    return f'src="assets/img/{src}" srcset="{srcset}" sizes="{sizes}" data-full="assets/img/{v[-1][0]}"'

def largest(file):
    v = variants(file)
    return v[-1][0] if v else file

def make_og_image():
    """assets/img/og-image.jpg (1200 x 630): logo on the left, portrait on the right. Made once; replace it freely."""
    dst = os.path.join(IMG, "og-image.jpg")
    if Image is None or os.path.isfile(dst):
        return
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (238, 245, 248))
    band = Image.new("RGB", (W, 10), (10, 58, 99)); bg.paste(band, (0, H - 10))
    with Image.open(os.path.join(IMG, "logo.png")) as logo:
        logo = logo.convert("RGBA"); lw = 560; logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
        bg.paste(logo, (70, (H - logo.height) // 2 - 10), logo)
    with Image.open(os.path.join(IMG, "dr-zico-portrait.png")) as p:
        p = p.convert("RGBA"); ph = H - 10; p = p.resize((round(p.width * ph / p.height), ph), Image.LANCZOS)
        bg.paste(p, (W - p.width - 30, H - 10 - ph), p)
    bg.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
