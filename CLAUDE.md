# AI Loser Stocks

**One-liner:** Find publicly traded companies whose stock crashed below their pre-ChatGPT price due to AI disruption, and track them in a master list.

## Git Workflow

Always commit and push to the **`main`** branch. Never use `master`.

## What This Task Does

This folder tracks publicly traded companies whose stock price has fallen below its November 29, 2022 close (the day before ChatGPT launched) because AI is disrupting their core business. The master list lives in `companies.csv`.

## Daily Workflow

Each session typically follows this workflow:

1. **Find a new company** — Read `companies.csv` to see what's covered, brainstorm candidates (especially in underrepresented categories), verify the stock price decline, research the AI angle, and add the new row.
2. **Add to CSV** — Append the new row with all fields (see CSV schema below).
3. **Update all prices** — Run `python3 update_prices.py` to refresh `price_now` and `change_percentage` for every company.

Optionally, the AI can generate a trading card image, pull historical revenue data, or produce reports — but only when explicitly asked.

---

## Environment Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management. To set up:

```bash
uv sync --all-extras    # Creates .venv and installs all deps including dev
```

All Python commands should use `uv run` to ensure the venv is active:

```bash
uv run python update_prices.py
uv run pytest test_update_prices.py
```

## Folder Structure

```
├── companies.csv           # Master list
├── update_prices.py        # Bulk price updater (yfinance)
├── test_update_prices.py   # Tests for price updater
├── generate_card.py        # Trading card image generator
├── pyproject.toml          # Python dependencies (uv)
├── CLAUDE.md               # This file
└── cards/                  # Generated trading card PNGs ({TICKER}_card.png)
```

---

## CSV Schema

`companies.csv` columns:

| Column | Description |
|---|---|
| `ticker` | yfinance-compatible ticker symbol (e.g., `CHGG`, `WPP.L`, `WKL.AS`) |
| `name` | Company name |
| `category` | Broad category (see Categories below) |
| `subcategory` | Specific subcategory |
| `description` | What the company does |
| `disruption` | How AI is disrupting them |
| `price_prechatgpt` | Closing price on November 29, 2022 |
| `price_now` | Most recent closing price (updated by `update_prices.py`) |
| `change_percentage` | `(price_now - price_prechatgpt) / price_prechatgpt` |

---

## Categories

Companies are organized into broad categories with specific subcategories:

| Category | Subcategories |
|---|---|
| Business Services | BPO / Contact Centers, IT Services, IT Staffing & Consulting, Staffing & Recruitment, Translation & Localization, Multi-Utility / Network Marketing |
| Software & SaaS | Contact Center Software, Conversational AI, Customer Support, Expense Management, HCM / Payroll, Project Management, Social Media Management, AP Automation / Fintech |
| Content & Media | Stock Media, Content Moderation / AI Data, Creative Software, Online Dating, Online Reviews / Travel |
| Marketing & Advertising | Ad Services / Agencies, Ad Tech, Digital Media / Affiliate |
| Research & Analytics | Data Warehousing, Healthcare Analytics, Market Research, Professional Information, Research / IP Analytics |
| Education | EdTech |
| Freelance Marketplaces | Freelance Platform |
| Legal & Tax | Legal Tech, Tax Preparation |

### Categorization Guidelines

- **Prefer existing categories and subcategories** when a company fits reasonably well.
- **New categories or subcategories are fine** when a company genuinely doesn't fit existing ones — but minimize fragmentation so we can do meaningful trend analysis.
- Subcategories should be **specific enough to be useful** but **broad enough to accumulate multiple entries** over time.

---

## Finding New Companies

### Stock Price Verification

Use `yfinance` — it's installed, fast, and reliable. Tickers must be **yfinance-compatible** (e.g., `WPP.L` not `LON:WPP`, `WKL.AS` not `AMS:WKL`).

```python
import yfinance as yf
stock = yf.Ticker('TICKER')
hist = stock.history(start='2022-11-28', end='2022-11-30')
nov_price = hist['Close'].iloc[-1]
current_price = stock.history(period='1d')['Close'].iloc[-1]
```

### Gotchas

- **Reverse stock splits** distort yfinance's adjusted data (e.g., LivePerson had a 1:15 split). Always check.
- **Delisted/acquired tickers** — verify the ticker is still active (e.g., ZoomInfo went private, Perficient was acquired).
- **CSV format** — standard comma-delimited with double-quoted fields containing commas. Use the Edit tool to append rows.
- **Trailing newline** — before appending a row, verify the file ends with a newline (`\n`). If it doesn't, the new row will be concatenated onto the last existing row. Never use `cat >>` or shell heredocs to append; always use the Edit tool or a Python script that explicitly checks for/adds a trailing newline first.

---

## Updating Prices (`update_prices.py`)

Fetches the last closing price for all tickers in a single bulk `yf.download()` call (avoids rate limiting) and updates `price_now` and `change_percentage`.

```bash
uv run python update_prices.py
```

Run this after adding a new company, or anytime you want to refresh prices. Tests: `uv run pytest test_update_prices.py`

---

## Trading Card Generator (`generate_card.py`)

> Card generation is **optional** — only when Simon explicitly asks.

Creates 1080×1350 portrait PNGs (4:5 ratio) as "trading cards" with a giant glitched ticker symbol whose distortion scales with the stock decline.

### Usage

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

### Text Length Guidelines

Card space is limited. Do NOT paste raw `description` or `disruption` fields from `companies.csv` — they're too long. Write short, punchy versions:

- **`what_they_do`** — One sentence, 10–20 words. Aim for 1–2 lines on the card.
- **`ai_impact`** — One to two sentences, 15–30 words. Max 4 lines in the callout box.

### Category Colors & Logos

- Colors are in the `CATEGORY_COLORS` dict. Unknown categories fall back to indigo (`#6366F1`). Add entries for new categories if you want a specific color — pick medium-bright saturated hues.
- Long category names may need an abbreviation in the `CATEGORY_SHORT` dict.
- `fetch_logo(ticker)` uses the `DOMAIN_MAP` dict. Missing entries just skip the logo (the glitched ticker is the hero visual).

### Output

Cards go in `cards/` as `{TICKER}_card.png`.

---

## Historical Quarterly Revenue

> Only pull revenue data when explicitly asked.

### US-Listed Companies: SEC EDGAR XBRL API

`yfinance` only returns ~7 recent quarters — not enough to reach Q3 2022. Use SEC EDGAR instead:

```python
import requests, time

headers = {'User-Agent': 'YourName your@email.com'}

# 1. Get CIK mapping
cik_resp = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers)
cik_map = {v['ticker']: v['cik_str'] for v in cik_resp.json().values()}

# 2. Pull company facts
cik = cik_map['CHGG']
url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json'
resp = requests.get(url, headers=headers)
facts = resp.json()

# 3. Revenue tags (try in priority order)
REVENUE_TAGS = [
    'RevenueFromContractWithCustomerExcludingAssessedTax',
    'RevenueFromContractWithCustomerIncludingAssessedTax',
    'Revenues',
    'SalesRevenueNet',
    'SalesRevenueServicesNet',
]
# Check: facts['facts']['us-gaap'][tag]['units']['USD']
# For IFRS filers: facts['facts']['ifrs-full']['Revenue']
```

**Critical filtering rules:**
- **Duration ≤120 days** — many XBRL entries are YTD or annual figures, not quarterly.
- **Merge tag transitions** — companies often switched revenue tags around 2018–2020. Check all tags, prioritize higher-priority ones for duplicate periods.
- **Outlier filter** — discard values <0.05× or >20× the median.
- **Form filter** — accept 10-Q, 10-K, 20-F, 10-K/A, 10-Q/A.
- **Rate limiting** — add `time.sleep(0.12)` between requests (10 req/sec max). Include name/email in User-Agent.

### Non-US Companies

Non-US tickers use yfinance-friendly symbols (e.g., `RWS.L`, `WPP.L`, `WKL.AS`, `TEP.L`). These won't be in EDGAR. Use `yfinance` annual data as fallback. Mark these as "Annual" with local currency (GBP/EUR/JPY) in the Note column.

### Foreign Private Issuers (FVRR, DAVA)

Check SEC EDGAR first (may use non-standard tags), then fall back to web search for press releases.

### Data Caveats

- **CNXC** — revenue jump is mostly from the Webhelp merger, not organic growth.
- **DAVA** — fiscal year starts July, so "Q3 2022" = their Q1 FY2023.
