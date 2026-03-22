# Trading Card Generator (`generate_card.py`)

> Card generation is **optional** — only when Simon explicitly asks.

Creates 1080×1350 portrait PNGs (4:5 ratio) as "trading cards" with a giant glitched ticker symbol whose distortion scales with the stock decline.

## Usage

```python
from generate_card import generate_card, fetch_logo

logo = fetch_logo("CHGG")  # Returns PIL Image or None

generate_card(
    ticker="CHGG",
    name="Chegg Inc",
    category="Education",
    what_they_do="Online homework help and textbook rental platform used by millions of college students.",
    ai_impact="ChatGPT replaced Chegg's core homework help product almost overnight, causing 30%+ subscriber losses and a 91% stock collapse.",
    pre_price=14.74,
    current_price=1.35,
    logo_img=logo,
    output_path="cards/CHGG_card.png",
    card_date="2026-03-10",
)
```

## Text Length Guidelines

Card space is limited. Do NOT paste raw `description` or `disruption` fields from `companies.csv` — they're too long. Write short, punchy versions:

- **`what_they_do`** — One sentence, 10–20 words. Aim for 1–2 lines on the card.
- **`ai_impact`** — One to two sentences, 15–30 words. Max 4 lines in the callout box.

## Category Colors & Logos

- Colors are in the `CATEGORY_COLORS` dict. Unknown categories fall back to indigo (`#6366F1`). Add entries for new categories if you want a specific color — pick medium-bright saturated hues.
- Long category names may need an abbreviation in the `CATEGORY_SHORT` dict.
- `fetch_logo(ticker)` uses the `DOMAIN_MAP` dict. Missing entries just skip the logo (the glitched ticker is the hero visual).

## Output

Cards go in `cards/` as `{TICKER}_card.png`.
