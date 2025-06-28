"""Tests for PDF export functionality."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc.report import export_pdf
from harper_calc.calculator import SiteData, calculate_site_loads


def test_export_pdf(tmp_path):
    data = SiteData(1.0, 1.0, 0.5, 2.0, 0.5)
    result = calculate_site_loads(data)
    pdf_path = tmp_path / "result.pdf"
    export_pdf(result, pdf_path, data=data)
    assert pdf_path.exists() and pdf_path.stat().st_size > 0