"""
Rebuild gallery.json / site.json companies + creatives from live_layout_map.json
so placement matches https://byshumail.my.canva.site/

Rules:
- Industries worked with = brand LOGOS only (white canvas wordmarks)
- Final Reel / BTS = phone-format reels (tall frames), not UI chrome
- Concert / Drone / Automobile / Weddings = real photos & reel stills in those X bands
- Junk = arrows, sparkles, process numbers, social app icons, tiny UI
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "data" / "live_layout_map.json"
GALLERY = ROOT / "data" / "gallery.json"
SITE = ROOT / "data" / "site.json"

CREATIVE_LABELS = {
    "final-reel": "Final Reel",
    "bts": "BTS",
    "concert": "Hanan Shaah Concert",
    "drone": "Drone Shots",
    "automobile": "Automobile",
    "weddings": "Weddings & Events",
}


def analyze(path: Path) -> dict:
    im = Image.open(path)
    if im.mode in ("P", "RGBA"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im).convert("RGB")
    else:
        im = im.convert("RGB")
    w, h = im.size
    small = im.resize((48, 48))
    px = [small.getpixel((x, y)) for y in range(48) for x in range(48)]
    n = len(px)
    white = sum(1 for r, g, b in px if r > 230 and g > 230 and b > 230) / n
    black = sum(1 for r, g, b in px if r < 30 and g < 30 and b < 30) / n
    st = ImageStat.Stat(small)
    variance = sum(st.var) / max(len(st.var), 1)
    return {
        "w": w,
        "h": h,
        "ar": h / w if w else 1,
        "white": white,
        "black": black,
        "flat": white + black,
        "variance": variance,
        "bytes": path.stat().st_size,
        "ext": path.suffix.lower(),
    }


# Social app icons / process UI chrome — never show as creatives
ICON_DENY = (
    "MAA9p5KWXCY",  # white circles
    "MAD2U3W6DDA",  # number 1 circles
    "MADnBoBFUeY",  # Gmail
    "MAE1AuWxAmE",  # LinkedIn
    "MAE3Aa_nr44",  # email envelopes
    "MAEjDAuyytM",  # clapperboard / reel icons
    "MAElfTPish0",  # IG
    "MAFfKYTpv5s",  # WA
    "MAFShx0XtCw",  # arrows
    "MAFMK3m-Qqw",  # sparkles
    "MAFTBi1WAvo",
    "MAFTBmGra3o",
    "MAE8_lt1Pww",  # empty phone
    "MAFHg0JTam0",
)


def is_junk(a: dict, path: str | Path | None = None) -> bool:
    if path is not None:
        name = Path(path).name
        if any(d in name for d in ICON_DENY):
            return True
    if a["bytes"] < 5000:
        return True
    if min(a["w"], a["h"]) < 70:
        return True
    # pure black/white decorative
    if a["flat"] > 0.88 and a["variance"] < 1800:
        return True
    if a["black"] > 0.8 and a["variance"] < 2200:
        return True
    # ultra-wide UI bars
    if a["h"] < 90 and a["w"] > a["h"] * 5 and a["variance"] < 3500:
        return True
    # large flat icon sheets (gmail/linkedin style)
    if a["ext"] == ".png" and a["black"] > 0.55 and a["variance"] < 2500 and a["bytes"] < 200000:
        return True
    return False


def is_logo(a: dict) -> bool:
    if is_junk(a):
        return False
    # blank phone mockups / device chrome (not a brand)
    if a["ar"] >= 1.2 and a["ext"] == ".png" and a["variance"] < 6000 and a["white"] > 0.25 and a["white"] < 0.55:
        # empty phone UI often mid white + flat
        if a["w"] > 1000 and a["h"] > 1400:
            return False
    # real photos are never logos
    if a["ext"] in (".jpg", ".jpeg") and a["variance"] > 1800 and a["bytes"] > 30000:
        return False
    # social app squares (IG/WA style)
    if 0.85 <= a["ar"] <= 1.15 and a["w"] <= 900 and a["white"] < 0.75 and a["black"] < 0.1:
        if a["variance"] > 3000:
            return False
    # brand marks: light canvas OR dark canvas wordmark logos
    if a["ext"] == ".png" and a["white"] > 0.4:
        return True
    if a["ext"] == ".png" and a["black"] > 0.4 and a["ar"] < 0.6 and a["bytes"] > 20000:
        # e.g. Al Bahja on black
        return True
    if a["ext"] == ".png" and a["variance"] < 4000 and a["white"] > 0.3:
        return True
    return False


def is_photo(a: dict) -> bool:
    if is_junk(a):
        return False
    if is_logo(a):
        return False
    if a["ext"] in (".jpg", ".jpeg", ".webp") and a["bytes"] >= 15000:
        return True
    if a["variance"] > 2000 and a["bytes"] > 25000:
        return True
    return False


def is_phone_reel(entry: dict, a: dict) -> bool:
    # tall phone-like frames used for Final Reel / BTS
    ar = entry.get("ar") or a["ar"]
    w = entry.get("w") or a["w"]
    if ar >= 1.45 and 150 <= w <= 600:
        return True
    if entry.get("kind") == "video" and ar >= 1.4:
        return True
    return False


def main():
    layout = json.loads(MAP.read_text(encoding="utf-8"))
    buckets = layout["buckets"]

    companies = []
    creatives = {k: [] for k in CREATIVE_LABELS}
    junk = []
    seen = set()

    # Process each live bucket
    for bucket_key, entries in buckets.items():
        if bucket_key == "pre-portfolio":
            # only keep hero-related large photo if needed — skip UI chrome
            continue

        for e in entries:
            f = e["file"]
            if f in seen:
                continue
            full = ROOT / f
            if not full.exists():
                junk.append(f)
                continue
            try:
                a = analyze(full)
            except Exception:
                junk.append(f)
                continue

            if is_junk(a, f):
                junk.append(f)
                continue

            # --- industries bucket: logos only; re-home photos/reels ---
            if bucket_key == "industries":
                if is_logo(a):
                    seen.add(f)
                    companies.append(
                        {
                            "path": f,
                            "x": e["x"],
                            "y": e["y"],
                            "source": e["id"],
                        }
                    )
                    continue
                if is_phone_reel(e, a):
                    # phone reels near this strip belong to Final Reel / BTS
                    cat = "bts" if e["y"] >= 780 else "final-reel"
                    seen.add(f)
                    creatives[cat].append(
                        {
                            "path": f,
                            "type": "video" if e["kind"] == "video" else "media",
                            "x": e["x"],
                            "y": e["y"],
                            "source": e["id"],
                        }
                    )
                    continue
                if is_photo(a):
                    # Featured showcase photos sitting in industries X — assign by content shape
                    # tall → final-reel, wide multi/auto-ish left, wedding-ish right of band
                    if a["ar"] >= 1.25:
                        cat = "bts" if e["y"] > 400 else "final-reel"
                    elif e["x"] < 2400:
                        cat = "weddings"  # confetti/celebration common left
                    elif e["x"] < 2800:
                        cat = "automobile"
                    else:
                        cat = "final-reel"
                    # refine known files by name patterns later
                    seen.add(f)
                    creatives[cat].append(
                        {
                            "path": f,
                            "type": "media",
                            "x": e["x"],
                            "y": e["y"],
                            "source": e["id"],
                        }
                    )
                    continue
                junk.append(f)
                continue

            # --- final-reel / bts: only phone reels + real photos, no UI chrome ---
            if bucket_key in ("final-reel", "bts"):
                if is_logo(a) or is_junk(a, f):
                    junk.append(f)
                    continue
                if is_phone_reel(e, a) or is_photo(a) or e["kind"] == "video":
                    cat = bucket_key
                    # if phone in final-reel band but low y for bts label
                    if is_phone_reel(e, a) and e["y"] >= 780:
                        cat = "bts"
                    elif is_phone_reel(e, a):
                        cat = "final-reel"
                    seen.add(f)
                    creatives[cat].append(
                        {
                            "path": f,
                            "type": "video" if e["kind"] == "video" else "media",
                            "x": e["x"],
                            "y": e["y"],
                            "source": e["id"],
                        }
                    )
                else:
                    junk.append(f)
                continue

            # --- creative sections ---
            if bucket_key in CREATIVE_LABELS:
                if is_logo(a):
                    # logos that appear near wedding footer etc. still companies if quality
                    if a["white"] > 0.45 and a["black"] < 0.12:
                        seen.add(f)
                        companies.append(
                            {"path": f, "x": e["x"], "y": e["y"], "source": e["id"]}
                        )
                    else:
                        junk.append(f)
                    continue
                if not (is_photo(a) or e["kind"] == "video" or is_phone_reel(e, a)):
                    junk.append(f)
                    continue
                # drop social icons that slipped as "photo"
                if a["ext"] == ".png" and a["w"] < 800 and 0.9 <= a["ar"] <= 1.1 and a["white"] < 0.7:
                    junk.append(f)
                    continue
                seen.add(f)
                creatives[bucket_key].append(
                    {
                        "path": f,
                        "type": "video" if e["kind"] == "video" else "media",
                        "x": e["x"],
                        "y": e["y"],
                        "source": e["id"],
                    }
                )
                continue

            junk.append(f)

    # Manual re-homes for known mis-bucketed showcases (content verified earlier)
    rehome = {
        # wedding confetti groom — industries X but wedding content
        "media_046_MAHMpkOVBdk.jpg": "weddings",
        # BTS laptop edit
        "media_023_MAHMpgLn9sQ.jpg": "bts",
        # car collage
        "media_038_MAHMpivmVfw.jpg": "automobile",
    }
    for cat_list in creatives.values():
        for item in cat_list:
            name = Path(item["path"]).name
            if name in rehome:
                item["_rehome"] = rehome[name]

    # apply rehome
    flat = []
    for cat, items in creatives.items():
        for item in items:
            target = item.pop("_rehome", cat)
            flat.append((target, item))
    creatives = {k: [] for k in CREATIVE_LABELS}
    for target, item in flat:
        # dedupe path
        if any(x["path"] == item["path"] for x in creatives[target]):
            continue
        creatives[target].append(item)

    # Also pull logos that appear inside industries map entries (even if earlier filter missed)
    for e in buckets.get("industries", []):
        f = e["file"]
        full = ROOT / f
        if not full.exists():
            continue
        try:
            a = analyze(full)
        except Exception:
            continue
        if is_logo(a) and f not in {c["path"] for c in companies}:
            companies.append({"path": f, "x": e["x"], "y": e["y"], "source": e["id"]})

    # Build company items — logos only (no phone mockups / app icons)
    companies = sorted(companies, key=lambda c: (c["x"], c["y"]))
    company_items = []
    seen_co = set()
    for c in companies:
        if c["path"] in seen_co:
            continue
        full = ROOT / c["path"]
        a = analyze(full)
        if not is_logo(a):
            continue
        name = Path(c["path"]).name
        # hard deny: phone mockups, UI chrome, process bars
        deny = (
            "MAE8_lt1Pww",  # empty phone frame
            "MAFHg0JTam0",  # UI toggle bar
            "MAFTBi1WAvo",  # process numbers
            "MAFTBmGra3o",
            "MAElfTPish0",  # IG
            "MAFfKYTpv5s",  # WA
            "MAFShx0XtCw",  # arrows
            "MAFMK3m-Qqw",  # sparkles
        )
        if any(d in name for d in deny):
            continue
        # blank phone frame heuristic
        if a["ar"] >= 1.15 and a["h"] > 1200 and a["white"] < 0.6:
            continue
        # app icons
        if 0.85 <= a["ar"] <= 1.15 and a["w"] <= 900 and a["white"] < 0.78 and a["black"] < 0.15 and a["variance"] > 3500:
            continue
        seen_co.add(c["path"])
        title_map = {
            "media_085": "Revo",
            "MAHMwsKDn2s": "Revo",
            "media_087": "Nakshatra Gold & Diamonds",
            "MAHMxAZwkWY": "Nakshatra Gold & Diamonds",
            "media_086": "alhind Tours & Travels",
            "MAHMwu8Sfzo": "alhind Tours & Travels",
            "media_088": "Shobhika Weddings",
            "MAHMxJKmBsk": "Shobhika Weddings",
            "media_084": "Koukh al Shay",
            "MAHMwgWnf0A": "Koukh al Shay",
            "media_089": "Al Bahja Al Daema",
            "MAHMxUJPuHA": "Al Bahja Al Daema",
        }
        title = "Partner"
        for k, v in title_map.items():
            if k in name:
                title = v
                break
        company_items.append(
            {
                "id": f"co{len(company_items)+1:02d}",
                "title": title,
                "cat": "companies",
                "categoryLabel": "Industries worked with",
                "image": c["path"],
                "visible": True,
                "type": "logo",
                "section": "companies",
            }
        )

    # Force-include known partner logos if present on disk
    force_logos = [
        ("assets/canva/media/media_085_MAHMwsKDn2s.png", "Revo"),
        ("assets/canva/media/media_087_MAHMxAZwkWY.png", "Nakshatra Gold & Diamonds"),
        ("assets/canva/media/media_086_MAHMwu8Sfzo.png", "alhind Tours & Travels"),
        ("assets/canva/media/media_088_MAHMxJKmBsk.png", "Shobhika Weddings"),
        ("assets/canva/media/media_084_MAHMwgWnf0A.png", "Koukh al Shay"),
        ("assets/canva/media/media_089_MAHMxUJPuHA.png", "Al Bahja Al Daema"),
    ]
    have = {c["image"] for c in company_items}
    for path, title in force_logos:
        if path in have or not (ROOT / path).exists():
            continue
        company_items.append(
            {
                "id": f"co{len(company_items)+1:02d}",
                "title": title,
                "cat": "companies",
                "categoryLabel": "Industries worked with",
                "image": path,
                "visible": True,
                "type": "logo",
                "section": "companies",
            }
        )
    # stable order matching typical industries strip
    order_titles = [
        "Revo",
        "Nakshatra Gold & Diamonds",
        "alhind Tours & Travels",
        "Shobhika Weddings",
        "Koukh al Shay",
        "Al Bahja Al Daema",
    ]
    company_items.sort(
        key=lambda c: order_titles.index(c["title"]) if c["title"] in order_titles else 99
    )
    for i, c in enumerate(company_items, 1):
        c["id"] = f"co{i:02d}"

    # Creative items ordered as on site
    order = ["final-reel", "bts", "concert", "drone", "automobile", "weddings"]
    creative_items = []
    seen_cr = set()
    for key in order:
        items = sorted(creatives[key], key=lambda z: (z["y"], z["x"]))
        for it in items:
            if it["path"] in seen_cr or it["path"] in seen_co:
                continue
            full = ROOT / it["path"]
            if not full.exists() or full.stat().st_size < 12000:
                continue
            a = analyze(full)
            if is_junk(a) or is_logo(a):
                continue
            seen_cr.add(it["path"])
            creative_items.append(
                {
                    "id": f"cr{len(creative_items)+1:03d}",
                    "title": CREATIVE_LABELS[key],
                    "cat": key,
                    "categoryLabel": CREATIVE_LABELS[key],
                    "image": it["path"],
                    "visible": True,
                    "type": it["type"],
                    "section": "creatives",
                    "pageX": it["x"],
                    "pageY": it["y"],
                }
            )

    categories = [
        {"key": "companies", "label": "Industries worked with", "group": "companies"}
    ] + [
        {"key": k, "label": CREATIVE_LABELS[k], "group": "creatives"}
        for k in order
        if any(i["cat"] == k for i in creative_items)
    ]

    doc = {
        "count": len(company_items) + len(creative_items),
        "companiesCount": len(company_items),
        "creativesCount": len(creative_items),
        "junkRemoved": len(junk),
        "portrait": "assets/portrait.jpg",
        "categories": categories,
        "companies": company_items,
        "creatives": creative_items,
        "items": company_items + creative_items,
        "source": "live_layout_map + content filters",
    }
    GALLERY.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    if SITE.exists():
        site = json.loads(SITE.read_text(encoding="utf-8"))
        site["portfolio"] = doc["items"]
        site["portfolioCategories"] = categories
        site["companies"] = company_items
        site["creatives"] = creative_items
        site["portrait"] = "assets/portrait.jpg"
        SITE.write_text(json.dumps(site, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== Industries worked with (logos only) ===")
    for c in company_items:
        print(" ", c["image"])
    print(f"\n=== Creatives ({len(creative_items)}) ===")
    for lab, n in Counter(i["categoryLabel"] for i in creative_items).most_common():
        print(f"  {lab}: {n}")
    print(f"\nJunk filtered: {len(junk)}")


if __name__ == "__main__":
    main()
