# AI Disruption Index

Tracking publicly traded companies whose stock price has fallen below its November 29, 2022 close — the day before ChatGPT launched — because AI is disrupting their core business.

## The Index

If you had invested $1.00 equally across all companies in this index on November 29, 2022, you would have roughly **$0.38** today.

The interactive dashboard is available at **[simonsmith.ca/ai-disrupted-companies](https://simonsmith.ca/ai-disrupted-companies)**.

## How It Works

1. A new AI-disrupted company is researched and added to `companies.csv`
2. A GitHub Actions workflow automatically updates all stock prices and deploys an interactive dashboard

## Data

All data lives in `companies.csv` with the following fields:

- **ticker** — yfinance-compatible symbol
- **name** — company name
- **category / subcategory** — classification for trend analysis
- **description** — what the company does
- **disruption** — how AI is disrupting them
- **price_prechatgpt** — closing price on November 29, 2022
- **price_now** — most recent closing price
- **change_percentage** — decline from pre-ChatGPT price

## Development

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras
uv run pytest
uv run python update_prices.py
uv run python generate_page.py
```
