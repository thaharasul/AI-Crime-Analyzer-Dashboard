

import io
import csv
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from config import CRIME_CSV_PATH


def generate_csv_export(filters: dict | None = None) -> io.BytesIO:
    df = pd.read_csv(CRIME_CSV_PATH)
    filters = filters or {}

    if filters.get("zone"):
        df = df[df["zone"] == filters["zone"]]
    if filters.get("category"):
        df = df[df["category"] == filters["category"]]
    if filters.get("status"):
        df = df[df["status"] == filters["status"]]

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, quoting=csv.QUOTE_MINIMAL)

    byte_buffer = io.BytesIO(buffer.getvalue().encode("utf-8"))
    byte_buffer.seek(0)
    return byte_buffer


def _summary_table_data(analysis: dict):
    rows = [["Category", "Incident Count"]]
    for item in analysis.get("top_categories", []):
        rows.append([item["category"], str(item["count"])])
    return rows


def _zone_table_data(analysis: dict):
    rows = [["Zone", "Incident Count"]]
    for item in analysis.get("busiest_zones", []):
        rows.append([item["zone"], str(item["count"])])
    return rows


def generate_pdf_briefing(briefing: dict) -> io.BytesIO:
    """
    briefing is the dict returned by agents.coordinator.handle_request(
        "full_briefing", ...
    )
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6,
    )
    body_style = styles["BodyText"]

    story = [
        Paragraph("AI Crime Analyzer - Executive Briefing", title_style),
        Paragraph(
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style
        ),
        Spacer(1, 12),
    ]

    analysis = briefing.get("analysis", {})

    story.append(Paragraph("Overview", heading_style))
    story.append(Paragraph(
        f"Total recorded incidents in dataset: {analysis.get('total_crimes', 'N/A')}",
        body_style,
    ))

    story.append(Paragraph("Top Crime Categories", heading_style))
    cat_table = Table(_summary_table_data(analysis), hAlign="LEFT")
    cat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cat_table)

    story.append(Paragraph("Busiest Zones", heading_style))
    zone_table = Table(_zone_table_data(analysis), hAlign="LEFT")
    zone_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(zone_table)

    anomalies = analysis.get("zone_anomalies", [])
    if anomalies:
        story.append(Paragraph("Detected Anomalies", heading_style))
        for a in anomalies:
            story.append(Paragraph(
                f"- {a['zone']}: recent rate {a['recent_daily_rate']}/day vs "
                f"baseline {a['baseline_daily_rate']}/day "
                f"({a['increase_pct']}% increase)",
                body_style,
            ))

    story.append(Paragraph("AI-Generated Recommendations", heading_style))
    recommendation_text = briefing.get("recommendation", "No recommendation generated.")
    for line in recommendation_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))

    prediction = briefing.get("prediction")
    if prediction:
        story.append(Paragraph("Scenario Prediction", heading_style))
        story.append(Paragraph(
            f"Predicted category: {prediction['predicted_category']} "
            f"(confidence {prediction['confidence']*100:.1f}%, "
            f"risk level: {prediction['risk_level']})",
            body_style,
        ))

    doc.build(story)
    buffer.seek(0)
    return buffer
