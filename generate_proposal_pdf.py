#!/usr/bin/env python3
"""Customer presentation PDF — Shumail portfolio redesign."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Shumail-Website-Proposal.pdf"
PORTRAIT = ROOT / "assets" / "portrait.jpg"
GALLERY = ROOT / "data" / "gallery.json"

BG = HexColor("#0d0d0d")
CARD = HexColor("#1a1a1a")
ORANGE = HexColor("#f97316")
MUTED = HexColor("#a0a0a0")
LIGHT = HexColor("#f5f5f5")
BORDER = HexColor("#2a2a2a")
W, H = A4


def load_gallery():
    if GALLERY.exists():
        return json.loads(GALLERY.read_text(encoding="utf-8"))
    return {"companies": [], "creatives": [], "categories": []}


def draw_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor("#1a1008"))
    c.circle(W * 0.15, H * 0.92, 120, fill=1, stroke=0)


def draw_footer(c, page, total):
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(20 * mm, 14 * mm, W - 20 * mm, 14 * mm)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, 8 * mm, "byshumail redesign  ·  confidential proposal")
    c.drawRightString(W - 20 * mm, 8 * mm, f"{page} / {total}")


def draw_accent_bar(c, y, width=40 * mm):
    c.setFillColor(ORANGE)
    c.roundRect(20 * mm, y, width, 3, 1.5, fill=1, stroke=0)


def page_cover(c, total, gal):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.rect(0, 0, 6 * mm, H, fill=1, stroke=0)

    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, H - 28 * mm, "WEBSITE REDESIGN PROPOSAL")

    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(20 * mm, H - 52 * mm, "Shumail Ap")
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 64 * mm, "Portfolio Website")

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, H - 76 * mm, "Content Creator · Photographer · Videographer")
    c.drawString(20 * mm, H - 84 * mm, "Dubai, UAE")
    draw_accent_bar(c, H - 92 * mm, 28 * mm)

    if PORTRAIT.exists():
        size = 95 * mm
        x = W - 20 * mm - size
        y = H - 55 * mm - size
        c.saveState()
        path = c.beginPath()
        path.circle(x + size / 2, y + size / 2, size / 2)
        c.clipPath(path, stroke=0)
        c.drawImage(
            ImageReader(str(PORTRAIT)),
            x,
            y,
            width=size,
            height=size,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        c.restoreState()
        c.setStrokeColor(ORANGE)
        c.setLineWidth(2.5)
        c.circle(x + size / 2, y + size / 2, size / 2 + 2, fill=0, stroke=1)

    card_y = 42 * mm
    c.setFillColor(CARD)
    c.roundRect(20 * mm, card_y, W - 40 * mm, 58 * mm, 8, fill=1, stroke=0)
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(28 * mm, card_y + 44 * mm, "Prepared for Muhammed Shumail")
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawString(28 * mm, card_y + 32 * mm, "mudshumail@gmail.com  ·  +971 50 810 2437")
    c.drawString(28 * mm, card_y + 22 * mm, "Current site: byshumail.my.canva.site")
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    co = gal.get("companiesCount", len(gal.get("companies", [])))
    cr = gal.get("creativesCount", len(gal.get("creatives", [])))
    c.drawString(
        28 * mm,
        card_y + 8 * mm,
        f"Industries logos: {co}  ·  Creatives: {cr}  ·  Admin panel  ·  Mobile ready",
    )
    draw_footer(c, 1, total)


def page_structure(c, total, gal):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, H - 22 * mm, "01  —  SITE STRUCTURE")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 36 * mm, "Same classification as Canva")
    draw_accent_bar(c, H - 42 * mm)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11)
    lines = [
        "Content is organised exactly like byshumail.my.canva.site —",
        "not random tags. Two clear portfolio groups:",
    ]
    y = H - 55 * mm
    for line in lines:
        c.drawString(20 * mm, y, line)
        y -= 6 * mm

    # Two big cards
    y -= 4 * mm
    c.setFillColor(CARD)
    c.roundRect(20 * mm, y - 48 * mm, W - 40 * mm, 52 * mm, 8, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(28 * mm, y - 10 * mm, "1. Industries worked with")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(28 * mm, y - 20 * mm, "Separate heading — partner / company logos only")
    c.drawString(28 * mm, y - 30 * mm, "(Revo, Nakshatra, alhind, Shobhika, Koukh al Shay, …)")
    c.setFillColor(LIGHT)
    c.drawString(
        28 * mm,
        y - 42 * mm,
        f"{gal.get('companiesCount', 0)} logos cleaned from the original site",
    )

    y -= 62 * mm
    c.setFillColor(CARD)
    c.roundRect(20 * mm, y - 78 * mm, W - 40 * mm, 82 * mm, 8, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(28 * mm, y - 10 * mm, "2. Creatives (selected work)")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(28 * mm, y - 20 * mm, "His creative categories as filters:")

    cats = [
        ("Final Reel", "Phone reels / showreels"),
        ("BTS", "Behind the scenes"),
        ("Hanan Shaah Concert", "Live event coverage"),
        ("Drone Shots", "Aerial cinematography"),
        ("Automobile", "Automotive films & stills"),
        ("Weddings & Events", "Celebrations & functions"),
    ]
    yy = y - 32 * mm
    for title, desc in cats:
        c.setFillColor(ORANGE)
        c.circle(32 * mm, yy + 1.5 * mm, 1.5 * mm, fill=1, stroke=0)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(38 * mm, yy, title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(95 * mm, yy, desc)
        yy -= 7 * mm

    y = yy - 10 * mm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Junk removed: UI arrows, sparkles, process numbers, social icons")
    c.drawString(20 * mm, y - 7 * mm, f"({gal.get('junkRemoved', 0)} non-work assets filtered out)")

    draw_footer(c, 2, total)


def page_industries(c, total, gal):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, H - 22 * mm, "02  —  INDUSTRIES WORKED WITH")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 36 * mm, "Company logos")
    draw_accent_bar(c, H - 42 * mm)

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(
        20 * mm,
        H - 54 * mm,
        "Separate section on the website — not mixed into creative filters.",
    )

    logos = gal.get("companies") or []
    if not logos:
        c.drawString(20 * mm, H - 70 * mm, "No logos loaded.")
        draw_footer(c, 3, total)
        return

    cols = 3
    gap = 8 * mm
    margin = 20 * mm
    cell_w = (W - 40 * mm - gap * (cols - 1)) / cols
    cell_h = 32 * mm
    top = H - 68 * mm

    for i, item in enumerate(logos[:9]):
        col = i % cols
        row = i // cols
        x = margin + col * (cell_w + gap)
        y = top - (row + 1) * cell_h - row * gap
        c.setFillColor(HexColor("#ffffff"))
        c.roundRect(x, y, cell_w, cell_h, 6, fill=1, stroke=0)
        img_path = ROOT / item["image"]
        if img_path.exists():
            try:
                c.drawImage(
                    ImageReader(str(img_path)),
                    x + 4 * mm,
                    y + 4 * mm,
                    width=cell_w - 8 * mm,
                    height=cell_h - 8 * mm,
                    preserveAspectRatio=True,
                    anchor="c",
                    mask="auto",
                )
            except Exception:
                pass

    draw_footer(c, 3, total)


def page_creatives(c, total, gal):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, H - 22 * mm, "03  —  CREATIVES")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 36 * mm, "Work by category")
    draw_accent_bar(c, H - 42 * mm)

    creatives = gal.get("creatives") or []
    from collections import Counter

    counts = Counter(i.get("categoryLabel", i.get("cat")) for i in creatives)

    y = H - 58 * mm
    for label, n in counts.most_common():
        c.setFillColor(CARD)
        c.roundRect(20 * mm, y - 6 * mm, W - 40 * mm, 14 * mm, 5, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(28 * mm, y - 1 * mm, label)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 11)
        c.drawRightString(W - 28 * mm, y - 1 * mm, f"{n} pieces")
        y -= 17 * mm

    y -= 6 * mm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Total creatives on site: {len(creatives)}")
    c.drawString(20 * mm, y - 7 * mm, "Filters on the website match these headings exactly.")

    # sample grid
    y -= 18 * mm
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "Sample frames")
    y -= 6 * mm

    samples = [i for i in creatives if (ROOT / i["image"]).exists()][:6]
    cols = 3
    gap = 6 * mm
    cell_w = (W - 40 * mm - gap * 2) / 3
    cell_h = 38 * mm
    for i, item in enumerate(samples):
        col = i % cols
        row = i // cols
        x = 20 * mm + col * (cell_w + gap)
        yy = y - (row + 1) * cell_h - row * gap
        c.setFillColor(CARD)
        c.roundRect(x, yy, cell_w, cell_h, 5, fill=1, stroke=0)
        try:
            c.drawImage(
                ImageReader(str(ROOT / item["image"])),
                x + 1,
                yy + 1,
                width=cell_w - 2,
                height=cell_h - 2,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
        except Exception:
            pass

    draw_footer(c, 4, total)


def page_admin(c, total):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, H - 22 * mm, "04  —  ADMIN + DELIVERABLES")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 36 * mm, "What you get")
    draw_accent_bar(c, H - 42 * mm)

    items = [
        "Dark premium website (mobile ready)",
        "Industries logos strip (separate heading)",
        "Creatives gallery with his real categories",
        "Junk UI assets removed from the gallery",
        "Admin panel to edit content & view messages",
        "This proposal PDF for client review",
    ]
    y = H - 58 * mm
    for t in items:
        c.setFillColor(CARD)
        c.roundRect(20 * mm, y - 5 * mm, W - 40 * mm, 12 * mm, 4, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(28 * mm, y - 1 * mm, "✓")
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 11)
        c.drawString(38 * mm, y - 1 * mm, t)
        y -= 15 * mm

    y -= 8 * mm
    c.setFillColor(ORANGE)
    c.roundRect(20 * mm, y - 36 * mm, W - 40 * mm, 40 * mm, 8, fill=1, stroke=0)
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(28 * mm, y - 12 * mm, "Admin login")
    c.setFont("Helvetica", 10)
    c.drawString(28 * mm, y - 22 * mm, "URL: /admin/    User: admin    Pass: shumail2026")
    c.drawString(28 * mm, y - 30 * mm, "Change password after handover.")

    draw_footer(c, 5, total)


def page_next(c, total):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, H - 22 * mm, "05  —  NEXT STEPS")
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, H - 36 * mm, "Launch checklist")
    draw_accent_bar(c, H - 42 * mm)

    steps = [
        "1. Review live preview + this PDF with the client",
        "2. Confirm company logos + creative category filters",
        "3. Connect custom domain (e.g. byshumail.com)",
        "4. Optional: WhatsApp button, booking form, blog",
        "5. Go live + analytics if required",
    ]
    y = H - 60 * mm
    c.setFont("Helvetica", 12)
    for s in steps:
        c.setFillColor(MUTED)
        c.drawString(20 * mm, y, s)
        y -= 10 * mm

    y -= 10 * mm
    c.setFillColor(CARD)
    c.roundRect(20 * mm, y - 40 * mm, W - 40 * mm, 44 * mm, 8, fill=1, stroke=0)
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(28 * mm, y - 14 * mm, "Contact on file")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(28 * mm, y - 24 * mm, "Muhammed Shumail  ·  mudshumail@gmail.com")
    c.drawString(28 * mm, y - 34 * mm, "+971 50 810 2437  ·  @shumail.ap")

    draw_footer(c, 6, total)


def main():
    gal = load_gallery()
    total = 6
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("Shumail Ap — Website Redesign Proposal")
    c.setAuthor("Website Redesign")
    c.setSubject("Portfolio redesign for byshumail.my.canva.site")

    page_cover(c, total, gal)
    c.showPage()
    page_structure(c, total, gal)
    c.showPage()
    page_industries(c, total, gal)
    c.showPage()
    page_creatives(c, total, gal)
    c.showPage()
    page_admin(c, total)
    c.showPage()
    page_next(c, total)
    c.save()
    print(f"Wrote {OUT}")
    print(
        f"Companies={gal.get('companiesCount')} Creatives={gal.get('creativesCount')} Junk={gal.get('junkRemoved')}"
    )


if __name__ == "__main__":
    main()
