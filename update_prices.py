#!/usr/bin/env python3
"""Update price_now and change_percentage for all companies in companies.csv."""

import csv
import sys
from pathlib import Path

import yfinance as yf

CSV_PATH = Path(__file__).parent / "companies.csv"


def parse_price(s):
    """Parse a price string, stripping $, commas, and whitespace."""
    return float(s.replace("$", "").replace(",", "").strip())


def read_companies(path=CSV_PATH):
    """Read companies.csv and return (fieldnames, rows)."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def fetch_prices(tickers):
    """Fetch last close price for a list of tickers. Returns {ticker: price}."""
    if not tickers:
        return {}
    data = yf.download(tickers, period="1d", progress=False)
    if data.empty:
        return {}
    prices = {}
    if len(tickers) == 1:
        # Single ticker: Close is a plain Series, not MultiIndex
        last = data["Close"].iloc[-1]
        if last == last:  # not NaN
            prices[tickers[0]] = float(last)
    else:
        for ticker in tickers:
            try:
                val = data["Close"][ticker].iloc[-1]
                if val == val:  # not NaN
                    prices[ticker] = float(val)
            except (KeyError, IndexError):
                pass
    return prices


def update_rows(rows, prices):
    """Update price_now and change_percentage in rows. Returns list of (ticker, old, new)."""
    changes = []
    for row in rows:
        ticker = row["ticker"]
        if ticker not in prices:
            print(f"  WARNING: No price data for {ticker}, keeping old value")
            continue
        old_price = row["price_now"]
        new_price = prices[ticker]
        pre_price = parse_price(row["price_prechatgpt"])
        change_pct = (new_price - pre_price) / pre_price
        row["price_now"] = f"{new_price:.2f}"
        row["change_percentage"] = str(change_pct)
        changes.append((ticker, old_price, row["price_now"]))
    return changes


def write_companies(fieldnames, rows, path=CSV_PATH):
    """Write rows back to companies.csv."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    # Ensure trailing newline
    with open(path, "a") as f:
        pass


def main():
    fieldnames, rows = read_companies()
    tickers = [row["ticker"] for row in rows]
    print(f"Fetching prices for {len(tickers)} tickers...")
    prices = fetch_prices(tickers)
    print(f"Got prices for {len(prices)}/{len(tickers)} tickers")
    changes = update_rows(rows, prices)
    write_companies(fieldnames, rows)
    print(f"\nUpdated {len(changes)} prices:")
    for ticker, old, new in changes:
        print(f"  {ticker}: {old} -> {new}")


if __name__ == "__main__":
    main()
