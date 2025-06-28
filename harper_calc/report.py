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
    ordered = [
        ("runoff_volume_m3", "Runoff Volume (m^3)"),
        ("TN_kg_per_yr", "TN Load (kg/yr)"),
        ("TN_lb_per_yr", "TN Load (lb/yr)"),
        ("TP_kg_per_yr", "TP Load (kg/yr)"),
        ("TP_lb_per_yr", "TP Load (lb/yr)"),
    ]
    for key, label in ordered:
        if key in result:
            text.textLine(f"{label}: {result[key]:.2f}")
    if data is not None:
        text.textLine("")
        for line in format_breakdown(data, result).splitlines():
            text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
