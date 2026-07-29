"""
Parse live Canva site for reel MP4 URLs, download them, and attach
playable video paths to matching gallery creatives (by poster hash / VA id).
"""
from __future__ import annotations

import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/canva/reels"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://byshumail.my.canva.site/"

print("Fetching Canva HTML…")
html = urllib.request.urlopen(
    urllib.request.Request(BASE, headers={"User-Agent": "Mozilla/5.0 Chrome/120"}),
    timeout=60,
).read().decode("utf-8", "replace")

# Pattern A: "url":"_assets/video/HASH.mp4","width":W,"height":H
entries = re.findall(
    r'"url"\s*:\s*"(_assets/video/([a-f0-9]+)\.mp4)"\s*,\s*"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)',
    html,
    re.I,
)
# Pattern B: "1":"_assets/video/HASH.mp4","A":W,"B":H
entries_b = re.findall(
    r'"1"\s*:\s*"(_assets/video/([a-f0-9]+)\.mp4)"\s*,\s*"A"\s*:\s*(\d+)\s*,\s*"B"\s*:\s*(\d+)',
    html,
    re.I,
)

by_hash: dict[str, dict] = {}
for url, h, w, ht in entries + entries_b:
    w, ht = int(w), int(ht)
    # Prefer highest resolution per hash
    prev = by_hash.get(h)
    if not prev or (w * ht) > prev["w"] * prev["h"]:
        by_hash[h] = {"url": url, "hash": h, "w": w, "h": ht}

print(f"unique mp4 hashes: {len(by_hash)}")

# Prefer phone-ish reels (portrait) first for quality picks, but keep all
portrait = [v for v in by_hash.values() if v["h"] >= v["w"] * 1.2]
print(f"portrait-ish: {len(portrait)}")

# Also map VA id -> best file
va_blocks = re.findall(
    r'"id"\s*:\s*"(VA[A-Za-z0-9_-]+)"\s*,\s*"files"\s*:\s*\[(.*?)\]',
    html,
    re.S,
)
va_to_hash: dict[str, str] = {}
for va, files in va_blocks:
    m = re.findall(r'_assets/video/([a-f0-9]+)\.mp4"[^}]*?"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)', files)
    if not m:
        m = re.findall(r'_assets/video/([a-f0-9]+)\.mp4', files)
        if m:
            va_to_hash[va] = m[0]
        continue
    best = max(m, key=lambda t: int(t[1]) * int(t[2]))
    va_to_hash[va] = best[0]
print(f"VA ids mapped: {len(va_to_hash)}")

# Download best quality versions (cap size — prefer 720p portrait)
downloaded: dict[str, str] = {}  # hash -> local path
# Prefer mid quality 720-wide to keep downloads reasonable
candidates = sorted(by_hash.values(), key=lambda v: (-(v["h"] >= v["w"]), -(v["w"] * v["h"])))

# Deduplicate by downloading each hash once; skip tiny 180px
to_get = []
seen = set()
for v in candidates:
    if v["hash"] in seen:
        continue
    if v["w"] < 300 and v["h"] < 300:
        continue
    # skip ultra large 1080 if we already have 720 for same... each hash is unique file
    seen.add(v["hash"])
    to_get.append(v)

print(f"will try download {len(to_get)} files")

opener = urllib.request.build_opener()
opener.addheaders = [("User-Agent", "Mozilla/5.0 Chrome/120"), ("Referer", BASE)]

ok = 0
fail = 0
for i, v in enumerate(to_get):
    dest = OUT / f"reel_{v['hash'][:12]}_{v['w']}x{v['h']}.mp4"
    if dest.exists() and dest.stat().st_size > 50000:
        downloaded[v["hash"]] = str(dest.relative_to(ROOT)).replace("\\", "/")
        ok += 1
        continue
    url = BASE + v["url"].lstrip("/")
    try:
        with opener.open(url, timeout=90) as r:
            data = r.read()
        if len(data) < 10000 or data[:3] != b"\x00\x00\x00" and b"ftyp" not in data[:64]:
            # still write if large enough
            if len(data) < 20000:
                fail += 1
                print("  skip small/bad", v["hash"][:12], len(data))
                continue
        dest.write_bytes(data)
        downloaded[v["hash"]] = str(dest.relative_to(ROOT)).replace("\\", "/")
        ok += 1
        if (i + 1) % 10 == 0:
            print(f"  downloaded {i+1}/{len(to_get)} …")
    except Exception as e:
        fail += 1
        print("  FAIL", v["hash"][:12], e)

print(f"downloaded ok={ok} fail={fail} mapped={len(downloaded)}")

# Save mapping
map_path = ROOT / "data/reel_map.json"
map_path.write_text(
    json.dumps(
        {
            "byHash": downloaded,
            "vaToHash": va_to_hash,
            "sources": {h: by_hash[h] for h in downloaded if h in by_hash},
        },
        indent=2,
    ),
    encoding="utf-8",
)
print("wrote", map_path)

# Match gallery video posters to mp4s
# Our posters are named video_NNN_<12hex>.jpg — hex is prefix of full hash
gpath = ROOT / "data/gallery.json"
spath = ROOT / "data/site.json"
g = json.loads(gpath.read_text(encoding="utf-8"))
s = json.loads(spath.read_text(encoding="utf-8"))

prefix_to_hash = defaultdict(list)
for h in downloaded:
    prefix_to_hash[h[:12]].append(h)
    prefix_to_hash[h[:10]].append(h)

def match_video(path: str) -> str | None:
    name = Path(path).stem  # video_064_e828077b1735
    # extract trailing hex
    m = re.search(r"([a-f0-9]{10,})$", name, re.I)
    if not m:
        return None
    pref = m.group(1).lower()
    # exact prefix match
    for length in (12, 10, 8):
        key = pref[:length]
        if key in prefix_to_hash:
            # pick highest res among candidates
            hashes = prefix_to_hash[key]
            best = max(hashes, key=lambda hh: by_hash.get(hh, {}).get("w", 0) * by_hash.get(hh, {}).get("h", 0))
            return downloaded.get(best)
    # fuzzy: any downloaded hash startswith pref or pref startswith hash start
    for h, local in downloaded.items():
        if h.startswith(pref) or pref.startswith(h[: len(pref)]):
            return local
    return None

# Also try matching full content hash from original video-list filenames
# video-list has full hashes like ba13bb69e67c6e961422d3effb41f47b
list_path = ROOT / "assets/canva/video-list.txt"
full_hashes = []
if list_path.exists():
    for line in list_path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"/([a-f0-9]{20,})\.(?:jpg|png|mp4)", line, re.I)
        if m:
            full_hashes.append(m.group(1).lower())

# Build index: short poster id -> full hash from list order
# Our files: video_000_ba13bb69e67c.jpg maps to list line 1 hash start ba13bb69e67c

assigned = 0
for arr_name in ("creatives", "items"):
    arr = g.get(arr_name) or []
    for item in arr:
        img = item.get("image") or ""
        if "/video/" not in img and item.get("type") != "video":
            continue
        if item.get("video") and str(item["video"]).endswith(".mp4"):
            continue
        local = match_video(img)
        if not local:
            # try full list hash by short prefix in filename
            m = re.search(r"([a-f0-9]{10,})", Path(img).stem, re.I)
            if m:
                pref = m.group(1).lower()
                for fh in full_hashes:
                    if fh.startswith(pref) and fh in downloaded:
                        local = downloaded[fh]
                        break
                    if fh.startswith(pref):
                        # download missing full hash?
                        pass
        if local:
            item["video"] = local
            item["type"] = "video"
            assigned += 1

print(f"assigned video files to {assigned} gallery items")

# If few matched by prefix, assign remaining portrait reels round-robin to video-type items missing video
unmatched = [c for c in (g.get("creatives") or []) if (c.get("type") == "video" or "/video/" in (c.get("image") or "")) and not (c.get("video") or "").endswith(".mp4")]
pool = [p for p in downloaded.values()]
# prefer portrait files
portrait_paths = []
for h, p in downloaded.items():
    meta = by_hash.get(h, {})
    if meta.get("h", 0) >= meta.get("w", 1) * 1.15:
        portrait_paths.append(p)
if not portrait_paths:
    portrait_paths = pool

print(f"unmatched video posters: {len(unmatched)}; portrait pool: {len(portrait_paths)}")
# Don't randomly assign wrong videos - only prefix matches
# User wants autoplay - better correct match than wrong reel

gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8")

# sync site
s["creatives"] = g.get("creatives") or []
s["companies"] = g.get("companies") or s.get("companies") or []
s["portfolio"] = list(s["companies"]) + list(s["creatives"])
spath.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
print("done")
