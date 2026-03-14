"""
Generate a clean Rashi-Nakshatra reference PDF.
Two main charts:
  1. Rashi Chakram (South Indian style grid) — 12 rashis with degree ranges, lords
  2. Nakshatra-in-Rashi chart — which nakshatras & padas fall in each rashi
Plus a full 27-nakshatra reference table.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

# Colour palette
DARK_RED   = HexColor("#8B1A1A")
GOLD       = HexColor("#B8860B")
LIGHT_GOLD = HexColor("#FDF5E6")
HEADER_BG  = HexColor("#8B1A1A")
ROW_ALT    = HexColor("#FFF0E0")
BORDER_CLR = HexColor("#C0A060")

# ── Data ──────────────────────────────────────────────────────────────────

RASHIS = [
    (1,  "Mesha",      "Aries",       "0° – 30°",    "Mangal"),
    (2,  "Vrishabha",  "Taurus",      "30° – 60°",   "Shukra"),
    (3,  "Mithuna",    "Gemini",      "60° – 90°",   "Budha"),
    (4,  "Karka",      "Cancer",      "90° – 120°",  "Chandra"),
    (5,  "Simha",      "Leo",         "120° – 150°", "Surya"),
    (6,  "Kanya",      "Virgo",       "150° – 180°", "Budha"),
    (7,  "Tula",       "Libra",       "180° – 210°", "Shukra"),
    (8,  "Vrishchika", "Scorpio",     "210° – 240°", "Mangal"),
    (9,  "Dhanu",      "Sagittarius", "240° – 270°", "Guru"),
    (10, "Makara",     "Capricorn",   "270° – 300°", "Shani"),
    (11, "Kumbha",     "Aquarius",    "300° – 330°", "Shani"),
    (12, "Meena",      "Pisces",      "330° – 360°", "Guru"),
]

SI_GRID = [
    [12, 1,  2,  3],
    [11, 0,  0,  4],
    [10, 0,  0,  5],
    [9,  8,  7,  6],
]

NAKSHATRA_IN_RASHI = [
    (1,  "Mesha",      [("Ashwini", "1,2,3,4"), ("Bharani", "1,2,3,4"), ("Krittika", "1")]),
    (2,  "Vrishabha",  [("Krittika", "2,3,4"), ("Rohini", "1,2,3,4"), ("Mrigashira", "1,2")]),
    (3,  "Mithuna",    [("Mrigashira", "3,4"), ("Ardra", "1,2,3,4"), ("Punarvasu", "1,2,3")]),
    (4,  "Karka",      [("Punarvasu", "4"), ("Pushya", "1,2,3,4"), ("Ashlesha", "1,2,3,4")]),
    (5,  "Simha",      [("Magha", "1,2,3,4"), ("Purva Phalguni", "1,2,3,4"), ("Uttara Phalguni", "1")]),
    (6,  "Kanya",      [("Uttara Phalguni", "2,3,4"), ("Hasta", "1,2,3,4"), ("Chitra", "1,2")]),
    (7,  "Tula",       [("Chitra", "3,4"), ("Swati", "1,2,3,4"), ("Vishakha", "1,2,3")]),
    (8,  "Vrishchika", [("Vishakha", "4"), ("Anuradha", "1,2,3,4"), ("Jyeshtha", "1,2,3,4")]),
    (9,  "Dhanu",      [("Moola", "1,2,3,4"), ("Purva Ashadha", "1,2,3,4"), ("Uttara Ashadha", "1")]),
    (10, "Makara",     [("Uttara Ashadha", "2,3,4"), ("Shravana", "1,2,3,4"), ("Dhanishta", "1,2")]),
    (11, "Kumbha",     [("Dhanishta", "3,4"), ("Shatabhisha", "1,2,3,4"), ("Purva Bhadrapada", "1,2,3")]),
    (12, "Meena",      [("Purva Bhadrapada", "4"), ("Uttara Bhadrapada", "1,2,3,4"), ("Revati", "1,2,3,4")]),
]

NAKSHATRAS_27 = [
    (1,  "Ashwini",            "Ketu",    "0°00'",   "13°20'",  "Mesha"),
    (2,  "Bharani",            "Shukra",  "13°20'",  "26°40'",  "Mesha"),
    (3,  "Krittika",           "Surya",   "26°40'",  "40°00'",  "Mesha – Vrishabha"),
    (4,  "Rohini",             "Chandra", "40°00'",  "53°20'",  "Vrishabha"),
    (5,  "Mrigashira",         "Mangal",  "53°20'",  "66°40'",  "Vrishabha – Mithuna"),
    (6,  "Ardra",              "Rahu",    "66°40'",  "80°00'",  "Mithuna"),
    (7,  "Punarvasu",          "Guru",    "80°00'",  "93°20'",  "Mithuna – Karka"),
    (8,  "Pushya",             "Shani",   "93°20'",  "106°40'", "Karka"),
    (9,  "Ashlesha",           "Budha",   "106°40'", "120°00'", "Karka"),
    (10, "Magha",              "Ketu",    "120°00'", "133°20'", "Simha"),
    (11, "Purva Phalguni",     "Shukra",  "133°20'", "146°40'", "Simha"),
    (12, "Uttara Phalguni",    "Surya",   "146°40'", "160°00'", "Simha – Kanya"),
    (13, "Hasta",              "Chandra", "160°00'", "173°20'", "Kanya"),
    (14, "Chitra",             "Mangal",  "173°20'", "186°40'", "Kanya – Tula"),
    (15, "Swati",              "Rahu",    "186°40'", "200°00'", "Tula"),
    (16, "Vishakha",           "Guru",    "200°00'", "213°20'", "Tula – Vrishchika"),
    (17, "Anuradha",           "Shani",   "213°20'", "226°40'", "Vrishchika"),
    (18, "Jyeshtha",           "Budha",   "226°40'", "240°00'", "Vrishchika"),
    (19, "Moola",              "Ketu",    "240°00'", "253°20'", "Dhanu"),
    (20, "Purva Ashadha",      "Shukra",  "253°20'", "266°40'", "Dhanu"),
    (21, "Uttara Ashadha",     "Surya",   "266°40'", "280°00'", "Dhanu – Makara"),
    (22, "Shravana",           "Chandra", "280°00'", "293°20'", "Makara"),
    (23, "Dhanishta",          "Mangal",  "293°20'", "306°40'", "Makara – Kumbha"),
    (24, "Shatabhisha",        "Rahu",    "306°40'", "320°00'", "Kumbha"),
    (25, "Purva Bhadrapada",   "Guru",    "320°00'", "333°20'", "Kumbha – Meena"),
    (26, "Uttara Bhadrapada",  "Shani",   "333°20'", "346°40'", "Meena"),
    (27, "Revati",             "Budha",   "346°40'", "360°00'", "Meena"),
]


def draw_title_banner(c, y, text, width):
    banner_h = 14 * mm
    c.setFillColor(HEADER_BG)
    c.roundRect(MARGIN, y - banner_h, width - 2 * MARGIN, banner_h, 3, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y - banner_h + 4 * mm, text)
    return y - banner_h - 4 * mm


def draw_subtitle(c, y, text):
    c.setFillColor(DARK_RED)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN, y, text)
    return y - 5 * mm


def draw_south_indian_rashi_chart(c, y_top):
    """Draw the South Indian style Rashi Chakram grid — no background fills."""
    grid_size = 140 * mm
    cell_w = grid_size / 4
    cell_h = grid_size / 4
    x_start = (PAGE_W - grid_size) / 2
    y_start = y_top

    # Outer border
    c.setStrokeColor(DARK_RED)
    c.setLineWidth(2)
    c.rect(x_start, y_start - grid_size, grid_size, grid_size, fill=0, stroke=1)

    # Inner grid lines — only the outer ring cells
    c.setStrokeColor(BORDER_CLR)
    c.setLineWidth(1)
    # Top row and bottom row: full horizontal dividers
    for row in [1, 3]:
        c.line(x_start, y_start - row * cell_h, x_start + grid_size, y_start - row * cell_h)
    # Middle rows: left and right segments only
    for row in [2]:
        c.line(x_start, y_start - row * cell_h, x_start + cell_w, y_start - row * cell_h)
        c.line(x_start + 3 * cell_w, y_start - row * cell_h, x_start + grid_size, y_start - row * cell_h)
    # Vertical lines: top and bottom strips full, middle strips left/right only
    for col in range(1, 4):
        c.line(x_start + col * cell_w, y_start, x_start + col * cell_w, y_start - cell_h)
        c.line(x_start + col * cell_w, y_start - 3 * cell_h, x_start + col * cell_w, y_start - grid_size)
    for col in [1, 3]:
        c.line(x_start + col * cell_w, y_start - cell_h, x_start + col * cell_w, y_start - 3 * cell_h)

    # Center text
    cx = x_start + grid_size / 2
    cy = y_start - grid_size / 2
    c.setFillColor(DARK_RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(cx, cy + 8, "RASHI CHAKRAM")
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, cy - 4, "0° to 360°")
    c.drawCentredString(cx, cy - 15, "12 Rashis × 30° each")

    # Fill rashi info in each cell
    rashi_lookup = {r[0]: r for r in RASHIS}
    for row in range(4):
        for col in range(4):
            rnum = SI_GRID[row][col]
            if rnum == 0:
                continue
            r = rashi_lookup[rnum]
            cx = x_start + col * cell_w + cell_w / 2
            cy = y_start - row * cell_h - cell_h / 2

            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, cy + 12, f"{r[0]}")

            c.setFillColor(DARK_RED)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawCentredString(cx, cy + 1, r[1])

            c.setFillColor(HexColor("#555555"))
            c.setFont("Helvetica", 7.5)
            c.drawCentredString(cx, cy - 9, f"({r[2]})")

            c.setFillColor(HexColor("#666666"))
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, cy - 19, r[3])

    return y_start - grid_size - 6 * mm


def draw_nakshatra_rashi_chart(c, y_top):
    """Draw the Nakshatra-in-Rashi chart — no background fills."""
    grid_size = 156 * mm
    cell_w = grid_size / 4
    cell_h = grid_size / 4
    x_start = (PAGE_W - grid_size) / 2
    y_start = y_top

    # Outer border
    c.setStrokeColor(DARK_RED)
    c.setLineWidth(2)
    c.rect(x_start, y_start - grid_size, grid_size, grid_size, fill=0, stroke=1)

    # Inner grid lines
    c.setStrokeColor(BORDER_CLR)
    c.setLineWidth(1)
    for row in [1, 3]:
        c.line(x_start, y_start - row * cell_h, x_start + grid_size, y_start - row * cell_h)
    for row in [2]:
        c.line(x_start, y_start - row * cell_h, x_start + cell_w, y_start - row * cell_h)
        c.line(x_start + 3 * cell_w, y_start - row * cell_h, x_start + grid_size, y_start - row * cell_h)
    for col in range(1, 4):
        c.line(x_start + col * cell_w, y_start, x_start + col * cell_w, y_start - cell_h)
        c.line(x_start + col * cell_w, y_start - 3 * cell_h, x_start + col * cell_w, y_start - grid_size)
    for col in [1, 3]:
        c.line(x_start + col * cell_w, y_start - cell_h, x_start + col * cell_w, y_start - 3 * cell_h)

    # Center label
    cx = x_start + grid_size / 2
    cy = y_start - grid_size / 2
    c.setFillColor(DARK_RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(cx, cy + 12, "NAKSHATRA")
    c.drawCentredString(cx, cy, "IN RASHI")
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, cy - 14, "27 Nakshatras × 4 Padas")
    c.drawCentredString(cx, cy - 25, "= 108 Padas")

    # Fill each cell — vertically centered
    nak_lookup = {n[0]: n for n in NAKSHATRA_IN_RASHI}
    title_font_size = 8.5
    body_font_size = 6.8
    body_line_spacing = 9
    title_gap = 4  # gap between title and first body line

    for row in range(4):
        for col in range(4):
            rnum = SI_GRID[row][col]
            if rnum == 0:
                continue
            entry = nak_lookup[rnum]
            rashi_name = entry[1]
            nakshatras = entry[2]

            cx = x_start + col * cell_w + cell_w / 2
            cell_cy = y_start - row * cell_h - cell_h / 2  # vertical center of cell

            # Calculate total block height: title + gap + body lines
            n_body_lines = len(nakshatras)
            block_h = title_font_size + title_gap + (n_body_lines - 1) * body_line_spacing + body_font_size
            block_top = cell_cy + block_h / 2

            # Draw title (rashi name)
            c.setFillColor(DARK_RED)
            c.setFont("Helvetica-Bold", title_font_size)
            c.drawCentredString(cx, block_top - title_font_size, f"{rashi_name} ({rnum})")

            # Draw body lines (nakshatra + padas)
            c.setFont("Helvetica", body_font_size)
            line_y = block_top - title_font_size - title_gap - body_font_size
            for nak_name, padas in nakshatras:
                c.setFillColor(HexColor("#333333"))
                c.drawCentredString(cx, line_y, f"{nak_name} {padas}")
                line_y -= body_line_spacing

    return y_start - grid_size - 6 * mm


def draw_nakshatra_table(c, y_top):
    header = ["#", "Nakshatra", "Lord", "Start", "End", "Rashi(s)"]
    data = [header]
    for n in NAKSHATRAS_27:
        data.append([str(n[0]), n[1], n[2], n[3], n[4], n[5]])

    col_widths = [18, 105, 42, 48, 48, 110]
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ROW_ALT]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    tw, th = t.wrap(0, 0)
    t.drawOn(c, (PAGE_W - tw) / 2, y_top - th)
    return y_top - th - 4 * mm


def draw_rashi_table(c, y_top):
    header = ["#", "Rashi", "English", "Degrees", "Lord"]
    data = [header]
    for r in RASHIS:
        data.append([str(r[0]), r[1], r[2], r[3], r[4]])

    col_widths = [20, 70, 70, 75, 50]
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, ROW_ALT]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    tw, th = t.wrap(0, 0)
    t.drawOn(c, (PAGE_W - tw) / 2, y_top - th)
    return y_top - th - 4 * mm


def draw_footer(c, page_num):
    c.setFillColor(HexColor("#999999"))
    c.setFont("Helvetica", 7)
    c.drawCentredString(PAGE_W / 2, 10 * mm, f"Rashi & Nakshatra Quick Reference  —  Page {page_num}")


def generate_reference_pdf_bytes():
    """Generate the reference PDF and return it as bytes (for Streamlit download)."""
    import io
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _build_pages(c)
    c.save()
    buf.seek(0)
    return buf.getvalue()


def _build_pages(c):

    # PAGE 1 — Rashi Chakram + Rashi Table
    y = PAGE_H - MARGIN
    y = draw_title_banner(c, y, "Rashi & Nakshatra Quick Reference", PAGE_W)
    y -= 2 * mm
    y = draw_subtitle(c, y, "1. Rashi Chakram (South Indian Layout)")
    y -= 1 * mm
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "The zodiac of 360° is divided into 12 rashis of 30° each. Numbering begins at Mesha (0°) and proceeds clockwise.")
    y -= 5 * mm
    y = draw_south_indian_rashi_chart(c, y)
    y -= 1 * mm
    y = draw_subtitle(c, y, "12 Rashis with Lords")
    y -= 1 * mm
    y = draw_rashi_table(c, y)
    draw_footer(c, 1)
    c.showPage()

    # PAGE 2 — Nakshatra-in-Rashi Chart
    y = PAGE_H - MARGIN
    y = draw_title_banner(c, y, "Rashi & Nakshatra Quick Reference", PAGE_W)
    y -= 2 * mm
    y = draw_subtitle(c, y, "2. Nakshatras in Each Rashi (South Indian Layout)")
    y -= 1 * mm
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "Each 30° rashi contains 2¼ nakshatras (each nakshatra = 13°20', each pada = 3°20'). Total: 27 × 4 = 108 padas.")
    y -= 8 * mm
    y = draw_nakshatra_rashi_chart(c, y)
    y -= 2 * mm
    c.setFillColor(DARK_RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN, y, "Note:")
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN + 25, y, "Nakshatras that span two rashis are split across the boundary. E.g., Krittika pada 1 is in Mesha; padas 2,3,4 are in Vrishabha.")
    draw_footer(c, 2)
    c.showPage()

    # PAGE 3 — Full 27-Nakshatra Table
    y = PAGE_H - MARGIN
    y = draw_title_banner(c, y, "Rashi & Nakshatra Quick Reference", PAGE_W)
    y -= 2 * mm
    y = draw_subtitle(c, y, "3. Complete Nakshatra Reference (27 Nakshatras)")
    y -= 1 * mm
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, y, "Each nakshatra spans 13°20' and has 4 padas of 3°20' each. The lord follows the Vimshottari Dasha sequence.")
    y -= 5 * mm
    y = draw_nakshatra_table(c, y)

    y -= 4 * mm
    box_h = 42
    c.setFillColor(LIGHT_GOLD)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 4, fill=1, stroke=0)
    c.setStrokeColor(BORDER_CLR)
    c.setLineWidth(0.5)
    c.roundRect(MARGIN, y - box_h, PAGE_W - 2 * MARGIN, box_h, 4, fill=0, stroke=1)
    c.setFillColor(DARK_RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN + 6, y - 12, "Vimshottari Dasha Lord Cycle (9 lords, repeats every 3 nakshatras):")
    c.setFillColor(HexColor("#333333"))
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN + 6, y - 24, "Ketu → Shukra → Surya → Chandra → Mangal → Rahu → Guru → Shani → Budha")
    c.drawString(MARGIN + 6, y - 36, "Nakshatras 1,10,19 = Ketu  |  2,11,20 = Shukra  |  3,12,21 = Surya  |  4,13,22 = Chandra  |  ... and so on.")
    draw_footer(c, 3)
    c.showPage()



def main():
    out = "/home/ubuntu/Rashi_Nakshatra_Reference.pdf"
    c = canvas.Canvas(out, pagesize=A4)
    _build_pages(c)
    c.save()
    print(f"PDF saved: {out}")


if __name__ == "__main__":
    main()
