"""Tests for PDF export functionality."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harper_calc.report import export_pdf
from harper_calc.calculator import SiteData, calculate_site_loads
from PyPDF2 import PdfReader


def test_export_pdf(tmp_path):
    data = SiteData(1.0, 1.0, 0.5, 2.0, 0.5)
    result = calculate_site_loads(data)
    pdf_path = tmp_path / "result.pdf"
    export_pdf(
        result,
        pdf_path,
        data=data,
        project_name="Test Project",
        left_margin=0.75,
        right_margin=0.75,
        top_margin=1.25,
        bottom_margin=1.25,
    )
    assert pdf_path.exists() and pdf_path.stat().st_size > 0
    reader = PdfReader(str(pdf_path))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert "Test Project" in text
