"""Build web-sized images from the raw originals.

Usage (from project root):
    python scripts/optimize_images.py <raw_dir> app/static/img

<raw_dir> mirrors the layout of the original WordPress download:
    brand/ icons/ gallery/ boats/ hero/
Outputs JPEG/PNG files sized for the web. Originals are never committed.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

RAW = Path(sys.argv[1])
OUT = Path(sys.argv[2])

NAVY = (11, 27, 63)


def save_jpeg(im, path, max_w, quality):
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size


def main():
    # hero
    for f in (RAW / "hero").glob("*.jpg"):
        save_jpeg(Image.open(f), OUT / "hero" / "hero.jpg", 1920, 80)

    # gallery: full size and thumb, in sorted order, written to a manifest
    names = []
    for f in sorted((RAW / "gallery").glob("*.jpg")):
        stem = f.stem.replace("-scaled", "").replace("-1", "")
        stem = stem.lower().replace("_", "-")
        w, h = save_jpeg(Image.open(f), OUT / "gallery" / f"{stem}.jpg", 1600, 80)
        save_jpeg(Image.open(f), OUT / "gallery" / "thumbs" / f"{stem}.jpg", 640, 76)
        names.append((f.stem, stem, w, h))
    (OUT / "gallery" / "MANIFEST.txt").write_text(
        "\n".join(f"{orig} -> {stem}.jpg {w}x{h}" for orig, stem, w, h in names) + "\n"
    )

    # boats
    for i, f in enumerate(sorted((RAW / "boats").glob("b*.*")), start=1):
        save_jpeg(Image.open(f), OUT / "boats" / f"boat-{i}.jpg", 900, 80)

    # icons: small PNGs, keep alpha
    for f in (RAW / "icons").glob("*.png"):
        im = Image.open(f).convert("RGBA")
        im.thumbnail((160, 160), Image.LANCZOS)
        dest = OUT / "icons" / f.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "PNG", optimize=True)

    # brand: logo (white on transparent), favicon set, social image
    logo = Image.open(RAW / "brand" / "101-Marina-Logo-2.png").convert("RGBA")
    dest = OUT / "brand"
    dest.mkdir(parents=True, exist_ok=True)
    big = logo.copy()
    big.thumbnail((600, 600), Image.LANCZOS)
    big.save(dest / "logo.png", "PNG", optimize=True)
    small = logo.copy()
    small.thumbnail((200, 200), Image.LANCZOS)
    small.save(dest / "logo-small.png", "PNG", optimize=True)
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")):
        tile = Image.new("RGBA", (size, size), NAVY + (255,))
        inner = logo.copy()
        inner.thumbnail((int(size * 0.92), int(size * 0.92)), Image.LANCZOS)
        tile.alpha_composite(inner, ((size - inner.width) // 2, (size - inner.height) // 2))
        tile.convert("RGB").save(dest / name, "PNG", optimize=True)
    # 1200x630 social card: navy field, logo centered
    card = Image.new("RGB", (1200, 630), NAVY)
    inner = logo.copy()
    inner.thumbnail((560, 560), Image.LANCZOS)
    card.paste(inner, ((1200 - inner.width) // 2, (630 - inner.height) // 2), inner)
    card.save(dest / "og-card.jpg", "JPEG", quality=88, optimize=True)


if __name__ == "__main__":
    main()
