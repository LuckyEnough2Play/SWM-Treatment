"""Simple PDF export utilities for the Harper nutrient calculator."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .calculator import SiteData, format_breakdown


def export_pdf(result: dict, filepath: str, *, data: SiteData | None = None) -> None:
    """Export calculation results to a PDF file."""
    c = canvas.Canvas(str(filepath), pagesize=letter)

    text = c.beginText(72, 720)
    text.setFont("Helvetica", 12)
    text.textLine("Harper Nutrient Loading Results")
    text.textLine("")
    for key, value in result.items():
        text.textLine(f"{key}: {value:.2f}")
    if data is not None:
        text.textLine("")
        for line in format_breakdown(data, result).splitlines():
            text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
