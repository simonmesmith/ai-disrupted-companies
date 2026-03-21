# AI Loser Stocks

**One-liner:** Find publicly traded companies whose stock crashed below their pre-ChatGPT price due to AI disruption, and track them in a master list.

## Git Workflow

Always commit and push to the **`main`** branch. Never use `master`.

## What This Task Does

This folder tracks publicly traded companies whose stock price has fallen below its November 29, 2022 close (the day before ChatGPT launched) because AI is disrupting their core business. The master list lives in `companies.csv` (currently 49 companies across 30+ categories). When asked to "find a new one," the AI should:

1. Read `companies.csv` to see what's already covered and which categories are saturated.
2. Brainstorm candidates from underrepresented categories.
3. Verify the stock price decline using `yfinance` in Python (the stock MUST trade below its Nov 29, 2022 close).
4. Research the AI impact angle via web search — confirm the decline is meaningfully tied to AI disruption, not just macro or unrelated issues.
5. Append the new row to `companies.csv` and report findings in chat.
6. Include the verbatim CSV row in a code block so Simon can paste it into his Google Sheet.

Optionally, the AI can generate a trading card image, pull historical revenue data, or produce reports — but only when explicitly asked.

---

## Folder Structure

```
├── companies.csv           # Master list (Ticker,Name,Category,Description,Impact)
├── generate_card.py        # Trading card image generator
├── CLAUDE.md               # This file
├── cards/                  # Generated trading card PNGs ({TICKER}_card.png)
└── reports/                # Revenue reports, analyses, data exports (date-prefixed)
```

---

## Finding New Companies

### Stock Price Verification

Use `yfinance` — it's installed, fast, and reliable. Don't bother with web scraping.

```python
import yfinance as yf
stock = yf.Ticker('TICKER')
hist = stock.history(start='2022-11-28', end='2022-11-30')
nov_price = hist['Close'].iloc[-1]
current_price = stock.history(period='5d')['Close'].iloc[-1]
```

### Category Saturation (as of March 2026)

Well-covered (3+ entries): staffing/workforce (4), advertising/marketing (4), BPO/CX (3). Underrepresented areas to explore: fintech, healthcare IT, legal tech, traditional SaaS, data/analytics, content/media, real estate tech, cybersecurity, insurance tech.

### Gotchas

- **Reverse stock splits** distort yfinance's adjusted data (e.g., LivePerson had a 1:15 split). Always check.
- **Delisted/acquired tickers** — verify the ticker is still active (e.g., ZoomInfo went private, Perficient was acquired).
- **CSV format** — standard comma-delimited with double-quoted fields containing commas. Use the Edit tool to append rows.

### Output Format

After adding the row, include the verbatim CSV line in a code block for easy copy-paste into Simon's Google Sheet.

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
    category="Education Technology",
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

Card space is limited. Do NOT paste raw `Description` or `Impact` fields from `companies.csv` — they're too long. Write short, punchy versions:

- **`what_they_do`** — One sentence, 10–20 words. Aim for 1–2 lines on the card.
- **`ai_impact`** — One to two sentences, 15–30 words. Max 4 lines in the callout box.

### Category Colors & Logos

- Colors are in the `CATEGORY_COLORS` dict. Unknown categories fall back to indigo (`#6366F1`). Add entries for new categories if you want a specific color — pick medium-bright saturated hues.
- Long category names may need an abbreviation in the `CATEGORY_SHORT` dict.
- `fetch_logo(ticker)` uses the `DOMAIN_MAP` dict. Missing entries just skip the logo (the glitched ticker is the hero visual).

### Output

Cards go in `cards/` as `{TICKER}_card.png`. Reports go in `reports/` with a `YYYY-MM-DD_` prefix.

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

These tickers won't be in EDGAR: LON:RWS, LON:WPP, AMS:WKL, TEP, PUBGY, RCRUY, RELX. Use `yfinance` annual data as fallback:

```python
yf_map = {
    'LON:RWS': 'RWS.L', 'LON:WPP': 'WPP.L', 'AMS:WKL': 'WKL.AS',
    'TEP': 'TEP.L', 'PUBGY': 'PUB.PA', 'RCRUY': '6098.T', 'RELX': 'RELX.L',
}
```

Mark these as "Annual" with local currency (GBP/EUR/JPY) in the Note column.

### Foreign Private Issuers (FVRR, DAVA)

Check SEC EDGAR first (may use non-standard tags), then fall back to web search for press releases.

### Revenue CSV Format

`reports/revenue-comparison-*.csv` columns: `Ticker, Pre-ChatGPT Quarter Date, Pre-ChatGPT Quarter Revenue, Most Recent Quarter Date, Most Recent Quarter Revenue, Revenue Change ($), Revenue Change (%), Note`

### Data Caveats

- **CNXC** — revenue jump is mostly from the Webhelp merger, not organic growth.
- **RCRUY** — revenue in JPY (trillions), not directly comparable to USD.
- **DAVA** — fiscal year starts July, so "Q3 2022" = their Q1 FY2023.
- **IPG** — CIK 49826 (not in standard ticker map).
