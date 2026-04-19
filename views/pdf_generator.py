# Student Name: Omar Alfrouh
# Student ID: 24020879

import os
import sys
import subprocess
from datetime import datetime
from fpdf import FPDF

# ── Colour palette ────────────────────────────────────────────────────────────
_P_DARK   = (17,  24,  39)    # header band
_PRIMARY  = (59,  130, 246)   # section headers
_SUCCESS  = (21,  128, 61)    # paid
_WARNING  = (161, 98,  7)     # pending
_DANGER   = (185, 28,  28)    # overdue
_TEXT     = (15,  23,  42)
_MUTED    = (100, 116, 139)
_LIGHT    = (241, 245, 249)
_WHITE    = (255, 255, 255)
_BORDER   = (203, 213, 225)
_GBP      = chr(163)           # £ — safe in FPDF Latin-1 fonts


def _status_colors(status):
    s = (status or "").lower()
    if s == "paid":    return _SUCCESS
    if s == "overdue": return _DANGER
    return _WARNING


def _section_header(pdf, title, lm, cw):
    y = pdf.get_y() + 4
    pdf.set_fill_color(*_PRIMARY)
    pdf.rect(lm, y, cw, 7, "F")
    pdf.set_xy(lm + 3, y)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_WHITE)
    pdf.cell(cw - 6, 7, title)
    pdf.set_text_color(*_TEXT)
    pdf.set_y(y + 10)


def _kv(pdf, label, value, lm, cw):
    y = pdf.get_y()
    pdf.set_xy(lm + 3, y)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_MUTED)
    pdf.cell(42, 6, label + ":")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_TEXT)
    pdf.cell(cw - 48, 6, str(value) if value else "-")
    pdf.set_y(y + 6)


def generate_invoice_pdf(data, save_path):
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    W  = 210
    LM = 15
    RM = 15
    CW = W - LM - RM   # 180 mm

    # ── Header band ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*_P_DARK)
    pdf.rect(0, 0, W, 40, "F")

    pdf.set_xy(LM, 9)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*_WHITE)
    pdf.cell(90, 10, "PAMS")

    pdf.set_xy(LM, 22)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(160, 185, 220)
    pdf.cell(90, 5, "Paragon Apartment Management System")

    pdf.set_xy(W - RM - 85, 9)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*_WHITE)
    pdf.cell(85, 10, "INVOICE", align="R")

    pdf.set_xy(W - RM - 85, 22)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(160, 185, 220)
    pdf.cell(85, 5, f"# INV-{data['invoice_id']:04d}", align="R")

    pdf.set_text_color(*_TEXT)
    pdf.set_y(48)

    # ── Meta row: two boxes side by side ─────────────────────────────────────
    half = (CW - 4) / 2

    # Left box — invoice dates
    pdf.set_fill_color(*_LIGHT)
    pdf.rect(LM, 48, half, 28, "F")
    pdf.set_xy(LM + 3, 50)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*_MUTED)
    pdf.cell(half - 6, 4, "INVOICE DETAILS")
    pdf.set_y(55)
    _kv(pdf, "Issue Date", data["issue_date"],   LM, half)
    _kv(pdf, "Due Date",   data["due_date"],     LM, half)

    # Right box — amount + status badge
    rx = LM + half + 4
    pdf.set_fill_color(*_LIGHT)
    pdf.rect(rx, 48, half, 28, "F")

    sc = _status_colors(data["status"])
    pdf.set_fill_color(*sc)
    badge_w = 30
    pdf.rect(rx + half - badge_w - 3, 50, badge_w, 9, "F")
    pdf.set_xy(rx + half - badge_w - 3, 50)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_WHITE)
    pdf.cell(badge_w, 9, data["status"].upper(), align="C")

    pdf.set_xy(rx + 3, 58)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_MUTED)
    pdf.cell(half - 6, 5, "TOTAL AMOUNT", align="R")

    pdf.set_xy(rx + 3, 64)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*_TEXT)
    pdf.cell(half - 6, 10, f"{_GBP}{data['total_amount']:.2f}", align="R")

    pdf.set_text_color(*_TEXT)
    pdf.set_y(82)

    # ── Bill To ───────────────────────────────────────────────────────────────
    _section_header(pdf, "BILL TO", LM, CW)
    _kv(pdf, "Name",  data["tenant_name"], LM, CW)
    _kv(pdf, "NI No", data["ni_number"],   LM, CW)
    _kv(pdf, "Email", data["email"],       LM, CW)
    _kv(pdf, "Phone", data["phone"],       LM, CW)

    # ── Property ──────────────────────────────────────────────────────────────
    _section_header(pdf, "PROPERTY", LM, CW)
    unit_str = f"Unit {data['unit']}" if data["unit"] else None
    _kv(pdf, "Unit",    unit_str,        LM, CW)
    _kv(pdf, "Address", data["address"], LM, CW)
    _kv(pdf, "City",    data["city"],    LM, CW)

    # ── Line items ────────────────────────────────────────────────────────────
    _section_header(pdf, "CHARGES", LM, CW)

    desc_w = CW - 45
    amt_w  = 42

    y = pdf.get_y()
    pdf.set_fill_color(*_LIGHT)
    pdf.rect(LM, y, CW, 7, "F")
    pdf.set_xy(LM + 3, y)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*_MUTED)
    pdf.cell(desc_w, 7, "DESCRIPTION")
    pdf.cell(amt_w,  7, "AMOUNT", align="R")
    pdf.set_y(y + 8)

    pdf.set_xy(LM + 3, pdf.get_y())
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_TEXT)
    pdf.cell(desc_w, 7, "Monthly Rent")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(amt_w,  7, f"{_GBP}{data['total_amount']:.2f}", align="R")
    pdf.ln(7)

    # Total band
    y = pdf.get_y() + 4
    pdf.set_fill_color(*_P_DARK)
    pdf.rect(LM, y, CW, 12, "F")
    pdf.set_xy(LM + 3, y + 1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_WHITE)
    pdf.cell(desc_w + 3, 10, "TOTAL DUE")
    pdf.cell(amt_w - 3,  10, f"{_GBP}{data['total_amount']:.2f}", align="R")
    pdf.set_text_color(*_TEXT)
    pdf.set_y(y + 16)

    # ── Payment history ───────────────────────────────────────────────────────
    if data["payments"]:
        _section_header(pdf, "PAYMENT HISTORY", LM, CW)

        col_w = [35, 35, 35, CW - 108]
        hdrs  = ["AMOUNT", "DATE", "METHOD", "REFERENCE"]

        y = pdf.get_y()
        pdf.set_fill_color(*_LIGHT)
        pdf.rect(LM, y, CW, 7, "F")
        x = LM + 3
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*_MUTED)
        for h, w in zip(hdrs, col_w):
            pdf.set_xy(x, y)
            pdf.cell(w, 7, h)
            x += w
        pdf.set_y(y + 8)

        for pay in data["payments"]:
            vals = [f"{_GBP}{pay[0]:.2f}", str(pay[1]), str(pay[2]), str(pay[3]) or "—"]
            y = pdf.get_y()
            x = LM + 3
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*_TEXT)
            for val, w in zip(vals, col_w):
                pdf.set_xy(x, y)
                pdf.cell(w, 6, val)
                x += w
            pdf.set_y(y + 6)

    # ── Footer (disable auto-break so we don't spill a blank page) ───────────
    pdf.set_auto_page_break(auto=False)
    footer_y = 272
    pdf.set_draw_color(*_BORDER)
    pdf.line(LM, footer_y, W - RM, footer_y)
    pdf.set_xy(LM, footer_y + 2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*_MUTED)
    generated = datetime.now().strftime("%d %b %Y at %H:%M")
    pdf.cell(CW / 2, 4, f"Generated by PAMS  |  {generated}")
    pdf.cell(CW / 2, 4, "Paragon Apartment Management System  |  Confidential",
             align="R")

    pdf.output(save_path)


def open_file(path):
    """Open the saved PDF in the system default viewer."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass
