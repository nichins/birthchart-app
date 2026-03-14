"""
PDF Generator for Kundli Report
Renders South Indian style birth charts and generates a clean PDF report.
Uses ReportLab for PDF generation.
Kannada title and shloka are embedded as pre-rendered static PNG images.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from io import BytesIO
from vedic_calc import KundliData, RASHI_NAMES, calculate_navamsa
from PIL import Image

# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
PRIMARY = HexColor("#8B1A1A")
SECONDARY = HexColor("#D4A017")
LIGHT_BG = HexColor("#FFF8F0")
CHART_BORDER = HexColor("#8B1A1A")
CHART_LINE = HexColor("#C0A060")
TEXT_DARK = HexColor("#1A1A1A")
TEXT_MED = HexColor("#4A4A4A")
LAGNA_HIGHLIGHT = HexColor("#FFF0D0")
BORDER_COLOR = HexColor("#8B1A1A")
BORDER_INNER = HexColor("#D4A017")

# ---------------------------------------------------------------------------
# Font sizes — uniform across pages
# ---------------------------------------------------------------------------
FONT_SECTION_HEADING = 14
FONT_TABLE_HEADER = 10.5
FONT_TABLE_BODY = 10.5
FONT_LABEL = 11
FONT_VALUE = 11
FONT_SMALL_NOTE = 9.5

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GANESHA_IMG = os.path.join(BASE_DIR, "ganesha_emblem.png")
TITLE_KANNADA_IMG = os.path.join(BASE_DIR, "title_kannada.png")
SHLOKA_KANNADA_IMG = os.path.join(BASE_DIR, "shloka_kannada.png")

# ---------------------------------------------------------------------------
# Abbreviation map
# ---------------------------------------------------------------------------
GRAHA_ABBREV = {
    "Lagna": "Lg", "Surya": "Su", "Chandra": "Ch", "Mangal": "Ma",
    "Budha": "Bu", "Guru": "Gu", "Shukra": "Sk", "Shani": "Sa",
    "Rahu": "Ra", "Ketu": "Ke",
}

# ---------------------------------------------------------------------------
# South Indian Chart Grid
# ---------------------------------------------------------------------------
SOUTH_INDIAN_GRID = {
    (0, 0): 11, (0, 1): 0, (0, 2): 1, (0, 3): 2,
    (1, 0): 10, (1, 3): 3,
    (2, 0): 9,  (2, 3): 4,
    (3, 0): 8,  (3, 1): 7, (3, 2): 6, (3, 3): 5,
}
RASHI_TO_GRID = {v: k for k, v in SOUTH_INDIAN_GRID.items()}




# ---------------------------------------------------------------------------
# Decorative Indian border
# ---------------------------------------------------------------------------
def _draw_page_border(c, page_width, page_height):
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(3)
    c.rect(8, 8, page_width - 16, page_height - 16)

    c.setStrokeColor(BORDER_INNER)
    c.setLineWidth(1)
    c.rect(14, 14, page_width - 28, page_height - 28)

    corner_size = 6
    corners = [
        (8, 8), (page_width - 14, 8),
        (8, page_height - 14),
        (page_width - 14, page_height - 14)
    ]
    c.setFillColor(SECONDARY)
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(1)
    for cx, cy in corners:
        c.rect(cx, cy, corner_size, corner_size, fill=1, stroke=1)

    c.setFillColor(SECONDARY)
    dot_spacing = 18
    for x_pos in range(30, int(page_width - 30), dot_spacing):
        c.circle(x_pos, page_height - 11, 1.2, fill=1, stroke=0)
        c.circle(x_pos, 11, 1.2, fill=1, stroke=0)
    for y_pos in range(30, int(page_height - 30), dot_spacing):
        c.circle(11, y_pos, 1.2, fill=1, stroke=0)
        c.circle(page_width - 11, y_pos, 1.2, fill=1, stroke=0)


# ---------------------------------------------------------------------------
# Draw South Indian Chart
# ---------------------------------------------------------------------------
def draw_south_indian_chart(c, x, y, size, rashi_grahas, lagna_rashi, title=""):
    cell_w = size / 4
    cell_h = size / 4

    c.setStrokeColor(CHART_BORDER)
    c.setLineWidth(2)
    c.rect(x, y, size, size)

    c.setLineWidth(1)
    c.setStrokeColor(CHART_LINE)
    for row in range(1, 4):
        c.line(x, y + row * cell_h, x + size, y + row * cell_h)
    for col in range(1, 4):
        c.line(x + col * cell_w, y, x + col * cell_w, y + size)

    c.setFillColor(white)
    c.setStrokeColor(CHART_LINE)
    c.setLineWidth(1)
    c.rect(x + cell_w, y + cell_h, cell_w * 2, cell_h * 2, fill=1)

    if title:
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + size / 2, y + size / 2 + 3, title)

    if lagna_rashi in RASHI_TO_GRID:
        row, col = RASHI_TO_GRID[lagna_rashi]
        bx = x + col * cell_w
        by = y + (3 - row) * cell_h
        c.setFillColor(LAGNA_HIGHLIGHT)
        c.rect(bx, by, cell_w, cell_h, fill=1, stroke=0)
        # Ear mark (outline triangle) in top-left corner of Lagna box
        ear = min(cell_w, cell_h) * 0.15
        p = c.beginPath()
        p.moveTo(bx, by + cell_h)            # top-left corner
        p.lineTo(bx + ear, by + cell_h)      # along top edge
        p.lineTo(bx, by + cell_h - ear)      # along left edge
        p.close()
        c.setStrokeColor(PRIMARY)
        c.setLineWidth(1.5)
        c.drawPath(p, fill=0, stroke=1)

    for (row, col), rashi_idx in SOUTH_INDIAN_GRID.items():
        bx = x + col * cell_w
        by = y + (3 - row) * cell_h

        # Rashi name — bottom-aligned in the box
        c.setFillColor(TEXT_MED)
        c.setFont("Helvetica", 7)
        c.drawString(bx + 2, by + 3, RASHI_NAMES[rashi_idx])

        # Planet abbreviations — wrap within cell boundaries
        planets = rashi_grahas.get(rashi_idx, [])
        if planets:
            c.setFillColor(TEXT_DARK)
            font_name = "Helvetica-Bold"
            font_size = 8.5
            c.setFont(font_name, font_size)
            pad = 3
            max_w = cell_w - 2 * pad  # usable width inside cell
            line_h = font_size + 2  # line height with spacing

            # Build wrapped lines: greedily fit abbreviations per line
            lines = []
            current_line = []
            for p in planets:
                test = "  ".join(current_line + [p])
                tw = c.stringWidth(test, font_name, font_size)
                if tw > max_w and current_line:
                    lines.append("  ".join(current_line))
                    current_line = [p]
                else:
                    current_line.append(p)
            if current_line:
                lines.append("  ".join(current_line))

            # Vertically center the block of lines in the cell
            block_h = len(lines) * line_h
            start_y = by + cell_h / 2 + block_h / 2 - font_size
            for i, line in enumerate(lines):
                c.drawString(bx + pad, start_y - i * line_h, line)

    c.setStrokeColor(CHART_BORDER)
    c.setLineWidth(2)
    c.rect(x, y, size, size, fill=0)


# ---------------------------------------------------------------------------
# Main PDF Generation
# ---------------------------------------------------------------------------
def generate_kundli_pdf(kundli: KundliData) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    margin = 24 * mm
    content_width = page_width - 2 * margin
    half_w = content_width / 2

    # ===================================================================
    # PAGE 1
    # ===================================================================
    _draw_page_border(c, page_width, page_height)

    # --- Header Banner (taller for larger title) ---
    banner_h = 52
    c.setFillColor(PRIMARY)
    c.rect(14, page_height - 14 - banner_h, page_width - 28, banner_h, fill=1, stroke=0)

    # Kannada title — pre-rendered static PNG (white text on transparent bg)
    title_img_path = TITLE_KANNADA_IMG
    if os.path.exists(title_img_path):
        pil_img = Image.open(title_img_path)
        img_w, img_h = pil_img.size
        display_h = 38
        scale = display_h / img_h
        display_w = img_w * scale
        c.drawImage(title_img_path, (page_width - display_w) / 2,
                    page_height - 14 - banner_h + 14, display_w, display_h,
                    preserveAspectRatio=True, mask='auto')

    # Subtitle
    c.setFillColor(HexColor("#CCCCCC"))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(page_width / 2, page_height - 14 - banner_h + 5, "Vedic Birth Chart Report")

    y_pos = page_height - 14 - banner_h - 4

    # --- Ganesha Emblem (above shloka, 72pt) ---
    if os.path.exists(GANESHA_IMG):
        emblem_size = 72
        y_pos -= emblem_size
        c.drawImage(GANESHA_IMG, (page_width - emblem_size) / 2, y_pos,
                    emblem_size, emblem_size, preserveAspectRatio=True, mask='auto')
        y_pos -= 4

    # --- Shloka — pre-rendered static PNG ---
    shloka_img_path = SHLOKA_KANNADA_IMG
    if os.path.exists(shloka_img_path):
        pil_img = Image.open(shloka_img_path)
        img_w, img_h = pil_img.size
        display_w = min(310, content_width)
        scale = display_w / img_w
        display_h = img_h * scale
        y_pos -= display_h
        c.drawImage(shloka_img_path, (page_width - display_w) / 2, y_pos,
                    display_w, display_h, preserveAspectRatio=True, mask='auto')
        y_pos -= 2

    # --- Gold line ---
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(1.5)
    c.line(margin, y_pos, page_width - margin, y_pos)

    # --- Name ---
    y_pos -= 18
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, y_pos, kundli.name)

    # --- Parent Names (if provided) ---
    father = getattr(kundli, 'father_name', '')
    mother = getattr(kundli, 'mother_name', '')
    if father or mother:
        y_pos -= 14
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        parts = []
        if father:
            parts.append(f"Father: {father}")
        if mother:
            parts.append(f"Mother: {mother}")
        c.drawCentredString(page_width / 2, y_pos, "    |    ".join(parts))

    # --- Birth Details (2-column) ---
    y_pos -= 6
    details_left = [
        ("Date of Birth", kundli.birth_date.strftime("%d %B %Y")),
        ("Time of Birth", kundli.birth_time_str),
        ("Latitude", f"{kundli.latitude:.4f}"),
        ("Longitude", f"{kundli.longitude:.4f}"),
    ]
    details_right = [
        ("Day", kundli.panchang.vara),
        ("Timezone", f"{kundli.timezone_name} (UTC {kundli.utc_offset})"),
        ("Place of Birth", kundli.birth_place),
        ("Ayanamsha", f"{kundli.ayanamsa_name}: {kundli.ayanamsa:.4f}"),
    ]

    for i in range(4):
        y_pos -= 14
        lbl, val = details_left[i]
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        c.drawString(margin, y_pos, lbl)
        c.setFont("Helvetica-Bold", FONT_VALUE)
        c.setFillColor(TEXT_DARK)
        c.drawString(margin + 90, y_pos, val)

        lbl, val = details_right[i]
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        c.drawString(margin + half_w + 10, y_pos, lbl)
        c.setFont("Helvetica-Bold", FONT_VALUE)
        c.setFillColor(TEXT_DARK)
        c.drawString(margin + half_w + 85, y_pos, val)

    # --- Gold line ---
    y_pos -= 10
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, y_pos, page_width - margin, y_pos)

    # --- Panchang Section ---
    y_pos -= 16
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Panchang Details")

    # Build Masa display string
    masa_display = kundli.panchang.masa
    if kundli.panchang.masa_is_adhika:
        masa_display = f"Adhika {masa_display}"

    panchang_left = [
        ("Vara", kundli.panchang.vara),
        ("Tithi", f"{kundli.panchang.paksha} {kundli.panchang.tithi_name}"),
        ("Nakshatra", f"{kundli.panchang.nakshatra_name}, Pada {kundli.panchang.nakshatra_pada}"),
        ("Yoga", kundli.panchang.yoga_name),
        ("Karana", kundli.panchang.karana_name),
    ]
    panchang_right = [
        ("Samvatsara", kundli.panchang.samvatsara),
        ("Masa", masa_display),
        ("Paksha", kundli.panchang.paksha),
        ("Ayana", kundli.panchang.ayana),
        ("Rutu", kundli.panchang.rutu),
    ]

    for i in range(5):
        y_pos -= 14
        if i % 2 == 0:
            c.setFillColor(LIGHT_BG)
            c.rect(margin, y_pos - 3, content_width, 14, fill=1, stroke=0)
        lbl, val = panchang_left[i]
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        c.drawString(margin + 4, y_pos, lbl)
        c.setFont("Helvetica-Bold", FONT_VALUE)
        c.setFillColor(TEXT_DARK)
        c.drawString(margin + 90, y_pos, val)

        lbl, val = panchang_right[i]
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        c.drawString(margin + half_w + 10, y_pos, lbl)
        c.setFont("Helvetica-Bold", FONT_VALUE)
        c.setFillColor(TEXT_DARK)
        c.drawString(margin + half_w + 95, y_pos, val)

    # --- Gold line ---
    y_pos -= 10
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, y_pos, page_width - margin, y_pos)

    # --- Key Indicators (4 boxes) ---
    y_pos -= 16
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Key Indicators")

    y_pos -= 24
    indicators = [
        ("Lagna", f"{kundli.lagna.rashi_name} ({kundli.lagna.degree_str})"),
        ("Chandra Nakshatra", f"{kundli.panchang.nakshatra_name}, Pada {kundli.panchang.nakshatra_pada}"),
        ("Chandra Rashi", kundli.grahas[1].rashi_name),
        ("Surya Rashi", kundli.grahas[0].rashi_name),
    ]

    box_width = content_width / 2
    for i, (label, value) in enumerate(indicators):
        col = i % 2
        if i == 2:
            y_pos -= 28
        bx = margin + col * box_width
        c.setFillColor(LIGHT_BG)
        c.setStrokeColor(CHART_LINE)
        c.setLineWidth(0.5)
        c.roundRect(bx + 2, y_pos - 3, box_width - 8, 24, 3, fill=1, stroke=1)
        c.setFont("Helvetica", 7)
        c.setFillColor(TEXT_MED)
        c.drawString(bx + 8, y_pos + 11, label)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(TEXT_DARK)
        c.drawString(bx + 8, y_pos + 1, value)

    # --- Gold line ---
    y_pos -= 10
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, y_pos, page_width - margin, y_pos)

    # --- Nakshatra Details (no symbol) ---
    y_pos -= 16
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Nakshatra Details")

    nak_data = [
        ("Nakshatra", f"{kundli.panchang.nakshatra_name}, Pada {kundli.panchang.nakshatra_pada}"),
        ("Nakshatra Lord", kundli.panchang.nakshatra_lord),
        ("Deity", getattr(kundli, 'nakshatra_deity', '-')),
        ("Gana", getattr(kundli, 'nakshatra_gana', '-')),
        ("Nadi", getattr(kundli, 'nakshatra_nadi', '-')),
    ]

    for i, (lbl, val) in enumerate(nak_data):
        y_pos -= 14
        if i % 2 == 0:
            c.setFillColor(LIGHT_BG)
            c.rect(margin, y_pos - 3, content_width, 14, fill=1, stroke=0)
        c.setFont("Helvetica", FONT_LABEL)
        c.setFillColor(TEXT_MED)
        c.drawString(margin + 4, y_pos, lbl)
        c.setFont("Helvetica-Bold", FONT_VALUE)
        c.setFillColor(TEXT_DARK)
        c.drawString(margin + 110, y_pos, val)

    # --- Gold line ---
    y_pos -= 10
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, y_pos, page_width - margin, y_pos)


    # --- Generation timestamp footnote ---
    from datetime import datetime as _dt
    _now = _dt.now().strftime("%d %b %Y, %I:%M %p")
    c.setFillColor(TEXT_MED)
    c.setFont("Helvetica", 6)
    c.drawRightString(page_width - 20, 20, f"Generated on {_now}")

    c.showPage()

    # ===================================================================
    # PAGE 2: Planetary Positions + Charts + Dasha
    # ===================================================================
    _draw_page_border(c, page_width, page_height)

    # --- Header ---
    banner_h2 = 40
    c.setFillColor(PRIMARY)
    c.rect(14, page_height - 14 - banner_h2, page_width - 28, banner_h2, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2, page_height - 14 - banner_h2 + 18, "Graha Sthiti & Vimshottari Dasha")
    c.setFont("Helvetica", 8)
    c.setFillColor(white)
    c.drawCentredString(page_width / 2, page_height - 14 - banner_h2 + 6, kundli.name)

    y_pos = page_height - 14 - banner_h2 - 10

    # --- 3 lines of space before content ---
    y_pos -= 42

    # --- Planetary Positions Table ---
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Sidereal Planetary Positions (Nirayana)")

    y_pos -= 4

    headers = ["Graha", "Abbr.", "Rashi", "Rashi Lord", "Degree", "Nakshatra", "Nak. Lord", "Pada", "Dignity"]
    col_widths = [58, 28, 58, 52, 56, 88, 52, 26, 41]
    NIRAYANA_FONT_HDR = 8.5
    NIRAYANA_FONT_BODY = 8.5
    NIRAYANA_ROW_H = 12

    y_pos -= NIRAYANA_ROW_H
    c.setFillColor(PRIMARY)
    c.rect(margin, y_pos - 3, content_width, NIRAYANA_ROW_H, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", NIRAYANA_FONT_HDR)
    x_offset = margin
    for i, header in enumerate(headers):
        c.drawString(x_offset + 2, y_pos, header)
        x_offset += col_widths[i]

    all_bodies = [kundli.lagna] + kundli.grahas
    for idx, body in enumerate(all_bodies):
        y_pos -= NIRAYANA_ROW_H
        if idx % 2 == 0:
            c.setFillColor(LIGHT_BG)
        else:
            c.setFillColor(white)
        c.rect(margin, y_pos - 3, content_width, NIRAYANA_ROW_H, fill=1, stroke=0)

        retro_mark = " (R)" if body.is_retrograde else ""
        dignity_str = body.dignity if body.dignity else "-"
        abbrev = GRAHA_ABBREV.get(body.name, "?")

        row_data = [
            body.name + retro_mark, abbrev, body.rashi_name,
            body.rashi_lord, body.degree_str, body.nakshatra_name,
            body.nakshatra_lord, str(body.pada), dignity_str
        ]

        x_offset = margin
        for i, val in enumerate(row_data):
            if i == 0:
                c.setFont("Helvetica-Bold", NIRAYANA_FONT_BODY)
                c.setFillColor(TEXT_DARK)
            elif i == 1:
                c.setFont("Helvetica-Bold", NIRAYANA_FONT_BODY)
                c.setFillColor(PRIMARY)
            else:
                c.setFont("Helvetica", NIRAYANA_FONT_BODY)
                c.setFillColor(TEXT_DARK)
            c.drawString(x_offset + 2, y_pos, val)
            x_offset += col_widths[i]

    y_pos -= 10
    c.setFont("Helvetica-Oblique", FONT_SMALL_NOTE)
    c.setFillColor(TEXT_MED)
    c.drawString(margin, y_pos, "Abbr. = chart label.  (R) = Vakri (retrograde).")

    # --- Gold line ---
    y_pos -= 6
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, y_pos, page_width - margin, y_pos)

    # --- Charts Section ---
    y_pos -= 14
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Birth Charts")

    navamsa_map = calculate_navamsa(kundli.grahas, kundli.lagna)

    chart_size = 190
    # Center the two charts with a gap between them
    gap = 20
    total_charts_width = chart_size * 2 + gap
    chart_x_start = (page_width - total_charts_width) / 2

    chart_y = y_pos - chart_size - 8
    chart_x = chart_x_start

    draw_south_indian_chart(
        c, chart_x, chart_y, chart_size,
        kundli.rashi_grahas, kundli.lagna.rashi_index,
        title="Rashi"
    )

    nav_chart_x = chart_x + chart_size + gap
    navamsa_lagna_rashi = None
    for rashi_idx, planets in navamsa_map.items():
        if "Lg" in planets:
            navamsa_lagna_rashi = rashi_idx
            break
    if navamsa_lagna_rashi is None:
        navamsa_lagna_rashi = 0

    draw_south_indian_chart(
        c, nav_chart_x, chart_y, chart_size,
        navamsa_map, navamsa_lagna_rashi,
        title="Navamsha"
    )

    # Chart labels
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(PRIMARY)
    c.drawCentredString(chart_x + chart_size / 2, chart_y - 10, "Rashi (D1)")
    c.drawCentredString(nav_chart_x + chart_size / 2, chart_y - 10, "Navamsha (D9)")

    # Legend (Lagna indicator only)
    legend_y = chart_y - 20
    c.setFillColor(LAGNA_HIGHLIGHT)
    c.rect(margin, legend_y - 1, 8, 8, fill=1, stroke=1)
    c.setFillColor(TEXT_MED)
    c.setFont("Helvetica", FONT_SMALL_NOTE)
    c.drawString(margin + 12, legend_y, "= Lagna Rashi (highlighted box with ear mark)")

    # --- Gold line ---
    legend_y -= 8
    c.setStrokeColor(SECONDARY)
    c.setLineWidth(0.5)
    c.line(margin, legend_y, page_width - margin, legend_y)

    # ===================================================================
    # DASHA TABLE
    # ===================================================================
    y_pos = legend_y - 14
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", FONT_SECTION_HEADING)
    c.drawString(margin, y_pos, "Vimshottari Maha Dasha")

    y_pos -= 4

    dasha_headers = ["Dasha Lord", "Start Date", "End Date", "Duration"]
    dasha_col_widths = [95, 125, 125, 95]

    y_pos -= 13
    c.setFillColor(PRIMARY)
    c.rect(margin, y_pos - 3, content_width, 13, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", FONT_TABLE_HEADER)
    x_offset = margin
    for i, header in enumerate(dasha_headers):
        c.drawString(x_offset + 4, y_pos, header)
        x_offset += dasha_col_widths[i]

    from datetime import datetime
    now = datetime.now()

    for idx, dp in enumerate(kundli.dasha_periods):
        y_pos -= 13

        is_current = dp.start_date <= now <= dp.end_date
        if is_current:
            c.setFillColor(HexColor("#E8F5E9"))
        elif idx % 2 == 0:
            c.setFillColor(LIGHT_BG)
        else:
            c.setFillColor(white)
        c.rect(margin, y_pos - 3, content_width, 13, fill=1, stroke=0)

        if is_current:
            c.setFillColor(HexColor("#2E7D32"))
            c.setFont("Helvetica-Bold", 5)
            c.drawRightString(margin + dasha_col_widths[0] - 4, y_pos + 5, "(Current)")

        years = int(dp.years)
        months = int((dp.years - years) * 12)
        duration_str = f"{years} yrs" if months == 0 else f"{years} yrs {months} mo"

        row_data = [
            dp.lord,
            dp.start_date.strftime("%d %b %Y"),
            dp.end_date.strftime("%d %b %Y"),
            duration_str
        ]

        c.setFillColor(TEXT_DARK)
        x_offset = margin
        for i, val in enumerate(row_data):
            if i == 0:
                c.setFont("Helvetica-Bold", FONT_TABLE_BODY)
            else:
                c.setFont("Helvetica", FONT_TABLE_BODY)
            c.drawString(x_offset + 4, y_pos, val)
            x_offset += dasha_col_widths[i]



    # --- Generation timestamp footnote ---
    from datetime import datetime as _dt
    _now = _dt.now().strftime("%d %b %Y, %I:%M %p")
    c.setFillColor(TEXT_MED)
    c.setFont("Helvetica", 6)
    c.drawRightString(page_width - 20, 20, f"Generated on {_now}")

    c.showPage()

    # ===================================================================
    # Finalize
    # ===================================================================
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
