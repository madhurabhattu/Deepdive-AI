"""
DeepDive AI — PDF Report Generator

Generates a professionally formatted PDF from a ResearchReport using ReportLab.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils.font_manager import ensure_fonts_exist, get_font_path
from utils.localization import get_text
from utils.report_schema import ResearchReport

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Brand colours
_PRIMARY = colors.HexColor("#1a237e")  # Deep indigo
_ACCENT = colors.HexColor("#0d47a1")  # Dark blue
_LIGHT_BG = colors.HexColor("#e8eaf6")  # Lavender
_TEXT_DARK = colors.HexColor("#212121")
_TEXT_GRAY = colors.HexColor("#616161")
_WHITE = colors.white


def sanitise_filename(topic: str) -> str:
    """Replace non-alphanumeric characters with underscores and truncate."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
    return clean[:80] if len(clean) > 80 else clean


def xml_escape(text: str) -> str:
    """Escape XML special characters while preserving allowed formatting tags.

    Allowed tags: <b>, </b>, <i>, </i>, <u>, </u>, <font...>, </font>, <a...>, </a>
    """
    if not isinstance(text, str):
        return str(text)

    # Escape raw ampersands that aren't already part of an XML entity
    text = re.sub(r"&(?!#[0-9]+;|[a-zA-Z0-9]+;)", "&amp;", text)

    # Mark allowed styling/link tags
    allowed_tags = r"(/?b|/?i|/?u|/?font|a\s+[^>]*|/a)"
    temp_start = "___TAG_START___"
    temp_end = "___TAG_END___"

    def mask_tag(match: re.Match) -> str:
        return f"{temp_start}{match.group(1)}{temp_end}"

    # Replace <tag> with masked placeholders
    tag_pattern = rf"<({allowed_tags})>"
    masked = re.sub(tag_pattern, mask_tag, text, flags=re.IGNORECASE)

    # Escape all other '<' and '>'
    escaped = masked.replace("<", "&lt;").replace(">", "&gt;")

    # Restore the allowed styling tags
    restored = escaped.replace(temp_start, "<").replace(temp_end, ">")
    return restored


def _get_pdf_font_name(lang: str) -> str:
    """Return appropriate font name based on language selection."""
    if lang in ["hi", "mr"]:
        return "NotoSansDevanagari"
    elif lang == "te":
        return "NotoSansTelugu"
    return "Helvetica"


def _register_indic_fonts() -> None:
    """Download and register Noto Sans fonts for PDF generation."""
    try:
        ensure_fonts_exist()
        # Register Noto Sans Devanagari (Regular and Bold alias to
        # avoid bold missing error)
        dev_path = get_font_path("NotoSansDevanagari-Regular.ttf")
        pdfmetrics.registerFont(TTFont("NotoSansDevanagari", dev_path))
        pdfmetrics.registerFont(TTFont("NotoSansDevanagari-Bold", dev_path))

        # Register Noto Sans Telugu (Regular and Bold alias)
        te_path = get_font_path("NotoSansTelugu-Regular.ttf")
        pdfmetrics.registerFont(TTFont("NotoSansTelugu", te_path))
        pdfmetrics.registerFont(TTFont("NotoSansTelugu-Bold", te_path))
    except Exception as exc:
        logger.error("Failed to register Indic fonts: %s", exc)


def _get_styles(lang: str = "en") -> dict[str, ParagraphStyle]:
    """Build custom paragraph styles for the PDF."""
    base = getSampleStyleSheet()
    font_name = _get_pdf_font_name(lang)
    bold_font_name = (
        f"{font_name}-Bold" if lang in ["hi", "mr", "te"] else "Helvetica-Bold"
    )

    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName=bold_font_name,
            fontSize=28,
            textColor=_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=34,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=14,
            textColor=_ACCENT,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_date": ParagraphStyle(
            "CoverDate",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=11,
            textColor=_TEXT_GRAY,
            alignment=TA_CENTER,
            spaceBefore=20,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading1"],
            fontName=bold_font_name,
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
            fontName=font_name,
            fontSize=11,
            textColor=_TEXT_DARK,
            alignment=TA_JUSTIFY,
            leading=16,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName=font_name,
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
            fontName=bold_font_name,
            fontSize=11,
            textColor=_ACCENT,
            leading=14,
            spaceAfter=2,
        ),
        "ref_snippet": ParagraphStyle(
            "RefSnippet",
            parent=base["Normal"],
            fontName=font_name,
            fontSize=10,
            textColor=_TEXT_GRAY,
            leading=13,
            leftIndent=16,
            spaceAfter=8,
        ),
    }


def build_pdf(report: ResearchReport, lang: str = "en") -> str:
    """Generate a multi-page localized PDF report and return the filepath.

    Parameters
    ----------
    report : ResearchReport
        A validated research report dataclass.
    lang : str
        The language code ('en', 'hi', 'mr', 'te') for the PDF layout.

    Returns
    -------
    str
        Absolute path to the generated PDF file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{sanitise_filename(report.topic)}_report.pdf"
    filepath = OUTPUT_DIR / filename

    if lang in ["hi", "mr", "te"]:
        _register_indic_fonts()

    styles = _get_styles(lang)
    story: list = []
    date_str = datetime.now().strftime("%B %d, %Y")
    font_name = _get_pdf_font_name(lang)
    bold_font_name = (
        f"{font_name}-Bold" if lang in ["hi", "mr", "te"] else "Helvetica-Bold"
    )

    # ── Cover Page ───────────────────────────────────────────────────
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph(get_text("app_title", lang), styles["cover_subtitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(xml_escape(report.topic), styles["cover_title"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(get_text("app_tagline", lang), styles["cover_subtitle"]))
    story.append(
        Paragraph(
            f"{get_text('built_with', lang)} DeepDive AI — {date_str}",
            styles["cover_date"],
        )
    )
    story.append(PageBreak())

    # ── Executive Summary & Background Context ───────────────────────
    story.append(
        Paragraph(get_text("feat_summary_title", lang), styles["section_heading"])
    )
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(xml_escape(report.executive_summary), styles["body"]))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(get_text("sec_background", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(xml_escape(report.background_context), styles["body"]))
    story.append(PageBreak())

    # ── Core Concepts ────────────────────────────────────────────────
    story.append(Paragraph(get_text("sec_concepts", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for concept in report.core_concepts:
        term = xml_escape(concept.get("term", ""))
        definition = xml_escape(concept.get("definition", ""))
        story.append(Paragraph(f"<b>•  {term}</b>: {definition}", styles["bullet"]))
        story.append(Spacer(1, 2 * mm))
    story.append(PageBreak())

    # ── Key Insights ─────────────────────────────────────────────────
    story.append(
        Paragraph(get_text("feat_insights_title", lang), styles["section_heading"])
    )
    story.append(Spacer(1, 4 * mm))
    for idx, insight in enumerate(report.key_insights, start=1):
        story.append(
            Paragraph(f"<b>{idx}.</b>  {xml_escape(insight)}", styles["bullet"])
        )
    story.append(PageBreak())

    # ── Statistics ───────────────────────────────────────────────────
    story.append(
        Paragraph(get_text("feat_stats_title", lang), styles["section_heading"])
    )
    story.append(Spacer(1, 4 * mm))

    # Translate column headers
    metric_label = get_text("supporting_data", lang)
    value_label = get_text("supporting_data", lang) + " " + "Value"  # e.g. "డేటా విలువ"
    if lang == "hi":
        value_label = "डेटा मान"
    elif lang == "mr":
        value_label = "डेटा मूल्य"
    elif lang == "te":
        value_label = "డేటా విలువ"
    else:
        value_label = "Value"

    table_data = [[metric_label, value_label]]
    for stat in report.statistics:
        table_data.append([stat.get("label", ""), stat.get("value", "")])

    col_widths = [3.5 * inch, 2.5 * inch]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
                ("FONTNAME", (0, 0), (-1, 0), bold_font_name),
                ("FONTNAME", (0, 1), (-1, -1), font_name),
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

    # ── Benefits, Challenges & Risks ─────────────────────────────────
    story.append(Paragraph(get_text("sec_benefits", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for it in report.benefits_challenges_risks:
        item_name = xml_escape(it.get("item", ""))
        item_type = xml_escape(it.get("type", "").upper())
        description = xml_escape(it.get("description", ""))

        color_hex = "#1b237e"
        if item_type == "BENEFIT":
            color_hex = "#2e7d32"
        elif item_type == "CHALLENGE":
            color_hex = "#f57c00"
        elif item_type == "RISK":
            color_hex = "#c62828"

        p_text = (
            f'<b><font color="{color_hex}">[{item_type}]</font> '
            f"{item_name}</b>: {description}"
        )
        story.append(
            Paragraph(
                p_text,
                styles["bullet"],
            )
        )
        story.append(Spacer(1, 2 * mm))
    story.append(PageBreak())

    # ── Real-World Applications ──────────────────────────────────────
    story.append(Paragraph(get_text("sec_apps", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for app in report.real_world_applications:
        application = xml_escape(app.get("application", ""))
        description = xml_escape(app.get("description", ""))
        story.append(
            Paragraph(f"<b>•  {application}</b>: {description}", styles["bullet"])
        )
        story.append(Spacer(1, 2 * mm))
    story.append(PageBreak())

    # ── Future Outlook & References ──────────────────────────────────
    story.append(Paragraph(get_text("sec_outlook", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for idx, outlook in enumerate(report.future_outlook, start=1):
        story.append(
            Paragraph(f"<b>{idx}.</b>  {xml_escape(outlook)}", styles["bullet"])
        )
        story.append(Spacer(1, 2 * mm))

    story.append(PageBreak())
    story.append(Paragraph(get_text("sec_references", lang), styles["section_heading"]))
    story.append(Spacer(1, 4 * mm))
    for idx, ref in enumerate(report.references, start=1):
        title = xml_escape(ref.get("title", "Untitled"))
        url = ref.get("url", "").replace("&", "&amp;")
        snippet = xml_escape(ref.get("snippet", ""))
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

    logger.info("PDF generated in language '%s': %s", lang, filepath)
    return str(filepath)
