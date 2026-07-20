# AI Disruption Index

Tracking publicly traded companies whose stock price has fallen below its November 29, 2022 close — the day before ChatGPT launched — because AI is disrupting their core business.

The active index is recalculated after each price refresh and contains only companies whose latest available close is below that baseline (`change_percentage < 0`). Historical members at or above the baseline remain in `companies.csv`, continue to receive daily price updates, and appear in the dashboard's **Recovered** view. If a recovered company falls below the baseline again, it automatically returns to the active index on the next refresh.

## The Index

The interactive dashboard is available at **[simonsmith.ca/ai-disrupted-companies](https://simonsmith.ca/ai-disrupted-companies)**.

## How It Works

1. A new AI-disrupted company is researched and added to `companies.csv`
2. A GitHub Actions workflow updates every historical member's stock price on pushes and every weekday after market close, then deploys the dashboard
3. Codex research sessions use the memory files plus deterministic checks to decide whether any new company qualifies

## Data

All data lives in `companies.csv` with the following fields:

- **ticker** — yfinance-compatible symbol
- **name** — company name
- **category / subcategory** — classification for trend analysis
- **description** — what the company does
- **disruption** — how AI is disrupting them
- **price_prechatgpt** — closing price on November 29, 2022
- **price_now** — most recent closing price
- **change_percentage** — change from the pre-ChatGPT price; negative rows are active and non-negative rows are recovered

The headline index value is an equal-weighted mean of `price_now / price_prechatgpt` for active companies only. The active count, category and subcategory statistics, and default company grid use the same active membership. Membership is a current price screen based on the latest available close, not a claim that a recovered company's original disruption thesis has been reversed.

## Development

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras
uv run pytest
uv run ai-index-update-prices
uv run ai-index-generate-page
```

For the daily Codex research loop:

```bash
git status --short --branch
git pull --rebase origin main       # sync before reading CSV/memory
uv run ai-index-daily-brief          # deterministic brief from CSV + memory
uv run ai-index-daily-brief --prices # also checks latest yfinance prices for leads
```

The daily GitHub Action handles price refresh and deployment. Use Codex for the LLM-heavy part: researching one candidate at a time, proving the AI disruption thesis, and updating `companies.csv` plus the memory files when a candidate qualifies.

Before pushing a Codex research commit, run `git pull --rebase origin main` again. The scheduled price-refresh workflow can commit while research is in progress; if `companies.csv` conflicts, keep the remote refreshed existing rows and reapply only the new company row.
