#!/usr/bin/env python3
"""
generate_icons.py — re-render the JB/ brand mark to crisp square PNGs.

Rebuilds the "JB/" logo from the site's Space Grotesk font + brand colours
(instead of upscaling the low-res .ico), then exports it at several padding
variants: the same square canvas each time, with the mark scaled to a
different fraction of the width. Handy for favicons (tight) through to
avatars / og-images (roomy safe-area).

    python tools/generate_icons.py

Edit the CONFIG block to change sizes, colours, padding or corner rounding.
Needs: Pillow (PIL).  No Chrome / network required.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# CONFIG — edit me
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
# JetBrains Mono — same font as the site's top-left "JB/" brand (--font-mono).
FONT_PATH = ROOT / "content" / "fonts" / "JetBrainsMono.woff2"
OUT_DIR   = ROOT / "content" / "images" / "icon"

# One or more square canvas sizes (px). Each variant is rendered at each size.
SIZES = [1024]

# Padding variants: name -> mark width as a fraction of the canvas width.
# 0.75 reproduces the original .ico; smaller = more breathing room.
FRACTIONS = {
    "full":   0.75,   # favicon / tab — mark near-full
    "wide":   0.62,
    "medium": 0.52,   # avatar
    "roomy":  0.42,   # og-image / social safe-area
}

BG_COLOR     = "#0a0d13"   # --bg, matches source square
INK_COLOR    = "#e7ebf1"   # --text, the "JB"
ACCENT_COLOR = "#4da8ff"   # --accent, the "/"
BG_ALPHA     = 255         # 0 = transparent canvas, 255 = solid square

FONT_WEIGHT  = 700         # matches the site brand weight (JetBrains Mono 100..800)
SLASH_GAP    = 0.0         # JetBrains Mono is monospaced — no extra gap needed
CORNER_RADIUS = 0.0        # rounded-corner radius as fraction of canvas (0 = square)
SUPERSAMPLE  = 4           # render at Nx then downscale for smooth edges
# ============================================================


def load_font(px: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(FONT_PATH), px)
    try:
        font.set_variation_by_axes([FONT_WEIGHT])
    except Exception:
        pass  # non-variable build — use default weight
    return font


def measure(font: ImageFont.FreeTypeFont, text: str):
    """Tight pixel bbox (left, top, right, bottom) of text at origin."""
    l, t, r, b = font.getbbox(text)
    return l, t, r, b


def render_mark(size_px: int) -> Image.Image:
    """Render 'JB/' onto a transparent square of side size_px, centred."""
    ss = size_px * SUPERSAMPLE
    img = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Pick a font size so the whole mark's width hits the target fraction.
    # Start from a reference size and scale linearly (bbox width ~ linear in px).
    ref = ss // 2
    font = load_font(ref)
    jb_l, _, jb_r, _ = measure(font, "JB")
    jb_w = jb_r - jb_l
    sl_l, _, sl_r, _ = measure(font, "/")
    sl_w = sl_r - sl_l
    gap = SLASH_GAP * ref
    mark_w = jb_w + gap + sl_w

    # target mark width is applied per-variant later; here render at ref, the
    # caller scales the returned tight-cropped mark. So just draw at ref.
    # Vertical: use combined bbox of the whole string for centring.
    full_l, full_t, full_r, full_b = measure(font, "JB/")

    # draw JB (ink) then / (accent) with a manual gap
    x0 = -jb_l
    baseline_top = -full_t
    draw.text((x0, baseline_top), "JB", font=font, fill=INK_COLOR)
    slash_x = x0 + jb_w + gap - sl_l
    draw.text((slash_x, baseline_top), "/", font=font, fill=ACCENT_COLOR)

    # tight-crop to the actual drawn pixels
    bbox = img.getbbox()
    return img.crop(bbox)


def compose(canvas_px: int, frac: float, mark: Image.Image) -> Image.Image:
    """Place the mark on a square canvas, scaled to `frac` of the width."""
    ss = canvas_px * SUPERSAMPLE
    bg = (*_hex(BG_COLOR), BG_ALPHA)
    canvas = Image.new("RGBA", (ss, ss), bg)

    target_w = int(frac * ss)
    scale = target_w / mark.width
    target_h = max(1, int(mark.height * scale))
    m = mark.resize((target_w, target_h), Image.LANCZOS)

    x = (ss - target_w) // 2
    y = (ss - target_h) // 2
    canvas.alpha_composite(m, (x, y))

    if CORNER_RADIUS > 0:
        canvas = _round_corners(canvas, int(CORNER_RADIUS * ss))

    return canvas.resize((canvas_px, canvas_px), Image.LANCZOS)


def _hex(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _round_corners(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width, img.height], radius, fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    for size_px in SIZES:
        mark = render_mark(size_px)  # tight, supersampled
        for name, frac in FRACTIONS.items():
            icon = compose(size_px, frac, mark)
            out = OUT_DIR / f"icon-{name}-{size_px}.png"
            icon.save(out)
            made.append(out)
    print(f"Wrote {len(made)} icon(s) to {OUT_DIR}:")
    for p in made:
        print("  ", p.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
