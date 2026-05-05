#!/usr/bin/env python3
"""Validate companies.csv for duplicate tickers and other data integrity issues."""

import sys

from .company_data import (
    CSV_PATH,
    FIELDNAMES,
    normalize_name,
    normalize_ticker,
    parse_price,
    read_companies,
)


def find_duplicate_tickers(path=CSV_PATH):
    """Return a dict of {ticker: [row_numbers]} for any ticker appearing more than once."""
    seen = {}
    _, rows = read_companies(path)
    for i, row in enumerate(rows, start=2):  # row 1 is header
        ticker = normalize_ticker(row["ticker"])
        seen.setdefault(ticker, []).append(i)
    return {t: rows for t, rows in seen.items() if len(rows) > 1}


def find_duplicate_names(path=CSV_PATH):
    """Return likely duplicate company names after light legal-suffix normalization."""
    seen = {}
    _, rows = read_companies(path)
    for i, row in enumerate(rows, start=2):
        name = normalize_name(row["name"])
        if name:
            seen.setdefault(name, []).append(i)
    return {name: rows for name, rows in seen.items() if len(rows) > 1}


def validate(path=CSV_PATH):
    """Run all validations. Returns True if valid, False otherwise."""
    errors = []
    fieldnames, rows = read_companies(path)

    if fieldnames != FIELDNAMES:
        errors.append(f"CSV header must be exactly: {FIELDNAMES}")

    dupes = find_duplicate_tickers(path)
    for ticker, ticker_rows in dupes.items():
        errors.append(f"Duplicate ticker '{ticker}' on rows: {ticker_rows}")

    duplicate_names = find_duplicate_names(path)
    for name, name_rows in duplicate_names.items():
        errors.append(f"Possible duplicate company name '{name}' on rows: {name_rows}")

    for i, row in enumerate(rows, start=2):
        missing = [field for field in FIELDNAMES if not row.get(field, "").strip()]
        if missing:
            errors.append(f"Row {i} has empty required fields: {missing}")
            continue

        try:
            pre_price = parse_price(row["price_prechatgpt"])
            current_price = parse_price(row["price_now"])
            change = float(row["change_percentage"])
        except ValueError as exc:
            errors.append(f"Row {i} has invalid numeric price/change data: {exc}")
            continue

        if pre_price <= 0:
            errors.append(f"Row {i} has non-positive pre-ChatGPT price")
            continue
        if current_price < 0:
            errors.append(f"Row {i} has negative current price")

        expected_change = (current_price - pre_price) / pre_price
        # Current prices are stored to two decimals, while yfinance-derived
        # change percentages may have been calculated from the unrounded close.
        rounding_tolerance = max(0.001, 0.005 / pre_price)
        if abs(change - expected_change) > rounding_tolerance:
            errors.append(
                f"Row {i} change_percentage {change} does not match prices "
                f"({expected_change})"
            )

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
