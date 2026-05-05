"""Tests for update_prices.py."""

from unittest.mock import patch

import pandas as pd
import pytest

from ai_disruption_index.update_prices import (
    fetch_prices,
    parse_price,
    read_companies,
    update_rows,
    write_companies,
)

SAMPLE_CSV = """ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage
CHGG,Chegg Inc,Education,EdTech,desc,disruption,$28.11,$0.45,-0.9839914621
EPAM,EPAM Systems Inc,Business Services,IT Services,desc,disruption,$343.94,$137.43,-0.6004244926
"""


@pytest.fixture
def csv_path(tmp_path):
    p = tmp_path / "companies.csv"
    p.write_text(SAMPLE_CSV)
    return p


class TestReadCompanies:
    def test_reads_all_rows(self, csv_path):
        fieldnames, rows = read_companies(csv_path)
        assert len(rows) == 2
        assert rows[0]["ticker"] == "CHGG"
        assert rows[1]["ticker"] == "EPAM"

    def test_reads_fieldnames(self, csv_path):
        fieldnames, rows = read_companies(csv_path)
        assert "ticker" in fieldnames
        assert "price_now" in fieldnames
        assert "change_percentage" in fieldnames


class TestWriteCompanies:
    def test_round_trip(self, csv_path):
        fieldnames, rows = read_companies(csv_path)
        write_companies(fieldnames, rows, csv_path)
        fieldnames2, rows2 = read_companies(csv_path)
        assert len(rows2) == len(rows)
        for orig, written in zip(rows, rows2):
            assert orig["ticker"] == written["ticker"]
            assert orig["price_prechatgpt"] == written["price_prechatgpt"]

    def test_preserves_quoted_fields(self, tmp_path):
        p = tmp_path / "test.csv"
        p.write_text(
            'ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage\n'
            'CHGG,Chegg Inc,Education,EdTech,"desc with, comma","disruption with, comma",28.11,0.45,-0.98\n'
        )
        fieldnames, rows = read_companies(p)
        write_companies(fieldnames, rows, p)
        fieldnames2, rows2 = read_companies(p)
        assert rows2[0]["description"] == "desc with, comma"


class TestParsePrice:
    def test_plain_number(self):
        assert parse_price("28.11") == 28.11

    def test_dollar_sign(self):
        assert parse_price("$28.11") == 28.11

    def test_dollar_with_comma(self):
        assert parse_price("$2,485.00") == 2485.00

    def test_whitespace(self):
        assert parse_price(" $28.11 ") == 28.11


class TestUpdateRows:
    def test_updates_prices(self):
        rows = [
            {"ticker": "CHGG", "price_prechatgpt": "$28.11", "price_now": "$0.45", "change_percentage": "-0.98"},
            {"ticker": "EPAM", "price_prechatgpt": "$343.94", "price_now": "$137.43", "change_percentage": "-0.60"},
        ]
        prices = {"CHGG": 0.50, "EPAM": 140.00}
        changes = update_rows(rows, prices)
        assert len(changes) == 2
        assert rows[0]["price_now"] == "0.50"
        assert rows[1]["price_now"] == "140.00"

    def test_calculates_change_percentage(self):
        rows = [
            {"ticker": "TEST", "price_prechatgpt": "100.00", "price_now": "50.00", "change_percentage": "-0.5"},
        ]
        prices = {"TEST": 75.0}
        update_rows(rows, prices)
        assert float(rows[0]["change_percentage"]) == pytest.approx(-0.25)

    def test_missing_ticker_keeps_old_value(self, capsys):
        rows = [
            {"ticker": "MISSING", "price_prechatgpt": "100.00", "price_now": "50.00", "change_percentage": "-0.5"},
        ]
        changes = update_rows(rows, {})
        assert len(changes) == 0
        assert rows[0]["price_now"] == "50.00"
        assert "WARNING" in capsys.readouterr().out

    def test_partial_prices(self):
        rows = [
            {"ticker": "A", "price_prechatgpt": "10.00", "price_now": "5.00", "change_percentage": "-0.5"},
            {"ticker": "B", "price_prechatgpt": "20.00", "price_now": "10.00", "change_percentage": "-0.5"},
        ]
        prices = {"A": 6.0}  # B is missing
        changes = update_rows(rows, prices)
        assert len(changes) == 1
        assert rows[0]["price_now"] == "6.00"
        assert rows[1]["price_now"] == "10.00"  # unchanged


class TestFetchPrices:
    def test_empty_tickers(self):
        assert fetch_prices([]) == {}

    @patch("ai_disruption_index.update_prices.yf.download")
    def test_single_ticker(self, mock_download):
        df = pd.DataFrame({"Close": [42.50]}, index=pd.DatetimeIndex(["2026-03-20"]))
        mock_download.return_value = df
        result = fetch_prices(["CHGG"])
        assert result == {"CHGG": 42.50}

    @patch("ai_disruption_index.update_prices.yf.download")
    def test_multiple_tickers(self, mock_download):
        arrays = [["Close", "Close"], ["CHGG", "EPAM"]]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples)
        df = pd.DataFrame([[0.50, 140.00]], columns=index, index=pd.DatetimeIndex(["2026-03-20"]))
        mock_download.return_value = df
        result = fetch_prices(["CHGG", "EPAM"])
        assert result["CHGG"] == pytest.approx(0.50)
        assert result["EPAM"] == pytest.approx(140.00)

    @patch("ai_disruption_index.update_prices.yf.download")
    def test_empty_download(self, mock_download):
        mock_download.return_value = pd.DataFrame()
        result = fetch_prices(["FAKE"])
        assert result == {}
