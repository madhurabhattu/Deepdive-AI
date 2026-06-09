"""
DeepDive AI — PDF Report Generator

Generates a professionally formatted PDF from a ResearchReport using ReportLab.

Output layout:
  Page 1 — Title + topic + date
  Page 2 — Executive Summary
  Page 3 — Key Insights (bulleted list)
  Page 4 — Statistics (two-column table)
  Page 5 — References (numbered list with URLs)
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.report_schema import ResearchReport

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Brand colours
_PRIMARY = colors.HexColor("#1a237e")     # Deep indigo
_ACCENT = colors.HexColor("#0d47a1")      # Dark blue
_LIGHT_BG = colors.HexColor("#e8eaf6")    # Lavender
_TEXT_DARK = colors.HexColor("#212121")
_TEXT_GRAY = colors.HexColor("#616161")
_WHITE = colors.white


def sanitise_filename(topic: str) -> str:
    """Replace non-alphanumeric characters with underscores and truncate."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
    return clean[:80] if len(clean) > 80 else clean


def _get_styles() -> dict[str, ParagraphStyle]:
    """Build custom paragraph styles for the PDF."""
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontSize=28,
            textColor=_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=34,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontSize=14,
            textColor=_ACCENT,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_date": ParagraphStyle(
            "CoverDate",
            parent=base["Normal"],
            fontSize=11,
            textColor=_TEXT_GRAY,
            alignment=TA_CENTER,
            spaceBefore=20,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading1"],
            fontSize=18,
            textColor=_PRIMARY,
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=0,
            borderPadding=0,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=11,
            textColor=_TEXT_DARK,
            alignment=TA_JUSTIFY,
            leading=16,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=11,
            textColor=_TEXT_DARK,
            leading=16,
            leftIndent=20,
            bulletIndent=8,
            spaceAfter=6,
        ),
        "ref_title": ParagraphStyle(
            "RefTitle",
            parent=base["Normal"],
            fontSize=11,
            textColor=_ACCENT,
            leading=14,
            spaceAfter=2,
        ),
        "ref_snippet": ParagraphStyle(
            "RefSnippet",
            parent=base["Normal"],
            fontSize=10,
            textColor=_TEXT_GRAY,
            leading=13,
            leftIndent=16,
            spaceAfter=8,
        ),
    }


def build_pdf(report: ResearchReport) -> str:
    """Generate a multi-page PDF report and return the filepath.

    Parameters
    ----------
    report : ResearchReport
        A validated research report dataclass.

    Returns
    -------
    str
        Absolute path to the generated PDF file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{sanitise_filename(report.topic)}_report.pdf"
    filepath = OUTPUT_DIR / filename
    styles = _get_styles()
    story: list = []
    date_str = datetime.now().strftime("%B %d, %Y")

    # ── Cover Page ───────────────────────────────────────────────────
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("🔬 DeepDive AI", styles["cover_subtitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(report.topic, styles["cover_title"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(
        Paragraph("AI-Generated Research Report", styles["cover_subtitle"])
    )
    story.append(Paragraph(f"Generated on {date_str}", styles["cover_date"]))
    story.append(PageBreak())

    # ── Executive Summary ────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(report.executive_summary, styles["body"]))
    story.append(PageBreak())

    # ── Key Insights ─────────────────────────────────────────────────
    story.append(Paragraph("Key Insights", styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for idx, insight in enumerate(report.key_insights, start=1):
        story.append(
            Paragraph(f"<b>{idx}.</b>  {insight}", styles["bullet"])
        )
    story.append(PageBreak())

    # ── Statistics ───────────────────────────────────────────────────
    story.append(
        Paragraph("Statistics &amp; Data", styles["section_heading"])
    )
    story.append(Spacer(1, 4 * mm))

    table_data = [["Metric", "Value"]]
    for stat in report.statistics:
        table_data.append([stat.get("label", ""), stat.get("value", "")])

    col_widths = [3.5 * inch, 2.5 * inch]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("FONTSIZE", (0, 1), (-1, -1), 11),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _LIGHT_BG]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdbdbd")),
            ]
        )
    )
    story.append(table)
    story.append(PageBreak())

    # ── References ───────────────────────────────────────────────────
    story.append(
        Paragraph("References &amp; Citations", styles["section_heading"])
    )
    story.append(Spacer(1, 4 * mm))
    for idx, ref in enumerate(report.references, start=1):
        title = ref.get("title", "Untitled")
        url = ref.get("url", "")
        snippet = ref.get("snippet", "")
        story.append(
            Paragraph(
                f'<b>{idx}.</b> <a href="{url}" color="#0d47a1">{title}</a>',
                styles["ref_title"],
            )
        )
        story.append(Paragraph(snippet, styles["ref_snippet"]))

    # ── Build PDF ────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"DeepDive AI — {report.topic}",
        author="DeepDive AI",
    )
    doc.build(story)

    logger.info("PDF generated: %s", filepath)
    return str(filepath)
