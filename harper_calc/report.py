"""Simple PDF export utilities for the Harper nutrient calculator."""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter

from .calculator import SiteData, format_breakdown


def export_pdf(
    result: dict,
    filepath: str,
    *,
    data: SiteData | None = None,
    project_name: str | None = None,
    left_margin: float = 0.5,
    right_margin: float = 0.5,
    top_margin: float = 1.0,
    bottom_margin: float = 1.0,
) -> None:
    """Export calculation results to a PDF file."""
    c = canvas.Canvas(str(filepath), pagesize=letter)

    line_height = 14
    x = left_margin * 72
    y = PAGE_HEIGHT - top_margin * 72
    text = c.beginText(x, y)
    text.setFont("Helvetica", 12)
    text.setLeading(line_height)
    text.textLine("Harper Nutrient Loading Results")
    y -= line_height
    if project_name:
        text.textLine(f"Project: {project_name}")
        y -= line_height
    text.textLine("")
    y -= line_height
    ordered = [
        ("runoff_volume_m3", "Runoff Volume (m^3)"),
        ("TN_kg_per_yr", "TN Load (kg/yr)"),
        ("TN_lb_per_yr", "TN Load (lb/yr)"),
        ("TP_kg_per_yr", "TP Load (kg/yr)"),
        ("TP_lb_per_yr", "TP Load (lb/yr)"),
    ]
    for key, label in ordered:
        if key in result:
            if y <= bottom_margin * 72:
                c.drawText(text)
                c.showPage()
                y = PAGE_HEIGHT - top_margin * 72
                text = c.beginText(x, y)
                text.setFont("Helvetica", 12)
            text.textLine(f"{label}: {result[key]:.2f}")
            y -= line_height
    if data is not None:
        if y <= bottom_margin * 72:
            c.drawText(text)
            c.showPage()
            y = PAGE_HEIGHT - top_margin * 72
            text = c.beginText(x, y)
            text.setFont("Helvetica", 12)
        text.textLine("")
        y -= line_height
        for line in format_breakdown(data, result).splitlines():
            if y <= bottom_margin * 72:
                c.drawText(text)
                c.showPage()
                y = PAGE_HEIGHT - top_margin * 72
                text = c.beginText(x, y)
                text.setFont("Helvetica", 12)
            text.textLine(line)
            y -= line_height

    c.drawText(text)
    c.showPage()
    c.save()
