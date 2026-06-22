"""
Report Generator — exports analysis results as PDF, CSV, or Excel.
"""
import io
import os
from typing import Any, Dict

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

from app.core.config import settings

REPORTS_DIR = os.path.join(settings.UPLOAD_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_report(
    title: str,
    sections: Dict[str, Any],
    output_path: str,
) -> str:
    """
    sections example:
    {
      "Dataset Summary": "text or list of bullet strings",
      "Key Insights": [...],
      "Recommendations": [...],
    }
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#6D28D9"))
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], textColor=colors.HexColor("#1E293B"))

    flow = [Paragraph(title, title_style), Spacer(1, 12)]

    for section_title, content in sections.items():
        flow.append(Paragraph(section_title, heading_style))
        flow.append(Spacer(1, 6))
        if isinstance(content, list):
            for item in content:
                flow.append(Paragraph(f"• {item}", styles["BodyText"]))
        elif isinstance(content, dict):
            data = [[k, str(v)] for k, v in content.items()]
            table = Table(data, colWidths=[6 * cm, 9 * cm])
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
            ]))
            flow.append(table)
        else:
            flow.append(Paragraph(str(content), styles["BodyText"]))
        flow.append(Spacer(1, 14))

    doc.build(flow)
    return output_path


def generate_csv_export(data: list[dict] | pd.DataFrame) -> bytes:
    df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_excel_export(sheets: Dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return buffer.getvalue()
