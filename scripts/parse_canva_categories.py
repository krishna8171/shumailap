"""Map Canva portfolio media to Muhammed Shumail's exact work categories."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

HTML = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "canva_categories.json"
GALLERY_OUT = ROOT / "data" / "gallery.json"
SITE_JSON = ROOT / "data" / "site.json"

# Exact labels from byshumail.my.canva.site
PORTFOLIO_LABELS = [
    ("final-reel", "Final Reel", "Final Reel"),
    ("bts", "BTS", "BTS\\n"),
    ("industries", "Industries Worked With", "Industries worked with"),
    ("concert", "Hanan Shaah Concert", "Hanan Shaah concert"),
    ("drone", "Drone Shots", "DRONE SHOTS"),
    ("automobile", "Automobile", "Automobile"),
    ("weddings", "Weddings & Events", "WEDDINGS & EVENTS"),
]


def find_label_pos(html: str, needle: str) -> dict | None:
    i = html.find(needle)
    if i < 0:
        i = html.find(needle.replace("\\n", ""))
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


def abs_parent_near(html: str, pos: int) -> tuple[float, float, float, float] | None:
    back = html[max(0, pos - 3000) : pos]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    best = None
    best_score = -1.0
    for c in coords:
        x, y, w, h = map(float, c.groups())
        if x < 150 or w < 40:
            continue
        score = w * h + c.start() * 0.01
        if score > best_score:
            best_score = score
            best = (x, y, w, h)
    return best


def extract_media_placements(html: str) -> list[dict]:
    items = []
    pat = (
        r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)'
        r'(?:(?!"A":[0-9.eE+-]+,"B":)[\s\S]){0,900}?"A\?":"d","A":"(MA[A-Za-z0-9_-]+)"'
    )
    for m in re.finditer(pat, html):
        x, y, w, h = map(float, m.group(1, 2, 3, 4))
        items.append(
            {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "id": m.group(5),
                "kind": "media",
                "ar": (h / w) if w else 1,
            }
        )
    return items


def extract_video_placements(html: str) -> list[dict]:
    items = []
    seen = set()
    for m in re.finditer(r'"(VA[A-Za-z0-9_-]{6,})"', html):
        vid = m.group(1)
        if vid in seen:
            continue
        parent = abs_parent_near(html, m.start())
        if not parent:
            continue
        x, y, w, h = parent
        if w < 80 or h < 80:
            continue
        seen.add(vid)
        items.append(
            {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "id": vid,
                "kind": "video",
                "ar": (h / w) if w else 1,
            }
        )
    return items


def video_id_to_local(html: str, root: Path) -> dict[str, str]:
    id_poster: dict[str, str] = {}
    for m in re.finditer(
        r'"id":"(VA[A-Za-z0-9_-]+)".{0,3500}?"posterframes":\[\{"A":"(_assets/video/([^"]+))"\}',
        html,
    ):
        id_poster[m.group(1)] = m.group(3)

    local_by_hash: dict[str, str] = {}
    for f in (root / "assets" / "canva" / "video").glob("*"):
        hm = re.search(r"([a-f0-9]{10,})", f.name)
        if hm:
            local_by_hash[hm.group(1)[:12]] = f"assets/canva/video/{f.name}"

    out: dict[str, str] = {}
    for vid, fname in id_poster.items():
        stem = Path(fname).stem
        key = stem[:12]
        if key in local_by_hash:
            out[vid] = local_by_hash[key]
            continue
        for h, path in local_by_hash.items():
            if h in stem:
                out[vid] = path
                break
    return out


def media_id_to_local(root: Path) -> dict[str, str]:
    man = root / "assets" / "canva" / "manifest.json"
    out: dict[str, str] = {}
    if not man.exists():
        return out
    data = json.loads(man.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    for m in data:
        if isinstance(m, dict) and m.get("type") == "media" and m.get("ok") and m.get("id"):
            out[m["id"]] = m["file"].replace("\\", "/")
    return out


def classify(it: dict, sections: dict[str, dict]) -> str:
    """
    Classify one placement using Shumail's horizontal portfolio layout.

    Site structure (left → right):
      Final Reel / BTS (phone reels, stacked by Y)
      Industries Worked With (logos + strip)
      Hanan Shaah Concert
      Drone Shots
      Automobile
      Weddings & Events
    """
    x, y, w, h, ar = it["x"], it["y"], it["w"], it["h"], it.get("ar", 1)

    # Ignore hero / services chrome far left
    if x < 1300:
        return "skip"

    fr = sections["final-reel"]
    bts = sections["bts"]
    ind = sections["industries"]
    con = sections["concert"]
    drn = sections["drone"]
    auto = sections["automobile"]
    wed = sections["weddings"]

    # --- Phone reel column (Final Reel + BTS) ---
    # Tall phone frames near Final Reel X, including phones at ~1900
    is_phone = ar >= 1.45 and 180 <= w <= 500 and h >= 350
    if is_phone and 1600 <= x <= 2400:
        # BTS label y≈856 — content below mid-stack is BTS
        split_y = (fr["y"] + bts["y"]) / 2  # ~511
        # Actually BTS section starts near bts label; phones at y=899 are BTS
        if y >= bts["y"] - 80:
            return "bts"
        return "final-reel"

    # Small UI chips on Final Reel / BTS column
    if 1450 <= x <= 1850:
        if y >= bts["y"] - 40:
            return "bts"
        return "final-reel"

    # --- Mid-page section bands by X (titles are anchors) ---
    # Boundaries = midpoints between section title X positions
    anchors = [
        ("industries", ind["x"]),
        ("concert", con["x"]),
        ("drone", drn["x"]),
        ("automobile", auto["x"]),
        ("weddings", wed["x"]),
    ]
    # left edge after phone column
    left_edge = 2000
    if x < left_edge:
        # strip logos / remaining between phones and industries title
        # industries logos sit around x 2100-2700
        if 2000 <= x < (ind["x"] + con["x"]) / 2:
            # huge full-bleed backgrounds — treat as industries section art
            return "industries"
        if 1450 <= x < 2000:
            return "final-reel" if y < bts["y"] - 40 else "bts"
        return "skip"

    bounds = []
    xs = [a[1] for a in anchors]
    for i, (key, cx) in enumerate(anchors):
        lo = (xs[i - 1] + cx) / 2 if i > 0 else left_edge
        hi = (cx + xs[i + 1]) / 2 if i + 1 < len(xs) else cx + 1200
        bounds.append((lo, hi, key))

    for lo, hi, key in bounds:
        if lo <= x < hi:
            return key

    # nearest anchor
    key = min(anchors, key=lambda a: abs(a[1] - x))[0]
    return key


def main() -> None:
    html = HTML.read_text(encoding="utf-8", errors="ignore")

    sections: dict[str, dict] = {}
    for key, label, needle in PORTFOLIO_LABELS:
        pos = find_label_pos(html, needle)
        if not pos and key == "bts":
            pos = find_label_pos(html, "BTS")
        if not pos:
            print(f"WARN: missing section {label}")
            continue
        sections[key] = {**pos, "key": key, "label": label}
        print(f"SECTION {key:12s}  x={pos['x']:8.1f}  y={pos['y']:7.1f}  {label}")

    media_pl = extract_media_placements(html)
    video_pl = extract_video_placements(html)
    print(f"\nplacements: media={len(media_pl)} video={len(video_pl)}")

    media_map = media_id_to_local(ROOT)
    video_map = video_id_to_local(html, ROOT)

    buckets: dict[str, list[dict]] = {k: [] for k in sections}
    buckets["skip"] = []

    for it in media_pl + video_pl:
        cat = classify(it, sections)
        buckets.setdefault(cat, []).append(it)

    print("\n=== placements by category ===")
    for k, v in buckets.items():
        print(f"  {k}: {len(v)}")

    label_of = {k: sections[k]["label"] for k in sections}
    order = [
        "final-reel",
        "bts",
        "industries",
        "concert",
        "drone",
        "automobile",
        "weddings",
    ]

    gallery: list[dict] = []
    seen: set[str] = set()
    n = 0

    def add(path: str | None, key: str, source: str, kind: str, it: dict):
        nonlocal n
        if not path or path in seen:
            return
        if not (ROOT / path).exists():
            return
        # skip tiny UI chips (< 8kb) from gallery noise — keep real work
        try:
            if (ROOT / path).stat().st_size < 8000 and kind == "media":
                # allow industry logos which can be small pngs
                if key != "industries":
                    return
        except OSError:
            return
        seen.add(path)
        n += 1
        gallery.append(
            {
                "id": f"g{n:03d}",
                "title": label_of.get(key, key),
                "cat": key,
                "categoryLabel": label_of.get(key, key),
                "image": path,
                "visible": True,
                "type": kind,
                "source": source,
                "pageX": round(it["x"], 1),
                "pageY": round(it["y"], 1),
            }
        )

    for key in order:
        items = sorted(buckets.get(key, []), key=lambda it: (it["y"], it["x"]))
        for it in items:
            if it["kind"] == "media":
                add(media_map.get(it["id"]), key, it["id"], "media", it)
            else:
                add(video_map.get(it["id"]), key, it["id"], "video", it)

    categories = [{"key": k, "label": label_of[k]} for k in order if any(g["cat"] == k for g in gallery)]

    result = {
        "layout": "canva-horizontal + phone-column",
        "sections": [
            {"key": k, "label": label_of[k], "x": sections[k]["x"], "y": sections[k]["y"]}
            for k in order
            if k in sections
        ],
        "counts": {
            k: {
                "placements": len(buckets.get(k, [])),
                "gallery": sum(1 for g in gallery if g["cat"] == k),
            }
            for k in order
        },
        "gallery": {"count": len(gallery), "items": gallery},
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gallery_doc = {
        "count": len(gallery),
        "visibleCount": len(gallery),
        "portrait": "assets/portrait.jpg",
        "categories": categories,
        "items": gallery,
    }
    GALLERY_OUT.write_text(json.dumps(gallery_doc, indent=2), encoding="utf-8")

    if SITE_JSON.exists():
        site = json.loads(SITE_JSON.read_text(encoding="utf-8"))
        site["portfolio"] = gallery
        site["portfolioCategories"] = categories
        SITE_JSON.write_text(json.dumps(site, indent=2), encoding="utf-8")

    print(f"\nGallery: {len(gallery)} items")
    for lab, c in Counter(g["categoryLabel"] for g in gallery).most_common():
        print(f"  {lab}: {c}")


if __name__ == "__main__":
    main()
