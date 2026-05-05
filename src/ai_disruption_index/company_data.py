#!/usr/bin/env python3
"""Shared data helpers for the AI Disruption Index."""

import csv
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "companies.csv"

FIELDNAMES = [
    "ticker",
    "name",
    "category",
    "subcategory",
    "description",
    "disruption",
    "price_prechatgpt",
    "price_now",
    "change_percentage",
]


def parse_price(value):
    """Parse a price string, stripping currency symbols, commas, and whitespace."""
    return float(str(value).replace("$", "").replace(",", "").strip())


def normalize_ticker(value):
    """Normalize a ticker for duplicate detection."""
    return str(value).strip().upper()


def normalize_name(value):
    """Normalize company names enough to catch likely duplicate rows."""
    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    words = [
        word
        for word in normalized.split()
        if word
        not in {
            "inc",
            "incorporated",
            "corp",
            "corporation",
            "company",
            "co",
            "ltd",
            "limited",
            "plc",
            "group",
            "holdings",
            "holding",
            "sa",
            "ag",
            "nv",
        }
    ]
    return " ".join(words)


def read_companies(path=CSV_PATH):
    """Read a companies CSV and return (fieldnames, rows)."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def read_typed_companies(path=CSV_PATH):
    """Read companies and parse numeric price fields."""
    _, rows = read_companies(path)
    typed_rows = []
    for row in rows:
        parsed = dict(row)
        parsed["price_prechatgpt"] = parse_price(row["price_prechatgpt"])
        parsed["price_now"] = parse_price(row["price_now"])
        parsed["change_percentage"] = float(row["change_percentage"])
        typed_rows.append(parsed)
    return typed_rows


def write_companies(fieldnames, rows, path=CSV_PATH):
    """Write rows back to companies.csv with a trailing newline."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def category_distribution(rows):
    """Return a category -> count mapping sorted by descending count."""
    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def company_count(rows):
    return len(rows)


def compute_index(companies):
    """Compute equal-weighted index value: mean of price_now / price_prechatgpt."""
    ratios = [c["price_now"] / c["price_prechatgpt"] for c in companies]
    return statistics.mean(ratios) if ratios else 0.0


def compute_group_stats(companies, key):
    """Compute aggregate stats grouped by a field."""
    groups = {}
    for company in companies:
        groups.setdefault(company[key], []).append(company["change_percentage"])
    return [
        {
            "name": name,
            "count": len(changes),
            "avg_change": statistics.mean(changes),
        }
        for name, changes in groups.items()
    ]
