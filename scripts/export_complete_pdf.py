#!/usr/bin/env python3
"""
Full portfolio website PDF — every section of the live page:
Hero, Services, About, Industries, Creatives (all categories), Process, Contact.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Shumail-Complete-Website.pdf"
SITE = ROOT / "data" / "site.json"
GALLERY = ROOT / "data" / "gallery.json"

BG = HexColor("#0d0d0d")
CARD = HexColor("#1a1a1a")
ORANGE = HexColor("#f97316")
ORANGE_SOFT = HexColor("#2a1810")
MUTED = HexColor("#a0a0a0")
DIM = HexColor("#6b6b6b")
LIGHT = HexColor("#f5f5f5")
BORDER = HexColor("#2a2a2a")
W, H = A4
M = 16 * mm


def load():
    site = json.loads(SITE.read_text(encoding="utf-8")) if SITE.exists() else {}
    gal = json.loads(GALLERY.read_text(encoding="utf-8")) if GALLERY.exists() else {}
    # Prefer gallery creatives/companies (freshest)
    if gal.get("creatives"):
        site["creatives"] = gal["creatives"]
    if gal.get("companies"):
        site["companies"] = gal["companies"]
    if gal.get("categories"):
        site["portfolioCategories"] = gal["categories"]
    return site


def draw_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # soft orange glow top-left
    c.setFillColor(HexColor("#1a1008"))
    c.circle(W * 0.12, H * 0.9, 100, fill=1, stroke=0)


def footer(c, page, total, name="Muhammed Shumail"):
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.4)
    c.line(M, 12 * mm, W - M, 12 * mm)
    c.setFillColor(DIM)
    c.setFont("Helvetica", 7.5)
    c.drawString(M, 7 * mm, f"{name}  ·  byshumail portfolio")
    c.setFillColor(ORANGE)
    c.drawRightString(W - M, 7 * mm, f"{page}  /  {total}")


def heading(c, eyebrow, title, y, accent=""):
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M, y, eyebrow.upper())
    y -= 8 * mm
    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(M, y, title)
    if accent:
        tw = c.stringWidth(title + " ", "Helvetica-Bold", 18)
        c.setFillColor(ORANGE)
        c.drawString(M + tw, y, accent)
    y -= 3 * mm
    c.setFillColor(ORANGE)
    c.roundRect(M, y, 22 * mm, 2.2, 1, fill=1, stroke=0)
    return y - 8 * mm


def fit_image(path: Path, max_w: float, max_h: float, max_px: int = 720):
    if not path.exists():
        return None, 0, 0
    try:
        im = PILImage.open(path)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        iw, ih = im.size
        # Cap pixel size for a shareable PDF
        if max(iw, ih) > max_px:
            r = max_px / max(iw, ih)
            im = im.resize((max(1, int(iw * r)), max(1, int(ih * r))), PILImage.Resampling.LANCZOS)
            iw, ih = im.size
        scale = min(max_w / iw, max_h / ih, 1.0)
        return ImageReader(im), iw * scale, ih * scale
    except Exception:
        return None, 0, 0


def page_cover(c, site, page, total):
    draw_bg(c)
    c.setFillColor(ORANGE)
    c.rect(0, 0, 5 * mm, H, fill=1, stroke=0)

    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, H - 28 * mm, "COMPLETE PORTFOLIO WEBSITE")

    name = site.get("name") or "Muhammed Shumail"
    role = site.get("role") or "Content Creator"
    tag = site.get("tagline") or "Photographer · Videographer · Dubai"

    c.setFillColor(LIGHT)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(M, H - 50 * mm, name)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(M, H - 62 * mm, role)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11)
    c.drawString(M, H - 72 * mm, tag)

    # Portrait circle-ish crop
    portrait = ROOT / (site.get("portrait") or "assets/portrait.jpg")
    img, iw, ih = fit_image(portrait, 85 * mm, 85 * mm)
    if img:
        x = W - M - 90 * mm
        y = H - 175 * mm
        c.setFillColor(ORANGE)
        c.circle(x + 42.5 * mm, y + 42.5 * mm, 44 * mm, fill=1, stroke=0)
        c.saveState()
        p = c.beginPath()
        p.circle(x + 42.5 * mm, y + 42.5 * mm, 40 * mm)
        c.clipPath(p, stroke=0)
        c.drawImage(img, x + 42.5 * mm - iw / 2, y + 42.5 * mm - ih / 2, iw, ih, mask="auto")
        c.restoreState()

    # Stats
    stats = site.get("stats") or []
    y = H - 110 * mm
    c.setFillColor(CARD)
    c.roundRect(M, y - 18 * mm, W - 2 * M - 100 * mm, 28 * mm, 8, fill=1, stroke=0)
    if stats:
        slot = (W - 2 * M - 100 * mm) / max(len(stats), 1)
        for i, s in enumerate(stats):
            cx = M + slot * i + slot / 2
            c.setFillColor(ORANGE)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(cx, y - 2 * mm, str(s.get("value", "")))
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 7)
            c.drawCentredString(cx, y - 9 * mm, str(s.get("label", ""))[:22])

    # Contact strip
    contact = site.get("contact") or {}
    y = 40 * mm
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    line = "  ·  ".join(
        filter(
            None,
            [
                contact.get("email"),
                contact.get("phone"),
                contact.get("location"),
                contact.get("instagramHandle"),
            ],
        )
    )
    c.drawString(M, y, line)
    footer(c, page, total, name)


def page_services(c, site, page, total):
    draw_bg(c)
    y = H - 28 * mm
    y = heading(c, "What I offer", "Services that ", y, "drive results")
    services = site.get("services") or []
    col_w = (W - 2 * M - 6 * mm) / 2
    row_h = 38 * mm
    for i, s in enumerate(services):
        col = i % 2
        row = i // 2
        x = M + col * (col_w + 6 * mm)
        yy = y - row * (row_h + 5 * mm) - row_h
        if yy < 20 * mm:
            break
        c.setFillColor(CARD)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.6)
        c.roundRect(x, yy, col_w, row_h, 6, fill=1, stroke=1)
        c.setFillColor(ORANGE)
        c.circle(x + 6 * mm, yy + row_h - 8 * mm, 2.2 * mm, fill=1, stroke=0)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 12 * mm, yy + row_h - 10 * mm, str(s.get("title", ""))[:36])
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        text = str(s.get("desc", ""))
        # wrap
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 8) < col_w - 14 * mm:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for li, line in enumerate(lines[:4]):
            c.drawString(x + 7 * mm, yy + row_h - 18 * mm - li * 3.6 * mm, line)
    footer(c, page, total, site.get("name", ""))


def page_about(c, site, page, total):
    draw_bg(c)
    y = H - 28 * mm
    about = site.get("about") or {}
    y = heading(
        c,
        "About me",
        about.get("title") or "Capturing Stories.",
        y,
        about.get("titleAccent") or "",
    )

    # Photo
    img_path = ROOT / (about.get("image") or "assets/work-1.jpg")
    img, iw, ih = fit_image(img_path, 70 * mm, 90 * mm)
    if img:
        c.setFillColor(CARD)
        c.roundRect(M, y - ih - 4 * mm, iw + 4 * mm, ih + 4 * mm, 6, fill=1, stroke=0)
        c.drawImage(img, M + 2 * mm, y - ih - 2 * mm, iw, ih, mask="auto")
        text_x = M + iw + 12 * mm
        text_w = W - text_x - M
    else:
        text_x = M
        text_w = W - 2 * M

    c.setFillColor(LIGHT)
    c.setFont("Helvetica", 9)
    lead = about.get("lead") or ""
    body = about.get("body") or ""

    def draw_wrapped(text, x, y0, max_w, size=9, color=MUTED, leading=3.8 * mm):
        c.setFillColor(color)
        c.setFont("Helvetica", size)
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if c.stringWidth(test, "Helvetica", size) < max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        yy = y0
        for line in lines:
            c.drawString(x, yy, line)
            yy -= leading
        return yy

    yy = y - 2 * mm
    yy = draw_wrapped(lead, text_x, yy, text_w, 9, LIGHT, 4 * mm)
    yy -= 3 * mm
    yy = draw_wrapped(body, text_x, yy, text_w, 8.5, MUTED, 3.6 * mm)
    yy -= 6 * mm

    for ach in about.get("achievements") or []:
        if yy < 30 * mm:
            break
        c.setFillColor(ORANGE)
        c.circle(text_x + 2 * mm, yy + 1.5 * mm, 1.8 * mm, fill=1, stroke=0)
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(text_x + 7 * mm, yy, str(ach.get("title", "")))
        yy -= 4 * mm
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(text_x + 7 * mm, yy, str(ach.get("desc", ""))[:70])
        yy -= 7 * mm

    clients = about.get("clients") or []
    if clients and yy > 25 * mm:
        c.setFillColor(DIM)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(text_x, yy, "TRUSTED BY")
        yy -= 6 * mm
        for cl in clients:
            c.setStrokeColor(BORDER)
            c.setFillColor(CARD)
            tw = c.stringWidth(cl, "Helvetica", 8) + 8 * mm
            c.roundRect(text_x, yy - 1 * mm, tw, 6 * mm, 3, fill=1, stroke=1)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(text_x + 4 * mm, yy + 0.8 * mm, cl)
            text_x += tw + 3 * mm

    footer(c, page, total, site.get("name", ""))


def page_industries(c, site, page, total):
    draw_bg(c)
    y = H - 28 * mm
    y = heading(c, "Partners", "Industries worked ", y, "with")
    companies = site.get("companies") or []
    if not companies:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(M, y, "No company logos.")
        footer(c, page, total, site.get("name", ""))
        return

    cols = 3
    gap = 5 * mm
    card_w = (W - 2 * M - gap * (cols - 1)) / cols
    card_h = 38 * mm
    for i, co in enumerate(companies):
        col = i % cols
        row = i // cols
        x = M + col * (card_w + gap)
        yy = y - row * (card_h + gap) - card_h
        if yy < 18 * mm:
            break
        c.setFillColor(HexColor("#ffffff"))
        c.roundRect(x, yy, card_w, card_h, 6, fill=1, stroke=0)
        img_path = ROOT / (co.get("image") or "")
        img, iw, ih = fit_image(img_path, card_w - 10 * mm, card_h - 14 * mm)
        if img:
            c.drawImage(
                img,
                x + (card_w - iw) / 2,
                yy + 8 * mm + (card_h - 14 * mm - ih) / 2,
                iw,
                ih,
                mask="auto",
            )
        c.setFillColor(DIM)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + card_w / 2, yy + 3 * mm, str(co.get("title", ""))[:28])
    footer(c, page, total, site.get("name", ""))


def pages_creatives(c, site, total_so_far, total_pages_ref):
    """Yield (drawn_pages_count). Draws all creative category pages."""
    creatives = [x for x in (site.get("creatives") or []) if x.get("visible") is not False]
    order = [
        ("final-reel", "Final Reel"),
        ("bts", "BTS"),
        ("concert", "Hanan Shaah Concert"),
        ("drone", "Drone Shots"),
        ("automobile", "Automobile"),
        ("weddings", "Weddings & Events"),
    ]
    by_cat = {}
    for item in creatives:
        by_cat.setdefault(item.get("cat") or "other", []).append(item)

    pages_drawn = 0
    page_num = total_so_far  # last completed page number

    for key, label in order:
        items = by_cat.get(key) or []
        if not items:
            continue
        # paginate 9 thumbs per page (3x3)
        per = 9
        for start in range(0, len(items), per):
            chunk = items[start : start + per]
            if pages_drawn > 0:
                c.showPage()
            page_num += 1
            pages_drawn += 1
            draw_bg(c)
            y = H - 28 * mm
            sub = f"{start + 1}–{start + len(chunk)} of {len(items)}"
            y = heading(c, "Creatives", label + "  ", y, sub)

            cols = 3
            gap = 4 * mm
            card_w = (W - 2 * M - gap * (cols - 1)) / cols
            card_h = 58 * mm
            for i, item in enumerate(chunk):
                col = i % cols
                row = i // cols
                x = M + col * (card_w + gap)
                yy = y - row * (card_h + gap) - card_h
                if yy < 16 * mm:
                    break
                c.setFillColor(CARD)
                c.setStrokeColor(BORDER)
                c.setLineWidth(0.5)
                c.roundRect(x, yy, card_w, card_h, 5, fill=1, stroke=1)

                img_path = ROOT / (item.get("image") or "")
                img, iw, ih = fit_image(img_path, card_w - 4 * mm, card_h - 12 * mm, max_px=480)
                if img:
                    c.saveState()
                    p = c.beginPath()
                    p.roundRect(x + 2 * mm, yy + 10 * mm, card_w - 4 * mm, card_h - 12 * mm, 3)
                    c.clipPath(p, stroke=0)
                    # cover fit
                    scale = max((card_w - 4 * mm) / max(iw, 1), (card_h - 12 * mm) / max(ih, 1))
                    dw, dh = iw * scale, ih * scale
                    c.drawImage(
                        img,
                        x + 2 * mm + (card_w - 4 * mm - dw) / 2,
                        yy + 10 * mm + (card_h - 12 * mm - dh) / 2,
                        dw,
                        dh,
                        mask="auto",
                    )
                    c.restoreState()

                # badge
                if item.get("video") or item.get("type") == "video":
                    c.setFillColor(ORANGE)
                    c.roundRect(x + 3 * mm, yy + card_h - 9 * mm, 14 * mm, 5 * mm, 2, fill=1, stroke=0)
                    c.setFillColor(HexColor("#111111"))
                    c.setFont("Helvetica-Bold", 6)
                    c.drawCentredString(x + 10 * mm, yy + card_h - 7.5 * mm, "REEL")

                c.setFillColor(MUTED)
                c.setFont("Helvetica", 6.5)
                c.drawString(x + 3 * mm, yy + 3.5 * mm, label[:28])

            # temporary page number; rewritten after total known — use placeholder
            footer(c, page_num, total_pages_ref[0], site.get("name", ""))

    return pages_drawn, page_num


def page_process(c, site, page, total):
    draw_bg(c)
    y = H - 28 * mm
    y = heading(c, "My creative process", "How it ", y, "works")
    steps = site.get("process") or []
    for i, s in enumerate(steps):
        yy = y - i * 28 * mm
        if yy < 24 * mm:
            break
        c.setFillColor(CARD)
        c.setStrokeColor(BORDER)
        c.roundRect(M, yy - 18 * mm, W - 2 * M, 24 * mm, 6, fill=1, stroke=1)
        c.setFillColor(ORANGE)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(M + 5 * mm, yy - 5 * mm, str(s.get("num", f"0{i+1}")))
        c.setFillColor(LIGHT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M + 22 * mm, yy - 2 * mm, str(s.get("title", "")))
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawString(M + 22 * mm, yy - 9 * mm, str(s.get("desc", ""))[:95])
    footer(c, page, total, site.get("name", ""))


def page_contact(c, site, page, total):
    draw_bg(c)
    y = H - 28 * mm
    y = heading(c, "Contact", "Let's work ", y, "together")
    contact = site.get("contact") or {}
    cta = site.get("cta") or {}

    c.setFillColor(CARD)
    c.roundRect(M, y - 70 * mm, W - 2 * M, 68 * mm, 8, fill=1, stroke=0)

    rows = [
        ("Email", contact.get("email", "")),
        ("Phone", contact.get("phone", "")),
        ("Location", contact.get("location", "")),
        ("Instagram", contact.get("instagramHandle", "")),
        ("LinkedIn", contact.get("linkedinHandle", "")),
    ]
    yy = y - 12 * mm
    for label, val in rows:
        if not val:
            continue
        c.setFillColor(DIM)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(M + 8 * mm, yy, label.upper())
        c.setFillColor(LIGHT)
        c.setFont("Helvetica", 11)
        c.drawString(M + 40 * mm, yy, str(val))
        yy -= 10 * mm

    yy = y - 90 * mm
    c.setFillColor(ORANGE)
    c.roundRect(M, yy - 28 * mm, W - 2 * M, 32 * mm, 8, fill=1, stroke=0)
    c.setFillColor(HexColor("#111111"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(M + 8 * mm, yy - 10 * mm, str(cta.get("title") or "Let's connect and work together"))
    c.setFont("Helvetica", 8.5)
    c.drawString(M + 8 * mm, yy - 18 * mm, str(cta.get("text") or "")[:90])

    footer(c, page, total, site.get("name", ""))


def main():
    site = load()
    # First pass: estimate pages
    creatives = [x for x in (site.get("creatives") or []) if x.get("visible") is not False]
    by_cat = {}
    for item in creatives:
        by_cat.setdefault(item.get("cat") or "other", []).append(item)
    order = ["final-reel", "bts", "concert", "drone", "automobile", "weddings"]
    creative_pages = 0
    for key in order:
        n = len(by_cat.get(key) or [])
        if n:
            creative_pages += (n + 8) // 9

    # cover + services + about + industries + creatives + process + contact
    total = 1 + 1 + 1 + 1 + creative_pages + 1 + 1
    total_ref = [total]

    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("Shumail Ap — Complete Portfolio Website")
    c.setAuthor(site.get("name") or "Muhammed Shumail")

    page = 1
    page_cover(c, site, page, total)
    c.showPage()
    page += 1

    page_services(c, site, page, total)
    c.showPage()
    page += 1

    page_about(c, site, page, total)
    c.showPage()
    page += 1

    page_industries(c, site, page, total)
    c.showPage()

    # Creatives gallery (one or more pages per category)
    drawn, page = pages_creatives(c, site, page, total_ref)
    if drawn == 0:
        # still advance page counter if no creatives
        page += 1
    c.showPage()
    page += 1

    page_process(c, site, page, total)
    c.showPage()
    page += 1

    page_contact(c, site, page, total)

    c.save()
    size_kb = OUT.stat().st_size / 1024
    print(f"OK: {OUT}")
    print(f"Pages: ~{total} (last page #{page})  Size: {size_kb:.0f} KB")
    print(f"Creatives: {len(creatives)} across {creative_pages} gallery pages")


if __name__ == "__main__":
    main()
