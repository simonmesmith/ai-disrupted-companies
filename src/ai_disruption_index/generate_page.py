#!/usr/bin/env python3
"""Generate docs/index.html from companies.csv and template.html."""

import html
import json
from datetime import datetime, timezone
from pathlib import Path

from .company_data import (
    CSV_PATH,
    compute_group_stats,
    compute_index,
    parse_price,
    read_typed_companies,
)

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "docs" / "index.html"


def read_companies():
    """Read companies.csv and return list of dicts with numeric fields parsed."""
    return read_typed_companies(CSV_PATH)


def build_payload(companies):
    """Build the complete JSON data payload for the template."""
    active_companies = [c for c in companies if c["change_percentage"] < 0]
    recovered_companies = [c for c in companies if c["change_percentage"] >= 0]
    index_val = compute_index(active_companies)
    now = datetime.now(timezone.utc)

    latest = active_companies[-1] if active_companies else None

    def serialize_company(company):
        return {
            "ticker": company["ticker"],
            "name": company["name"],
            "category": company["category"],
            "subcategory": company["subcategory"],
            "description": company["description"],
            "disruption": company["disruption"],
            "price_prechatgpt": company["price_prechatgpt"],
            "price_now": company["price_now"],
            "change_percentage": round(company["change_percentage"], 6),
        }

    return {
        "generated_at": now.isoformat(),
        "price_date": now.strftime("%B %d, %Y"),
        "index_value": round(index_val, 4),
        "company_count": len(active_companies),
        "recovered_count": len(recovered_companies),
        "tracked_company_count": len(companies),
        "latest_company": serialize_company(latest) if latest else None,
        "companies": [serialize_company(c) for c in active_companies],
        "recovered_companies": [
            serialize_company(c) for c in recovered_companies
        ],
        "categories": compute_group_stats(active_companies, "category"),
        "subcategories": compute_group_stats(active_companies, "subcategory"),
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
        f"$1.00 invested across {count} active AI-disrupted public companies "
        f"on Nov 29, 2022 would be worth {index_str} today. "
        f"Membership is based on each stock's latest available close."
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

    from .generate_og_image import generate as generate_og_image

    generate_og_image(payload)


if __name__ == "__main__":
    main()
