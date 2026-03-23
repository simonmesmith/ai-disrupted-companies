"""Tests for generate_page.py."""

import json
import pytest

from generate_page import (
    build_payload,
    compute_group_stats,
    compute_index,
    generate_html,
    parse_price,
    read_companies,
)

SAMPLE_CSV = """\
ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage
CHGG,Chegg Inc,Education,EdTech,desc one,disruption one,28.11,0.45,-0.9839914621
EPAM,EPAM Systems Inc,Business Services,IT Services,desc two,disruption two,343.94,137.43,-0.6004244926
FVRR,Fiverr International Ltd,Freelance Marketplaces,Freelance Platform,desc three,disruption three,33.13,10.25,-0.6906127377
"""


@pytest.fixture
def csv_path(tmp_path):
    p = tmp_path / "companies.csv"
    p.write_text(SAMPLE_CSV)
    return p


@pytest.fixture
def sample_companies():
    return [
        {
            "ticker": "CHGG", "name": "Chegg Inc",
            "category": "Education", "subcategory": "EdTech",
            "description": "desc one", "disruption": "disruption one",
            "price_prechatgpt": 28.11, "price_now": 0.45,
            "change_percentage": -0.9839914621,
        },
        {
            "ticker": "EPAM", "name": "EPAM Systems Inc",
            "category": "Business Services", "subcategory": "IT Services",
            "description": "desc two", "disruption": "disruption two",
            "price_prechatgpt": 343.94, "price_now": 137.43,
            "change_percentage": -0.6004244926,
        },
        {
            "ticker": "FVRR", "name": "Fiverr International Ltd",
            "category": "Freelance Marketplaces", "subcategory": "Freelance Platform",
            "description": "desc three", "disruption": "disruption three",
            "price_prechatgpt": 33.13, "price_now": 10.25,
            "change_percentage": -0.6906127377,
        },
    ]


class TestParsePrice:
    def test_plain(self):
        assert parse_price("28.11") == 28.11

    def test_dollar_sign(self):
        assert parse_price("$28.11") == 28.11

    def test_commas(self):
        assert parse_price("$2,485.00") == 2485.00


class TestReadCompanies:
    def test_reads_and_parses(self, csv_path, monkeypatch):
        monkeypatch.setattr("generate_page.CSV_PATH", csv_path)
        companies = read_companies()
        assert len(companies) == 3
        assert companies[0]["ticker"] == "CHGG"
        assert isinstance(companies[0]["price_prechatgpt"], float)
        assert isinstance(companies[0]["price_now"], float)
        assert isinstance(companies[0]["change_percentage"], float)


class TestComputeIndex:
    def test_equal_weighted(self, sample_companies):
        index = compute_index(sample_companies)
        # Manual: mean of (0.45/28.11, 137.43/343.94, 10.25/33.13)
        expected = (0.45 / 28.11 + 137.43 / 343.94 + 10.25 / 33.13) / 3
        assert index == pytest.approx(expected)

    def test_no_change(self):
        companies = [
            {"price_prechatgpt": 100.0, "price_now": 100.0},
            {"price_prechatgpt": 50.0, "price_now": 50.0},
        ]
        assert compute_index(companies) == pytest.approx(1.0)

    def test_total_loss(self):
        companies = [
            {"price_prechatgpt": 100.0, "price_now": 0.0},
        ]
        assert compute_index(companies) == pytest.approx(0.0)


class TestComputeGroupStats:
    def test_groups_by_category(self, sample_companies):
        stats = compute_group_stats(sample_companies, "category")
        names = {s["name"] for s in stats}
        assert names == {"Education", "Business Services", "Freelance Marketplaces"}

    def test_counts(self, sample_companies):
        stats = compute_group_stats(sample_companies, "category")
        by_name = {s["name"]: s for s in stats}
        assert by_name["Education"]["count"] == 1
        assert by_name["Business Services"]["count"] == 1

    def test_avg_change(self, sample_companies):
        stats = compute_group_stats(sample_companies, "category")
        by_name = {s["name"]: s for s in stats}
        assert by_name["Education"]["avg_change"] == pytest.approx(-0.9839914621)

    def test_groups_by_subcategory(self, sample_companies):
        stats = compute_group_stats(sample_companies, "subcategory")
        names = {s["name"] for s in stats}
        assert "EdTech" in names
        assert "IT Services" in names


class TestBuildPayload:
    def test_has_required_keys(self, sample_companies):
        payload = build_payload(sample_companies)
        assert "generated_at" in payload
        assert "price_date" in payload
        assert "index_value" in payload
        assert "company_count" in payload
        assert "companies" in payload
        assert "categories" in payload
        assert "subcategories" in payload

    def test_company_count(self, sample_companies):
        payload = build_payload(sample_companies)
        assert payload["company_count"] == 3
        assert len(payload["companies"]) == 3

    def test_index_value_is_numeric(self, sample_companies):
        payload = build_payload(sample_companies)
        assert isinstance(payload["index_value"], float)
        assert 0 < payload["index_value"] < 1

    def test_latest_company_is_last_row(self, sample_companies):
        payload = build_payload(sample_companies)
        latest = payload["latest_company"]
        assert latest["ticker"] == "FVRR"
        assert latest["name"] == "Fiverr International Ltd"
        assert latest["category"] == "Freelance Marketplaces"
        assert latest["subcategory"] == "Freelance Platform"
        assert latest["description"] == "desc three"
        assert latest["disruption"] == "disruption three"
        assert latest["price_prechatgpt"] == 33.13
        assert latest["price_now"] == 10.25
        assert latest["change_percentage"] == pytest.approx(-0.6906127377, rel=1e-4)


class TestGenerateHtml:
    def test_injects_json(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text("<html><script>const DATA = {{ DATA_JSON }};</script></html>")
        payload = {"test": "value", "num": 42}

        import generate_page
        orig = generate_page.TEMPLATE_PATH
        generate_page.TEMPLATE_PATH = template
        try:
            html = generate_html(payload)
        finally:
            generate_page.TEMPLATE_PATH = orig

        assert "{{ DATA_JSON }}" not in html
        assert '"test": "value"' in html
        assert '"num": 42' in html
        # Verify the injected JSON is valid
        start = html.index("const DATA = ") + len("const DATA = ")
        end = html.index(";", start)
        parsed = json.loads(html[start:end])
        assert parsed == payload
