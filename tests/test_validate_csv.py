"""Tests for validate_csv.py."""

from ai_disruption_index.validate_csv import (
    find_duplicate_names,
    find_duplicate_tickers,
    validate,
)

CLEAN_CSV = """\
ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage
CHGG,Chegg Inc,Education,EdTech,desc,disruption,28.11,0.45,-0.9839914621
EPAM,EPAM Systems Inc,Business Services,IT Services,desc,disruption,343.94,137.43,-0.6004244926
"""

DUPLICATE_CSV = """\
ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage
CHGG,Chegg Inc,Education,EdTech,desc,disruption,28.11,0.45,-0.9839914621
EPAM,EPAM Systems Inc,Business Services,IT Services,desc,disruption,343.94,137.43,-0.6004244926
CHGG,Chegg Inc,Education,EdTech,desc,disruption,28.11,0.45,-0.9839914621
"""


class TestFindDuplicateTickers:
    def test_no_duplicates(self, tmp_path):
        p = tmp_path / "clean.csv"
        p.write_text(CLEAN_CSV)
        assert find_duplicate_tickers(p) == {}

    def test_finds_duplicates(self, tmp_path):
        p = tmp_path / "dupes.csv"
        p.write_text(DUPLICATE_CSV)
        dupes = find_duplicate_tickers(p)
        assert "CHGG" in dupes
        assert len(dupes["CHGG"]) == 2

    def test_case_insensitive(self, tmp_path):
        csv_text = (
            "ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage\n"
            "chgg,Chegg,Education,EdTech,d,d,28.11,0.45,-0.9839914621\n"
            "CHGG,Chegg,Education,EdTech,d,d,28.11,0.45,-0.9839914621\n"
        )
        p = tmp_path / "case.csv"
        p.write_text(csv_text)
        dupes = find_duplicate_tickers(p)
        assert "CHGG" in dupes


class TestFindDuplicateNames:
    def test_finds_likely_duplicate_names(self, tmp_path):
        csv_text = (
            "ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage\n"
            "AAA,Acme Inc,Education,EdTech,d,d,100,50,-0.5\n"
            "BBB,Acme Corporation,Education,EdTech,d,d,100,50,-0.5\n"
        )
        p = tmp_path / "names.csv"
        p.write_text(csv_text)
        dupes = find_duplicate_names(p)
        assert "acme" in dupes


class TestValidate:
    def test_passes_clean(self, tmp_path):
        p = tmp_path / "clean.csv"
        p.write_text(CLEAN_CSV)
        assert validate(p) is True

    def test_fails_duplicates(self, tmp_path):
        p = tmp_path / "dupes.csv"
        p.write_text(DUPLICATE_CSV)
        assert validate(p) is False

    def test_fails_inconsistent_change_percentage(self, tmp_path):
        csv_text = (
            "ticker,name,category,subcategory,description,disruption,price_prechatgpt,price_now,change_percentage\n"
            "AAA,Acme Inc,Education,EdTech,d,d,100,50,-0.1\n"
        )
        p = tmp_path / "bad-change.csv"
        p.write_text(csv_text)
        assert validate(p) is False


class TestActualCsv:
    def test_no_duplicates_in_companies_csv(self):
        """Ensure the real companies.csv has no duplicate tickers."""
        assert validate() is True
