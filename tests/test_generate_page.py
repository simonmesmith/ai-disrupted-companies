"""Tests for generate_page.py."""

import json
import pytest

from ai_disruption_index.generate_page import (
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


@pytest.fixture
def mixed_companies(sample_companies):
    return sample_companies + [
        {
            "ticker": "REC", "name": "Recovered Corp",
            "category": "Education", "subcategory": "EdTech",
            "description": "desc four", "disruption": "disruption four",
            "price_prechatgpt": 10.0, "price_now": 12.0,
            "change_percentage": 0.2,
        }
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
        monkeypatch.setattr("ai_disruption_index.generate_page.CSV_PATH", csv_path)
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

    def test_company_count(self, mixed_companies):
        payload = build_payload(mixed_companies)
        assert payload["company_count"] == 3
        assert len(payload["companies"]) == 3
        assert payload["recovered_count"] == 1
        assert payload["tracked_company_count"] == 4
        assert len(payload["recovered_companies"]) == 1

    def test_partitions_companies_at_zero(self, mixed_companies):
        mixed_companies.append(
            {**mixed_companies[-1], "ticker": "ZERO", "change_percentage": 0.0}
        )
        payload = build_payload(mixed_companies)
        assert {c["ticker"] for c in payload["companies"]} == {
            "CHGG", "EPAM", "FVRR"
        }
        assert {c["ticker"] for c in payload["recovered_companies"]} == {
            "REC", "ZERO"
        }

    def test_index_and_groups_use_active_companies_only(self, mixed_companies):
        payload = build_payload(mixed_companies)
        active = mixed_companies[:3]
        assert payload["index_value"] == pytest.approx(compute_index(active), abs=0.00005)
        education = next(s for s in payload["categories"] if s["name"] == "Education")
        assert education["count"] == 1

    def test_recovered_company_reenters_when_change_turns_negative(
        self, mixed_companies
    ):
        mixed_companies[-1]["change_percentage"] = -0.1
        mixed_companies[-1]["price_now"] = 9.0
        payload = build_payload(mixed_companies)
        assert "REC" in {c["ticker"] for c in payload["companies"]}
        assert "REC" not in {
            c["ticker"] for c in payload["recovered_companies"]
        }

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

    def test_no_active_companies(self, mixed_companies):
        recovered = [mixed_companies[-1]]
        payload = build_payload(recovered)
        assert payload["index_value"] == 0.0
        assert payload["company_count"] == 0
        assert payload["latest_company"] is None
        assert payload["categories"] == []


class TestGenerateHtml:
    TEMPLATE_WITH_META = (
        "<html><head>"
        "<title>{{ OG_TITLE }}</title>"
        '<meta name="description" content="{{ META_DESCRIPTION }}">'
        '<script type="application/ld+json">{{ JSONLD }}</script>'
        "</head><body>"
        "<script>const DATA = {{ DATA_JSON }};</script>"
        "</body></html>"
    )

    def test_injects_json(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text("<html><script>const DATA = {{ DATA_JSON }};</script></html>")
        payload = {"test": "value", "num": 42, "index_value": 0.35, "company_count": 3}

        from ai_disruption_index import generate_page
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

    def test_replaces_all_placeholders(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text(self.TEMPLATE_WITH_META)
        payload = {"index_value": 0.42, "company_count": 10}

        from ai_disruption_index import generate_page
        orig = generate_page.TEMPLATE_PATH
        generate_page.TEMPLATE_PATH = template
        try:
            html = generate_html(payload)
        finally:
            generate_page.TEMPLATE_PATH = orig

        assert "{{ OG_TITLE }}" not in html
        assert "{{ META_DESCRIPTION }}" not in html
        assert "{{ JSONLD }}" not in html
        assert "{{ DATA_JSON }}" not in html

    def test_meta_description_contains_dynamic_values(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text(self.TEMPLATE_WITH_META)
        payload = {"index_value": 0.35, "company_count": 47}

        from ai_disruption_index import generate_page
        orig = generate_page.TEMPLATE_PATH
        generate_page.TEMPLATE_PATH = template
        try:
            html = generate_html(payload)
        finally:
            generate_page.TEMPLATE_PATH = orig

        assert "$0.35" in html
        assert "47" in html

    def test_jsonld_is_valid(self, tmp_path):
        template = tmp_path / "template.html"
        template.write_text(self.TEMPLATE_WITH_META)
        payload = {"index_value": 0.50, "company_count": 20}

        from ai_disruption_index import generate_page
        orig = generate_page.TEMPLATE_PATH
        generate_page.TEMPLATE_PATH = template
        try:
            html = generate_html(payload)
        finally:
            generate_page.TEMPLATE_PATH = orig

        start = html.index('application/ld+json">') + len('application/ld+json">')
        end = html.index("</script>", start)
        ld = json.loads(html[start:end])
        assert ld["@type"] == "WebSite"
        assert ld["@context"] == "https://schema.org"
        assert "url" in ld

    def test_recovered_company_label_is_singular_only_for_one(self):
        from ai_disruption_index import generate_page

        template = generate_page.TEMPLATE_PATH.read_text()

        assert (
            "DATA.recovered_count === 1 ? 'company' : 'companies'"
            in template
        )
        assert "recovered ${recoveredCompanyNoun}." in template
