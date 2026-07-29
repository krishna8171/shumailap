"""
Build company-based work classification (logo + name header, work below).
Uses layout proximity to logos + content heuristics + known branded frames.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
layout = json.loads((ROOT / "data/live_layout_map.json").read_text(encoding="utf-8"))
gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))
site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))

companies = gal.get("companies") or []
# Normalize company keys
COMPANY_META = []
for co in companies:
    COMPANY_META.append(
        {
            "id": co["id"],
            "title": co["title"],
            "logo": co["image"],
            "key": co["id"],
        }
    )

# Logo positions from industries bucket
logo_pos = {}
for e in layout["buckets"].get("industries", []):
    for co in companies:
        if Path(co["image"]).name in e["file"]:
            logo_pos[co["id"]] = {
                "x": e["x"],
                "y": e["y"],
                "title": co["title"],
                "logo": co["image"],
            }

print("Logo positions:", {k: (v["title"], round(v["x"]), round(v["y"])) for k, v in logo_pos.items()})

# Collect all media placements across buckets
placements = []
for bucket, items in layout["buckets"].items():
    for e in items:
        placements.append({**e, "bucket": bucket})

# For each logo, find nearby large photos (not logos themselves)
logo_files = {Path(co["image"]).name for co in companies}
deny_ui = (
    "MAFShx0",
    "MAFMK3",
    "MAElfT",
    "MAFfKY",
    "MAFTBi",
    "MAFTBm",
    "MAE8_lt",
    "MAFHg0",
    "MAA9p5",
    "MAD2U3",
    "MADnBo",
    "MAE1Au",
    "MAE3Aa",
    "MAEjDA",
    "MAHPOpv",  # tiny icon
)


def is_work_file(path: str) -> bool:
    name = Path(path).name
    if name in logo_files:
        return False
    if any(d in name for d in deny_ui):
        return False
    full = ROOT / path
    if not full.exists():
        return False
    try:
        im = Image.open(full)
        w, h = im.size
    except Exception:
        return False
    if min(w, h) < 200:
        return False
    # skip pure logo-ish pngs
    if full.suffix.lower() == ".png":
        try:
            im = Image.open(full).convert("RGB").resize((32, 32))
            st = ImageStat.Stat(im)
            if sum(st.var) < 800:
                return False
        except Exception:
            pass
    return True


# Proximity assignment: work near logo Y (vertical stack of brand logos)
# Logos are stacked by Y at x~2200-2600. Work images at similar x band.
company_work: dict[str, list[dict]] = defaultdict(list)
assigned_files: set[str] = set()

# Sort logos by Y
logos_by_y = sorted(logo_pos.items(), key=lambda kv: kv[1]["y"])

# Y bands between logos
bands = []
for i, (cid, pos) in enumerate(logos_by_y):
    y0 = pos["y"] - 80
    y1 = logos_by_y[i + 1][1]["y"] - 40 if i + 1 < len(logos_by_y) else pos["y"] + 250
    bands.append((cid, y0, y1, pos))

print("\nY bands:")
for cid, y0, y1, pos in bands:
    print(f"  {pos['title']}: y {y0:.0f}..{y1:.0f}")

# Assign industries-bucket large media by Y proximity to logo bands
for e in placements:
    f = e["file"]
    if not is_work_file(f):
        continue
    if e.get("w", 0) < 300 and e.get("h", 0) < 300:
        continue
    # Only consider media near industries x range OR large showcase near logos
    x, y = e.get("x", 0), e.get("y", 0)
    if not (1800 <= x <= 3600 or e.get("bucket") == "industries"):
        # still allow later heuristic
        continue
    # find closest logo by Y among those with x nearby
    best = None
    best_d = 1e9
    for cid, y0, y1, pos in bands:
        if y0 <= y <= y1 and abs(x - pos["x"]) < 900:
            d = abs(y - pos["y"])
            if d < best_d:
                best_d = d
                best = cid
    if best and f not in assigned_files:
        company_work[best].append(
            {
                "image": f,
                "type": "video" if e.get("kind") == "video" or "/video/" in f else "media",
                "source": "layout-proximity",
                "x": x,
                "y": y,
            }
        )
        assigned_files.add(f)

# Content heuristics for remaining creatives + unused media
def analyze(path: Path) -> dict:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    small = im.resize((48, 48))
    st = ImageStat.Stat(small)
    r, g, b = st.mean
    mean = (r + g + b) / 3
    return {"w": w, "h": h, "r": r, "g": g, "b": b, "mean": mean, "ar": h / max(w, 1)}


# Map existing creatives by category heuristics when not assigned
CAT_TO_COMPANY = {
    "weddings": None,  # Shobhika - find by title
}

title_to_id = {co["title"]: co["id"] for co in companies}
# Fuzzy
for co in companies:
    t = co["title"].lower()
    if "shobhika" in t:
        CAT_TO_COMPANY["weddings"] = co["id"]
    if "revo" in t:
        revo_id = co["id"]
    if "nakshatra" in t:
        nak_id = co["id"]
    if "koukh" in t or "shay" in t:
        koukh_id = co["id"]
    if "alhind" in t or "hind" in t:
        alhind_id = co["id"]
    if "bahja" in t:
        bahja_id = co["id"]

# Explicit known branded files
KNOWN = {
    "media_044_MAHMpkLpBZA.jpg": "nakshatra",  # NAKSHATRA backdrop
    "media_040_MAHMpjpcp-k.jpg": "koukh",  # food product
    "media_048_MAHMplGf74E.jpg": "revo",  # luxury interior / real estate
}

# resolve known short names to ids
def resolve_short(s: str) -> str | None:
    s = s.lower()
    for co in companies:
        tl = co["title"].lower()
        if s in tl or s.replace("_", " ") in tl:
            return co["id"]
        if s == "koukh" and "koukh" in tl:
            return co["id"]
        if s == "nakshatra" and "nakshatra" in tl:
            return co["id"]
        if s == "revo" and "revo" in tl:
            return co["id"]
    return None


for fname, short in KNOWN.items():
    cid = resolve_short(short)
    path = f"assets/canva/media/{fname}"
    if cid and Path(ROOT / path).exists() and path not in assigned_files and fname not in {Path(x).name for x in assigned_files}:
        company_work[cid].append({"image": path, "type": "media", "source": "known-brand"})
        assigned_files.add(path)

# Assign wedding creatives to Shobhika
shob = next((co["id"] for co in companies if "shobhika" in co["title"].lower()), None)
if shob:
    for c in gal.get("creatives") or []:
        if c.get("cat") == "weddings":
            img = c.get("image")
            if img and img not in assigned_files:
                company_work[shob].append(
                    {
                        "image": img,
                        "video": c.get("video"),
                        "type": c.get("type") or "media",
                        "source": "cat-weddings",
                        "fromCreative": c.get("id"),
                    }
                )
                assigned_files.add(img)

# Scan unused media for more brand work
for p in (ROOT / "assets/canva/media").glob("*.jpg"):
    rel = str(p.relative_to(ROOT)).replace("\\", "/")
    if rel in assigned_files or p.name in logo_files:
        continue
    if any(d in p.name for d in deny_ui):
        continue
    try:
        a = analyze(p)
    except Exception:
        continue
    # food-ish warm bright → koukh
    if a["r"] > a["g"] + 15 and a["r"] > a["b"] + 20 and a["mean"] > 100:
        cid = resolve_short("koukh")
        if cid and len(company_work[cid]) < 12:
            company_work[cid].append({"image": rel, "type": "media", "source": "heuristic-food"})
            assigned_files.add(rel)
            continue
    # bright interior real estate → revo
    if a["mean"] > 140 and a["ar"] < 1.3 and a["w"] >= 1200:
        cid = resolve_short("revo")
        if cid and len([x for x in company_work[cid] if x.get("source") == "heuristic-interior"]) < 8:
            # only a few
            if "heuristic-interior" not in str(company_work[cid]):
                pass
            company_work[cid].append({"image": rel, "type": "media", "source": "heuristic-interior"})
            assigned_files.add(rel)

# Also pull automobile creatives as industry work under a pseudo? No - keep in creatives only.
# Pull some concert stays in creatives.

# Deduplicate and build structured companies with work
out_companies = []
for co in companies:
    cid = co["id"]
    works = company_work.get(cid) or []
    # dedupe by image path
    seen = set()
    clean = []
    for w in works:
        img = w.get("image")
        if not img or img in seen:
            continue
        if not (ROOT / img).exists():
            continue
        seen.add(img)
        clean.append(w)
    out_companies.append(
        {
            "id": cid,
            "title": co["title"],
            "logo": co["image"],
            "cat": "companies",
            "section": "companies",
            "work": clean,
            "workCount": len(clean),
        }
    )
    print(f"{co['title']}: {len(clean)} works")

# Save
out_path = ROOT / "data/company_work.json"
out_path.write_text(json.dumps({"companies": out_companies}, indent=2, ensure_ascii=False), encoding="utf-8")

# Merge into gallery.json + site.json
gal["companies"] = [
    {
        **{k: co[k] for k in ("id", "title", "cat", "categoryLabel", "image", "visible", "type", "section") if k in co or True},
        "id": c["id"],
        "title": c["title"],
        "cat": "companies",
        "categoryLabel": "Industries worked with",
        "image": c["logo"],
        "visible": True,
        "type": "logo",
        "section": "companies",
        "work": c["work"],
        "workCount": c["workCount"],
    }
    for c in out_companies
]
# Fix the messy dict comp above - rewrite cleanly
gal["companies"] = []
for c in out_companies:
    gal["companies"].append(
        {
            "id": c["id"],
            "title": c["title"],
            "cat": "companies",
            "categoryLabel": "Industries worked with",
            "image": c["logo"],
            "visible": True,
            "type": "logo",
            "section": "companies",
            "work": c["work"],
            "workCount": c["workCount"],
        }
    )

# Mark creatives that are now under companies so we can filter portfolio display
company_images = set()
for c in gal["companies"]:
    for w in c.get("work") or []:
        company_images.add(w.get("image"))

for cr in gal.get("creatives") or []:
    img = cr.get("image")
    if img in company_images:
        # find company
        for c in gal["companies"]:
            if any(w.get("image") == img for w in c.get("work") or []):
                cr["companyId"] = c["id"]
                cr["companyName"] = c["title"]
                break

gal["items"] = list(gal["companies"]) + list(gal.get("creatives") or [])
(ROOT / "data/gallery.json").write_text(json.dumps(gal, indent=2, ensure_ascii=False), encoding="utf-8")

site["companies"] = gal["companies"]
site["creatives"] = gal.get("creatives") or []
site["portfolio"] = gal["items"]
(ROOT / "data/site.json").write_text(json.dumps(site, indent=2, ensure_ascii=False), encoding="utf-8")

print("\nWrote data/company_work.json, gallery.json, site.json")
print("Total company works:", sum(c["workCount"] for c in out_companies))
