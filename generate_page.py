#!/usr/bin/env python3
"""Generate docs/index.html from companies.csv and template.html."""

import csv
import html
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "companies.csv"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "docs" / "index.html"


def parse_price(s):
    """Parse a price string, stripping $, commas, and whitespace."""
    return float(s.replace("$", "").replace(",", "").strip())


def read_companies():
    """Read companies.csv and return list of dicts with numeric fields parsed."""
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["price_prechatgpt"] = parse_price(row["price_prechatgpt"])
        row["price_now"] = parse_price(row["price_now"])
        row["change_percentage"] = float(row["change_percentage"])
    return rows


def compute_index(companies):
    """Compute equal-weighted index value: mean of (price_now / price_prechatgpt)."""
    ratios = [c["price_now"] / c["price_prechatgpt"] for c in companies]
    return statistics.mean(ratios)


def compute_group_stats(companies, key):
    """Compute aggregate stats grouped by a field (category or subcategory)."""
    groups = {}
    for c in companies:
        name = c[key]
        if name not in groups:
            groups[name] = []
        groups[name].append(c["change_percentage"])
    return [
        {
            "name": name,
            "count": len(changes),
            "avg_change": statistics.mean(changes),
        }
        for name, changes in groups.items()
    ]


def build_payload(companies):
    """Build the complete JSON data payload for the template."""
    index_val = compute_index(companies)
    now = datetime.now(timezone.utc)

    latest = companies[-1]

    return {
        "generated_at": now.isoformat(),
        "price_date": now.strftime("%B %d, %Y"),
        "index_value": round(index_val, 4),
        "company_count": len(companies),
        "latest_company": {
            "ticker": latest["ticker"],
            "name": latest["name"],
            "category": latest["category"],
            "subcategory": latest["subcategory"],
            "description": latest["description"],
            "disruption": latest["disruption"],
            "price_prechatgpt": latest["price_prechatgpt"],
            "price_now": latest["price_now"],
            "change_percentage": round(latest["change_percentage"], 6),
        },
        "companies": [
            {
                "ticker": c["ticker"],
                "name": c["name"],
                "category": c["category"],
                "subcategory": c["subcategory"],
                "description": c["description"],
                "disruption": c["disruption"],
                "price_prechatgpt": c["price_prechatgpt"],
                "price_now": c["price_now"],
                "change_percentage": round(c["change_percentage"], 6),
            }
            for c in companies
        ],
        "categories": compute_group_stats(companies, "category"),
        "subcategories": compute_group_stats(companies, "subcategory"),
    }


SITE_URL = "https://www.simonsmith.ca/ai-disrupted-companies/"


def generate_html(payload):
    """Read template.html, inject JSON data and meta tags, return complete HTML."""
    template = TEMPLATE_PATH.read_text()
    data_json = json.dumps(payload, ensure_ascii=False)

    index_str = f"${payload['index_value']:.2f}"
    count = payload["company_count"]

    og_title = f"AI Disruption Index \u2014 {index_str} from $1.00"
    meta_desc = (
        f"$1.00 invested across {count} AI-disrupted public companies "
        f"on Nov 29, 2022 would be worth {index_str} today. "
        f"Track the companies being destroyed by AI."
    )
    jsonld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "AI Disruption Index",
            "url": SITE_URL,
            "description": meta_desc,
        }
    )

    result = template.replace("{{ DATA_JSON }}", data_json)
    result = result.replace("{{ OG_TITLE }}", html.escape(og_title))
    result = result.replace("{{ META_DESCRIPTION }}", html.escape(meta_desc))
    result = result.replace("{{ JSONLD }}", jsonld)
    return result


def main():
    companies = read_companies()
    print(f"Read {len(companies)} companies")

    payload = build_payload(companies)
    print(f"Index value: ${payload['index_value']:.2f} (from $1.00)")

    html = generate_html(payload)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)
    print(f"Wrote {OUTPUT_PATH} ({len(html):,} bytes)")

    from generate_og_image import generate as generate_og_image

    generate_og_image(payload)


if __name__ == "__main__":
    main()
