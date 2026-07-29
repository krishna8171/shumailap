"""
Match byshumail.my.canva.site structure:

  HEADING: Industries worked with  → company logos only
  HEADING: Creatives / portfolio     → Final Reel, BTS, Concert,
                                       Automobile, Weddings, Drone
  Remove junk UI graphics
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageStat

HTML = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html")
ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = ROOT / "assets" / "canva" / "media"
VIDEO_DIR = ROOT / "assets" / "canva" / "video"
MANIFEST = ROOT / "assets" / "canva" / "manifest.json"
GALLERY_OUT = ROOT / "data" / "gallery.json"
SITE_JSON = ROOT / "data" / "site.json"
META_OUT = ROOT / "data" / "canva_categories.json"

CREATIVE_ORDER = [
    ("final-reel", "Final Reel"),
    ("bts", "BTS"),
    ("concert", "Hanan Shaah Concert"),
    ("drone", "Drone Shots"),
    ("automobile", "Automobile"),
    ("weddings", "Weddings & Events"),
]
CREATIVE_LABELS = dict(CREATIVE_ORDER)


def analyze(path: Path) -> dict:
    im = Image.open(path)
    if im.mode in ("P", "RGBA"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im).convert("RGB")
    else:
        im = im.convert("RGB")
    w, h = im.size
    small = im.resize((64, 64))
    # use load() for future-proofing
    px = [small.getpixel((x, y)) for y in range(64) for x in range(64)]
    n = len(px)
    white = sum(1 for r, g, b in px if r > 230 and g > 230 and b > 230) / n
    black = sum(1 for r, g, b in px if r < 30 and g < 30 and b < 30) / n
    st = ImageStat.Stat(small)
    # mean variance across channels
    variance = sum(st.var) / len(st.var)
    # edge flatness: how much is near pure black or white
    flat = white + black
    return {
        "w": w,
        "h": h,
        "ar": h / w if w else 1,
        "white": white,
        "black": black,
        "flat": flat,
        "variance": variance,
        "bytes": path.stat().st_size,
        "ext": path.suffix.lower(),
    }


def is_junk(a: dict, path: Path) -> bool:
    # tiny files
    if a["bytes"] < 3500:
        return True
    if min(a["w"], a["h"]) < 60:
        return True
    # pure black/white decorative icons (arrows, stars, toggles)
    if a["flat"] > 0.9 and a["variance"] < 1500:
        return True
    if a["black"] > 0.82 and a["variance"] < 2000:
        return True
    # ultra-wide 1px-style UI bars
    if a["h"] < 80 and a["w"] > a["h"] * 6 and a["variance"] < 3000:
        return True
    # known decorative name patterns — none
    return False


def is_logo(a: dict, path: Path) -> bool:
    if is_junk(a, path):
        return False
    # photographic frames are not logos
    if a["ext"] in (".jpg", ".jpeg") and a["variance"] > 2000 and a["bytes"] > 40000:
        return False
    # brand logos: png, often white bg or flat brand colors, not huge photos
    if a["ext"] == ".png":
        if a["bytes"] > 400_000 and a["variance"] > 4000:
            return False  # large complex png photo
        # white canvas logos (Revo, Shobhika style)
        if a["white"] > 0.35 and a["bytes"] < 250_000:
            return True
        # flat graphic logo
        if a["variance"] < 4500 and a["w"] < 1400:
            return True
        if a["ar"] < 0.5 and a["h"] < 350:
            return True
    return False


def is_photo_or_video(a: dict, kind: str) -> bool:
    if kind == "video":
        return a["bytes"] >= 5000
    if is_junk(a, Path("x")):
        return False
    if a["ext"] in (".jpg", ".jpeg", ".webp"):
        return a["bytes"] >= 15000
    # png photos rare but possible
    if a["ext"] == ".png" and a["variance"] > 4000 and a["bytes"] > 80000:
        return True
    return False


def find_label_pos(html: str, needle: str):
    i = html.find(needle)
    if i < 0:
        return None
    back = html[max(0, i - 500) : i]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    if not coords:
        return None
    x, y, w, h = map(float, coords[-1].groups())
    return {"x": x, "y": y, "w": w, "h": h}


def abs_parent_near(html: str, pos: int):
    back = html[max(0, pos - 3000) : pos]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    best, score = None, -1.0
    for c in coords:
        x, y, w, h = map(float, c.groups())
        if x < 150 or w < 40:
            continue
        sc = w * h + c.start() * 0.01
        if sc > score:
            score = sc
            best = (x, y, w, h)
    return best


def media_placements(html: str):
    out = []
    pat = (
        r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)'
        r'(?:(?!"A":[0-9.eE+-]+,"B":)[\s\S]){0,900}?"A\?":"d","A":"(MA[A-Za-z0-9_-]+)"'
    )
    for m in re.finditer(pat, html):
        x, y, w, h = map(float, m.group(1, 2, 3, 4))
        out.append({"x": x, "y": y, "w": w, "h": h, "id": m.group(5), "kind": "media"})
    return out


def video_placements(html: str):
    out, seen = [], set()
    for m in re.finditer(r'"(VA[A-Za-z0-9_-]{6,})"', html):
        vid = m.group(1)
        if vid in seen:
            continue
        parent = abs_parent_near(html, m.start())
        if not parent:
            continue
        x, y, w, h = parent
        if w < 100 or h < 100:
            continue
        seen.add(vid)
        out.append({"x": x, "y": y, "w": w, "h": h, "id": vid, "kind": "video"})
    return out


def load_maps(html: str):
    media_map = {}
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    for m in data:
        if isinstance(m, dict) and m.get("type") == "media" and m.get("ok") and m.get("id"):
            media_map[m["id"]] = m["file"].replace("\\", "/")

    id_poster = {}
    for m in re.finditer(
        r'"id":"(VA[A-Za-z0-9_-]+)".{0,3500}?"posterframes":\[\{"A":"(_assets/video/([^"]+))"\}',
        html,
    ):
        id_poster[m.group(1)] = m.group(3)

    local = {}
    for f in VIDEO_DIR.glob("*"):
        hm = re.search(r"([a-f0-9]{10,})", f.name)
        if hm:
            local[hm.group(1)[:12]] = f"assets/canva/video/{f.name}"

    video_map = {}
    for vid, fname in id_poster.items():
        stem = Path(fname).stem
        key = stem[:12]
        if key in local:
            video_map[vid] = local[key]
        else:
            for h, p in local.items():
                if h in stem:
                    video_map[vid] = p
                    break
    return media_map, video_map


def assign_creative(x, y, w, h, sections) -> str | None:
    ar = h / w if w else 1
    bts_y = sections["bts"]["y"]

    # Phone-format reels
    if ar >= 1.4 and 160 <= w <= 550 and 1500 <= x <= 2500:
        return "bts" if y >= bts_y - 80 else "final-reel"

    anchors = [
        ("concert", sections["concert"]["x"]),
        ("drone", sections["drone"]["x"]),
        ("automobile", sections["automobile"]["x"]),
        ("weddings", sections["weddings"]["x"]),
    ]

    if x >= 3000:
        xs = [a[1] for a in anchors]
        for i, (key, cx) in enumerate(anchors):
            lo = (xs[i - 1] + cx) / 2 if i > 0 else 3000
            hi = (cx + xs[i + 1]) / 2 if i + 1 < len(xs) else cx + 1600
            if lo <= x < hi:
                return key
        return min(anchors, key=lambda a: abs(a[1] - x))[0]

    # Featured strip between industries and concert (large photos)
    if 2000 <= x < 3000:
        # tall → reel/bts, else distribute by y buckets into featured creatives
        if ar >= 1.35:
            return "bts" if y >= bts_y - 80 else "final-reel"
        # horizontal/square showcases near this band — often wedding/auto montages
        # use image not position: caller may override; default final-reel showcase
        return "final-reel"

    if 1500 <= x < 2000:
        return "bts" if y >= bts_y - 80 else "final-reel"

    return None


def main():
    html = HTML.read_text(encoding="utf-8", errors="ignore")
    sections = {}
    for key, needle in [
        ("final-reel", "Final Reel"),
        ("bts", "BTS\\n"),
        ("industries", "Industries worked with"),
        ("concert", "Hanan Shaah concert"),
        ("drone", "DRONE SHOTS"),
        ("automobile", "Automobile"),
        ("weddings", "WEDDINGS & EVENTS"),
    ]:
        pos = find_label_pos(html, needle) or (
            find_label_pos(html, "BTS") if key == "bts" else None
        )
        if pos:
            sections[key] = pos
            print(f"SECTION {key:12s} x={pos['x']:.1f}")

    media_map, video_map = load_maps(html)
    m_pl, v_pl = media_placements(html), video_placements(html)

    # path -> best placement
    place: dict[str, dict] = {}

    def put(path, it, kind):
        if not path or not (ROOT / path).exists():
            return
        sc = it["w"] * it["h"]
        if path not in place or sc > place[path]["score"]:
            place[path] = {**it, "kind": kind, "score": sc, "path": path}

    for it in m_pl:
        put(media_map.get(it["id"]), it, "media")
    for it in v_pl:
        put(video_map.get(it["id"]), it, "video")

    # all files
    all_files = []
    for f in MEDIA_DIR.glob("*"):
        all_files.append((f"assets/canva/media/{f.name}", "media"))
    for f in VIDEO_DIR.glob("*"):
        all_files.append((f"assets/canva/video/{f.name}", "video"))

    companies = []
    creatives = []
    junk = []

    for rel, kind in all_files:
        full = ROOT / rel
        try:
            a = analyze(full)
        except Exception:
            junk.append(rel)
            continue

        if is_junk(a, full):
            junk.append(rel)
            continue

        meta = place.get(rel)
        has_place = bool(meta and meta.get("score", 0) > 0)
        if not meta:
            meta = {
                "x": 0,
                "y": 0,
                "w": a["w"],
                "h": a["h"],
                "kind": kind,
                "score": 0,
                "id": "",
            }

        # --- logos / companies (media PNGs only — never video posters) ---
        if kind == "media" and is_logo(a, full):
            # keep logos that sit on the site (esp. industries band) or clear brand marks
            if has_place or a["white"] > 0.4:
                companies.append({"path": rel, "x": meta["x"], "y": meta["y"], "a": a})
                continue
            junk.append(rel)
            continue

        # --- creatives: only real photos/videos that appear on the Canva layout ---
        if not is_photo_or_video(a, kind):
            junk.append(rel)
            continue

        # Require on-page placement in portfolio region to avoid junk dumps
        if not has_place or meta["x"] < 1400:
            junk.append(rel)
            continue

        cat = assign_creative(
            meta["x"], meta["y"], meta["w"] or a["w"], meta["h"] or a["h"], sections
        )

        if not cat:
            if has_place and meta["x"] >= 3000:
                anchors = [
                    ("concert", sections["concert"]["x"]),
                    ("drone", sections["drone"]["x"]),
                    ("automobile", sections["automobile"]["x"]),
                    ("weddings", sections["weddings"]["x"]),
                ]
                cat = min(anchors, key=lambda ax: abs(ax[1] - meta["x"]))[0]
            elif has_place and 1400 <= meta["x"] < 3000:
                cat = (
                    "bts"
                    if meta["y"] >= sections["bts"]["y"] - 80
                    else "final-reel"
                )
            else:
                junk.append(rel)
                continue

        if kind == "video" and 1600 <= meta["x"] <= 2500 and meta["y"] >= sections["bts"]["y"] - 80:
            cat = "bts"

        creatives.append(
            {
                "path": rel,
                "cat": cat,
                "type": "video" if kind == "video" else "media",
                "x": meta["x"],
                "y": meta["y"],
                "a": a,
            }
        )

    # Build company items — real brand logos only (not social icons / process numbers)
    companies_sorted = sorted(
        companies,
        key=lambda c: (0 if 1900 <= c["x"] <= 3400 else 1, c["x"], -c["a"]["bytes"]),
    )
    company_items = []
    seen = set()
    for c in companies_sorted:
        if c["path"] in seen:
            continue
        a = c["a"]
        # Drop process numbers (black pads)
        if a["black"] > 0.12:
            continue
        # Social app icons are square with less pure-white canvas
        if 0.85 <= a["ar"] <= 1.15 and a["w"] <= 900 and a["white"] < 0.8:
            continue
        # Brand marks: light canvas logos (Revo, Shobhika, alhind, etc.)
        if a["white"] < 0.45:
            continue
        seen.add(c["path"])
        company_items.append(
            {
                "id": f"co{len(company_items)+1:02d}",
                "title": "Industries worked with",
                "cat": "companies",
                "categoryLabel": "Industries worked with",
                "image": c["path"],
                "visible": True,
                "type": "logo",
                "section": "companies",
            }
        )

    # Creatives — require real media quality
    creative_items = []
    seen_c = set()
    for key, label in CREATIVE_ORDER:
        group = [c for c in creatives if c["cat"] == key]
        group = sorted(group, key=lambda z: (z["y"], z["x"], -z["a"]["bytes"]))
        for c in group:
            if c["path"] in seen_c or c["path"] in seen:
                continue
            # skip weak media chips
            if c["type"] == "media" and c["a"]["bytes"] < 20000:
                continue
            # drop residual flat graphics that slipped past
            if c["a"]["flat"] > 0.85 and c["a"]["variance"] < 1800:
                continue
            seen_c.add(c["path"])
            creative_items.append(
                {
                    "id": f"cr{len(creative_items)+1:03d}",
                    "title": label,
                    "cat": key,
                    "categoryLabel": label,
                    "image": c["path"],
                    "visible": True,
                    "type": c["type"],
                    "section": "creatives",
                    "pageX": round(c["x"], 1),
                    "pageY": round(c["y"], 1),
                }
            )

    categories = [
        {"key": "companies", "label": "Industries worked with", "group": "companies"}
    ] + [
        {"key": k, "label": lab, "group": "creatives"}
        for k, lab in CREATIVE_ORDER
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
    }
    GALLERY_OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    if SITE_JSON.exists():
        site = json.loads(SITE_JSON.read_text(encoding="utf-8"))
        site["portfolio"] = doc["items"]
        site["portfolioCategories"] = categories
        site["companies"] = company_items
        site["creatives"] = creative_items
        SITE_JSON.write_text(json.dumps(site, indent=2), encoding="utf-8")

    META_OUT.write_text(
        json.dumps(
            {
                "companies": [c["image"] for c in company_items],
                "creatives": dict(Counter(i["categoryLabel"] for i in creative_items)),
                "junkCount": len(junk),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\n=== Industries worked with (logos): {len(company_items)} ===")
    for c in company_items:
        print(" ", c["image"])
    print(f"\n=== Creatives: {len(creative_items)} ===")
    for lab, n in Counter(i["categoryLabel"] for i in creative_items).most_common():
        print(f"  {lab}: {n}")
    print(f"\nJunk removed: {len(junk)}")


if __name__ == "__main__":
    main()
