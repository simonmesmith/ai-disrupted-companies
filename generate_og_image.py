#!/usr/bin/env python3
"""Generate a social sharing (Open Graph) image for the AI Disruption Index."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUTPUT_PATH = ROOT / "docs" / "og-image.png"

# Image dimensions (standard OG image size)
WIDTH, HEIGHT = 1200, 630

# Colors matching the site's dark theme
BG = (10, 10, 10)  # #0a0a0a
RED = (220, 38, 38)  # #dc2626
RED_GLOW = (239, 68, 68)  # #ef4444
TEXT = (240, 240, 240)  # #f0f0f0
TEXT_DIM = (136, 136, 136)  # #888888
TEXT_MUTED = (85, 85, 85)  # #555555

# Font paths (DejaVu is available on Ubuntu CI and most Linux systems)
_DEJAVU_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_SANS_BOLD = _DEJAVU_DIR / "DejaVuSans-Bold.ttf"
FONT_MONO_BOLD = _DEJAVU_DIR / "DejaVuSansMono-Bold.ttf"
FONT_SANS = _DEJAVU_DIR / "DejaVuSans.ttf"


def _load_font(path, size):
    """Load a TrueType font, falling back to Pillow's default."""
    try:
        return ImageFont.truetype(str(path), size)
    except (OSError, IOError):
        return ImageFont.load_default(size=size)


def _draw_centered_text(draw, y, text, font, fill):
    """Draw text horizontally centered at the given y coordinate."""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)


def _draw_glow(img, center_y):
    """Draw a subtle red radial glow behind the index value."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = WIDTH // 2
    # Draw concentric ellipses with decreasing opacity
    for i in range(80, 0, -1):
        rx = i * 4
        ry = i * 2
        alpha = max(1, int(12 * (1 - i / 80)))
        draw.ellipse(
            (cx - rx, center_y - ry, cx + rx, center_y + ry),
            fill=(220, 38, 38, alpha),
        )
    # Composite onto the main image
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))


def generate(payload):
    """Generate the OG image from the data payload."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    index_str = f"${payload['index_value']:.2f}"
    count = payload["company_count"]
    date_str = payload["price_date"]

    # Load fonts at various sizes
    font_label = _load_font(FONT_SANS_BOLD, 28)
    font_index = _load_font(FONT_MONO_BOLD, 120)
    font_subtitle = _load_font(FONT_SANS, 28)
    font_stats = _load_font(FONT_SANS, 22)
    font_url = _load_font(FONT_SANS, 18)

    # Draw red radial glow behind index value area
    _draw_glow(img, 260)
    # Re-create draw after paste
    draw = ImageDraw.Draw(img)

    # "AI DISRUPTION INDEX" label
    _draw_centered_text(draw, 120, "AI DISRUPTION INDEX", font_label, RED)

    # Large index value (e.g. "$0.35")
    _draw_centered_text(draw, 190, index_str, font_index, RED_GLOW)

    # "from $1.00 invested"
    _draw_centered_text(draw, 330, "from $1.00 invested", font_subtitle, TEXT_DIM)

    # Thin red separator line
    line_y = 400
    line_margin = 200
    draw.line(
        [(line_margin, line_y), (WIDTH - line_margin, line_y)], fill=RED, width=1
    )

    # Stats line: "47 companies tracked  ·  March 24, 2026"
    stats_text = f"{count} companies tracked  \u00b7  {date_str}"
    _draw_centered_text(draw, 430, stats_text, font_stats, TEXT_DIM)

    # URL at bottom
    _draw_centered_text(
        draw, 500, "www.simonsmith.ca/ai-disrupted-companies", font_url, TEXT_MUTED
    )

    # Worst-hit company callout
    companies = payload.get("companies", [])
    if companies:
        worst = min(companies, key=lambda c: c["change_percentage"])
        worst_text = (
            f"Worst hit: {worst['name']} ({worst['ticker']}) "
            f"{worst['change_percentage']:+.0%}"
        )
        font_worst = _load_font(FONT_SANS, 18)
        _draw_centered_text(draw, 465, worst_text, font_worst, TEXT_MUTED)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    # Allow standalone execution for testing
    import json
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            payload = json.load(f)
    else:
        # Minimal test payload
        payload = {
            "index_value": 0.35,
            "company_count": 47,
            "price_date": "March 24, 2026",
            "companies": [
                {
                    "ticker": "CHGG",
                    "name": "Chegg Inc",
                    "change_percentage": -0.98,
                }
            ],
        }
    generate(payload)
