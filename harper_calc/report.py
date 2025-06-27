"""Simple PDF export utilities for the Harper nutrient calculator."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_pdf(result: dict, filepath: str) -> None:
    """Export calculation results to a PDF file."""
    c = canvas.Canvas(str(filepath), pagesize=letter)

    text = c.beginText(72, 720)
    text.setFont("Helvetica", 12)
    text.textLine("Harper Nutrient Loading Results")
    text.textLine("")
    for key, value in result.items():
        text.textLine(f"{key}: {value:.2f}")

    c.drawText(text)
    c.showPage()
    c.save()
