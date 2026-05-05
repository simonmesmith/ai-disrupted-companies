"""Tests for daily_research.py."""

from ai_disruption_index.daily_research import extract_leads


def test_extract_leads(tmp_path):
    leads = tmp_path / "leads.md"
    leads.write_text(
        "# Leads\n"
        "- **TRI (Thomson Reuters)** - monitor if decline deepens\n"
        "- **DOCU (DocuSign)** - could cross below\n"
        "- **Legal & Tax thin category** - no ticker here\n"
    )

    assert extract_leads(leads) == [
        {"ticker": "TRI", "name": "Thomson Reuters"},
        {"ticker": "DOCU", "name": "DocuSign"},
    ]
