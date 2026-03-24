"""Tests for generate_og_image.py."""

import pytest
from PIL import Image

from generate_og_image import generate


@pytest.fixture
def sample_payload():
    return {
        "index_value": 0.35,
        "company_count": 47,
        "price_date": "March 24, 2026",
        "companies": [
            {
                "ticker": "CHGG",
                "name": "Chegg Inc",
                "change_percentage": -0.98,
            },
            {
                "ticker": "EPAM",
                "name": "EPAM Systems Inc",
                "change_percentage": -0.60,
            },
        ],
    }


class TestGenerateOgImage:
    def test_creates_png(self, tmp_path, sample_payload, monkeypatch):
        output = tmp_path / "og-image.png"
        monkeypatch.setattr("generate_og_image.OUTPUT_PATH", output)
        generate(sample_payload)
        assert output.exists()

    def test_correct_dimensions(self, tmp_path, sample_payload, monkeypatch):
        output = tmp_path / "og-image.png"
        monkeypatch.setattr("generate_og_image.OUTPUT_PATH", output)
        generate(sample_payload)
        img = Image.open(output)
        assert img.size == (1200, 630)

    def test_is_valid_png(self, tmp_path, sample_payload, monkeypatch):
        output = tmp_path / "og-image.png"
        monkeypatch.setattr("generate_og_image.OUTPUT_PATH", output)
        generate(sample_payload)
        img = Image.open(output)
        assert img.format == "PNG"

    def test_nontrivial_file_size(self, tmp_path, sample_payload, monkeypatch):
        """Image should contain drawn text, so it should be more than a blank image."""
        output = tmp_path / "og-image.png"
        monkeypatch.setattr("generate_og_image.OUTPUT_PATH", output)
        generate(sample_payload)
        # A 1200x630 solid black PNG is ~2KB; with text it should be larger
        assert output.stat().st_size > 3000

    def test_works_without_companies(self, tmp_path, monkeypatch):
        """Should not crash when companies list is empty."""
        output = tmp_path / "og-image.png"
        monkeypatch.setattr("generate_og_image.OUTPUT_PATH", output)
        payload = {
            "index_value": 0.50,
            "company_count": 0,
            "price_date": "January 1, 2025",
            "companies": [],
        }
        generate(payload)
        assert output.exists()
