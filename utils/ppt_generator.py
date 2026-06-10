"""
DeepDive AI — PowerPoint Presentation Generator

Generates a 5+ slide PPTX from a ResearchReport using python-pptx.

Slide layout:
  Slide 1 — Title slide (topic name + date)
  Slide 2 — Executive Summary
  Slide 3 — Key Insights (bullet points)
  Slide 4 — Statistics & Data (table)
  Slide 5 — References & Citations
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from utils.report_schema import ResearchReport

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Brand colours
_PRIMARY = RGBColor(0x1A, 0x23, 0x7E)   # Deep indigo
_ACCENT = RGBColor(0x0D, 0x47, 0xA1)    # Dark blue
_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
_DARK_TEXT = RGBColor(0x21, 0x21, 0x21)
_GRAY_TEXT = RGBColor(0x61, 0x61, 0x61)
_LIGHT_BG = RGBColor(0xE8, 0xEA, 0xF6)  # Lavender


def sanitise_filename(topic: str) -> str:
    """Replace non-alphanumeric characters with underscores and truncate."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_").lower()
    return clean[:80] if len(clean) > 80 else clean


def _set_slide_bg(slide, color: RGBColor) -> None:
    """Set a solid background colour for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_textbox(
    slide,
    left: Inches,
    top: Inches,
    width: Inches,
    height: Inches,
    text: str,
    font_size: int = 16,
    bold: bool = False,
    color: RGBColor = _DARK_TEXT,
    alignment: PP_ALIGN = PP_ALIGN.LEFT,
) -> None:
    """Add a simple text box to a slide."""
    tx_box = slide.shapes.add_textbox(left, top, width, height)
    tf = tx_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = alignment


def build_ppt(report: ResearchReport) -> str:
    """Generate a 5+ slide PPTX and return the filepath.

    Parameters
    ----------
    report : ResearchReport
        A validated research report dataclass.

    Returns
    -------
    str
        Absolute path to the generated PPTX file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{sanitise_filename(report.topic)}_presentation.pptx"
    filepath = OUTPUT_DIR / filename
    date_str = datetime.now().strftime("%B %d, %Y")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ── Slide 1: Title Slide ─────────────────────────────────────────
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    _set_slide_bg(slide, _PRIMARY)

    # App name
    _add_textbox(
        slide,
        Inches(1), Inches(1.5), Inches(11), Inches(0.8),
        "🔬 DeepDive AI",
        font_size=20, color=_LIGHT_BG, alignment=PP_ALIGN.CENTER,
    )
    # Topic title
    _add_textbox(
        slide,
        Inches(1), Inches(2.5), Inches(11), Inches(2),
        report.topic,
        font_size=36, bold=True, color=_WHITE, alignment=PP_ALIGN.CENTER,
    )
    # Subtitle
    _add_textbox(
        slide,
        Inches(1), Inches(4.8), Inches(11), Inches(0.6),
        "AI-Generated Research Report",
        font_size=18, color=_LIGHT_BG, alignment=PP_ALIGN.CENTER,
    )
    # Date
    _add_textbox(
        slide,
        Inches(1), Inches(5.6), Inches(11), Inches(0.5),
        date_str,
        font_size=14, color=_LIGHT_BG, alignment=PP_ALIGN.CENTER,
    )

    # ── Slide 2: Executive Summary ───────────────────────────────────
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, _WHITE)

    _add_textbox(
        slide,
        Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "Executive Summary",
        font_size=28, bold=True, color=_PRIMARY,
    )

    # Summary body
    tx_box = slide.shapes.add_textbox(
        Inches(0.8), Inches(1.6), Inches(11.5), Inches(5)
    )
    tf = tx_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = report.executive_summary
    p.font.size = Pt(16)
    p.font.color.rgb = _DARK_TEXT
    p.line_spacing = Pt(24)

    # ── Slide 3: Key Insights ────────────────────────────────────────
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, _WHITE)

    _add_textbox(
        slide,
        Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "Key Insights",
        font_size=28, bold=True, color=_PRIMARY,
    )

    tx_box = slide.shapes.add_textbox(
        Inches(0.8), Inches(1.6), Inches(11.5), Inches(5.2)
    )
    tf = tx_box.text_frame
    tf.word_wrap = True

    for idx, insight in enumerate(report.key_insights):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = f"▸  {insight}"
        p.font.size = Pt(15)
        p.font.color.rgb = _DARK_TEXT
        p.space_after = Pt(10)
        p.line_spacing = Pt(22)

    # ── Slide 4: Statistics & Data ───────────────────────────────────
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, _WHITE)

    _add_textbox(
        slide,
        Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "Statistics & Data",
        font_size=28, bold=True, color=_PRIMARY,
    )

    # Build table
    rows = len(report.statistics) + 1  # header + data
    cols = 2
    tbl = slide.shapes.add_table(
        rows, cols,
        Inches(1.2), Inches(1.8), Inches(10.5), Inches(0.5 * rows + 0.4),
    ).table

    tbl.columns[0].width = Inches(5.5)
    tbl.columns[1].width = Inches(5)

    # Header row
    for col_idx, header in enumerate(["Metric", "Value"]):
        cell = tbl.cell(0, col_idx)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = _PRIMARY
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(14)
            paragraph.font.bold = True
            paragraph.font.color.rgb = _WHITE

    # Data rows
    for row_idx, stat in enumerate(report.statistics, start=1):
        label_cell = tbl.cell(row_idx, 0)
        value_cell = tbl.cell(row_idx, 1)

        label_cell.text = stat.get("label", "")
        value_cell.text = stat.get("value", "")

        # Alternate row shading
        if row_idx % 2 == 0:
            label_cell.fill.solid()
            label_cell.fill.fore_color.rgb = _LIGHT_BG
            value_cell.fill.solid()
            value_cell.fill.fore_color.rgb = _LIGHT_BG

        for cell in (label_cell, value_cell):
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(13)
                paragraph.font.color.rgb = _DARK_TEXT

    # ── Slide 5: References & Citations ──────────────────────────────
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, _WHITE)

    _add_textbox(
        slide,
        Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "References & Citations",
        font_size=28, bold=True, color=_PRIMARY,
    )

    tx_box = slide.shapes.add_textbox(
        Inches(0.8), Inches(1.6), Inches(11.5), Inches(5.2)
    )
    tf = tx_box.text_frame
    tf.word_wrap = True

    for idx, ref in enumerate(report.references):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()

        title = ref.get("title", "Untitled")
        url = ref.get("url", "")
        snippet = ref.get("snippet", "")

        p.text = f"{idx + 1}. {title}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = _ACCENT
        p.space_after = Pt(2)

        # URL line
        p_url = tf.add_paragraph()
        p_url.text = f"   {url}"
        p_url.font.size = Pt(11)
        p_url.font.color.rgb = _GRAY_TEXT
        p_url.space_after = Pt(1)

        # Snippet line
        p_snip = tf.add_paragraph()
        p_snip.text = f"   {snippet}"
        p_snip.font.size = Pt(12)
        p_snip.font.color.rgb = _DARK_TEXT
        p_snip.space_after = Pt(12)

    # ── Save ─────────────────────────────────────────────────────────
    prs.save(str(filepath))
    logger.info("PPTX generated: %s", filepath)
    return str(filepath)
