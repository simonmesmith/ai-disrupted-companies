#!/usr/bin/env python3
"""Prepare a deterministic daily Codex research brief.

This does not decide whether a company qualifies. It gathers the repeatable facts
Codex should start from before doing LLM/web research: current CSV coverage,
category balance, candidate leads, and optional yfinance price checks for leads.
"""

import argparse
import re
from datetime import date
from pathlib import Path

from company_data import category_distribution, read_companies, read_typed_companies
from update_prices import fetch_prices

ROOT = Path(__file__).parent
LEADS_PATH = ROOT / "leads.md"
MEMORY_PATH = ROOT / "MEMORY.md"
FAILED_PATH = ROOT / "failed-candidates.md"
STRATEGIES_PATH = ROOT / "search-strategies.md"


LEAD_RE = re.compile(
    r"^- \*\*(?P<ticker>[A-Z0-9.^-]+(?:\.[A-Z]+)?) \((?P<name>[^)]+)\)\*\*"
)


def extract_leads(path=LEADS_PATH):
    """Extract ticker/name pairs from the top-level leads table."""
    if not path.exists():
        return []

    leads = []
    for line in path.read_text().splitlines():
        match = LEAD_RE.match(line.strip())
        if match:
            leads.append(match.groupdict())
    return leads


def thin_categories(rows, limit=3):
    """Return the thinnest categories first."""
    counts = category_distribution(rows)
    return sorted(counts.items(), key=lambda item: (item[1], item[0]))[:limit]


def build_brief(include_prices=False):
    """Return a Markdown brief string for the daily Codex update loop."""
    _, rows = read_companies()
    typed_rows = read_typed_companies()
    leads = extract_leads()
    existing_tickers = {row["ticker"].upper() for row in rows}
    worst = min(typed_rows, key=lambda row: row["change_percentage"])

    prices = {}
    if include_prices and leads:
        prices = fetch_prices([lead["ticker"] for lead in leads])

    lines = [
        f"# Daily AI Disruption Index Brief - {date.today().isoformat()}",
        "",
        "## Deterministic Status",
        f"- Companies in CSV: {len(rows)}",
        f"- Worst current decline: {worst['ticker']} ({worst['change_percentage']:+.1%})",
        "- Thinnest categories: "
        + ", ".join(f"{name} ({count})" for name, count in thin_categories(rows)),
        "",
        "## Lead Queue",
    ]

    if not leads:
        lines.append("- No structured ticker leads found in leads.md.")
    else:
        for lead in leads:
            ticker = lead["ticker"]
            status = "already in CSV" if ticker.upper() in existing_tickers else "not in CSV"
            price_note = ""
            if ticker in prices:
                price_note = f"; latest close {prices[ticker]:.2f}"
            lines.append(f"- {ticker} - {lead['name']} ({status}{price_note})")

    lines.extend(
        [
            "",
            "## Codex Research Loop",
            "1. Start with the lead queue above, then `leads.md`, `failed-candidates.md`, and `search-strategies.md`.",
            "2. Evaluate one candidate at a time with current web evidence and yfinance prices.",
            "3. Stop at 15 candidate evaluations, 5 search approaches, or after the configured failure pattern.",
            "4. Only append a company after checking duplicate ticker and likely duplicate name.",
            "5. Run `uv run python validate_csv.py` and `uv run pytest` after code/data changes.",
            "6. Update MEMORY.md, failed-candidates.md, search-strategies.md, and leads.md before committing.",
            "",
            "## Files To Read First",
            f"- {MEMORY_PATH.name}",
            f"- {LEADS_PATH.name}",
            f"- {FAILED_PATH.name}",
            f"- {STRATEGIES_PATH.name}",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prices",
        action="store_true",
        help="Fetch latest yfinance prices for structured leads.",
    )
    args = parser.parse_args()
    print(build_brief(include_prices=args.prices))


if __name__ == "__main__":
    main()
