# AI Disruption Index

**One-liner:** Find publicly traded companies whose stock crashed below their pre-ChatGPT price due to AI disruption, and track them in a master list.

## Git Workflow

Always commit and push to the **`main`** branch. Never use `master`.

## What This Project Does

This repo tracks publicly traded companies whose stock price has fallen below its November 29, 2022 close (the day before ChatGPT launched) because AI is disrupting their core business. The master list lives in `companies.csv`. An interactive dashboard is deployed automatically via GitHub Pages.

## When Asked to Find a New Company

The AI's job is simple:

1. **Find a new company** — Read `companies.csv` to see what's covered, brainstorm candidates (especially in underrepresented categories), verify the stock price decline, research the AI angle.
2. **Add to CSV** — Append the new row with all fields (see CSV schema below).
3. **Commit and push** — That's it. GitHub Actions handles price updates and site deployment automatically.

Do not run `update_prices.py` or `generate_page.py` manually unless explicitly asked — the automation handles it.

---

## Environment Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management. To set up:

```bash
uv sync --all-extras    # Creates .venv and installs all deps including dev
```

All Python commands should use `uv run` to ensure the venv is active:

```bash
uv run pytest
uv run python update_prices.py
uv run python generate_page.py
```

## Folder Structure

```
├── companies.csv              # Master list (source of truth)
├── update_prices.py           # Bulk price updater (yfinance)
├── test_update_prices.py      # Tests for price updater
├── generate_page.py           # Static site generator
├── test_generate_page.py      # Tests for page generator
├── template.html              # HTML/CSS/JS template for the site
├── pyproject.toml             # Python dependencies (uv)
├── CLAUDE.md                  # This file
├── README.md                  # Public-facing project description
├── docs/                      # GitHub Pages output (index.html is generated, not committed)
└── .github/workflows/         # GitHub Actions: price updates + site deployment
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
| `price_now` | Most recent closing price (updated automatically) |
| `change_percentage` | `(price_now - price_prechatgpt) / price_prechatgpt` (updated automatically) |

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

## Automation

### GitHub Actions (`.github/workflows/update-and-generate.yml`)

Triggered on push to `main` when `companies.csv`, `generate_page.py`, or `template.html` change:

1. **update-prices job** — refreshes all prices via yfinance, commits updated CSV
2. **deploy-page job** — generates `docs/index.html` and deploys directly to GitHub Pages via `actions/deploy-pages`

The generated `docs/index.html` is **not committed** — it's built and deployed on the fly. Can also be triggered manually via `workflow_dispatch`.

### GitHub Pages

The site is deployed using the GitHub Pages action (not served from a committed file). Configure in repo Settings > Pages > Source: "GitHub Actions".

### Running Locally

```bash
uv run python update_prices.py     # Refresh prices
uv run python generate_page.py     # Generate docs/index.html locally
uv run pytest                       # Run all tests
```
