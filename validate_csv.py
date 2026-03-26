#!/usr/bin/env python3
"""Validate companies.csv for duplicate tickers and other data integrity issues."""

import csv
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent / "companies.csv"


def find_duplicate_tickers(path=CSV_PATH):
    """Return a dict of {ticker: [row_numbers]} for any ticker appearing more than once."""
    seen = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 is header
            ticker = row["ticker"].strip().upper()
            seen.setdefault(ticker, []).append(i)
    return {t: rows for t, rows in seen.items() if len(rows) > 1}


def validate(path=CSV_PATH):
    """Run all validations. Returns True if valid, False otherwise."""
    errors = []

    dupes = find_duplicate_tickers(path)
    for ticker, rows in dupes.items():
        errors.append(f"Duplicate ticker '{ticker}' on rows: {rows}")

    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print("Validation passed: no duplicate tickers found.")
    return True


def main():
    sys.exit(0 if validate() else 1)


if __name__ == "__main__":
    main()
