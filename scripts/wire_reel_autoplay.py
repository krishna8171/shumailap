"""
Precise poster→mp4 wiring for Canva reels + download for muted autoplay.
Strategy:
1. Find each full poster hash in HTML.
2. Within a tight window, collect mp4 hashes and pick best quality.
3. Prefer unique 1:1 assignment; fall back carefully.
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

# Full poster hashes from video-list (order matches original scrape naming)
full_posters: list[str] = []
list_path = ROOT / "assets/canva/video-list.txt"
if list_path.exists():
    for line in list_path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"/([a-f0-9]{20,})\.(?:jpg|png)", line, re.I)
        if m:
            full_posters.append(m.group(1).lower())
print("posters", len(full_posters))

# Quality map for mp4 hashes
qualities: dict[str, list[tuple[int, int]]] = defaultdict(list)
for h, w, ht in re.findall(
    r'"url"\s*:\s*"_assets/video/([a-f0-9]+)\.mp4"\s*,\s*"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)',
    html,
    re.I,
):
    qualities[h.lower()].append((int(w), int(ht)))
for h, w, ht in re.findall(
    r'"1"\s*:\s*"_assets/video/([a-f0-9]+)\.mp4"\s*,\s*"A"\s*:\s*(\d+)\s*,\s*"B"\s*:\s*(\d+)',
    html,
    re.I,
):
    qualities[h.lower()].append((int(w), int(ht)))


def best_quality(hashes: list[str]) -> str | None:
    if not hashes:
        return None

    def score(h: str) -> tuple:
        qs = qualities.get(h) or []
        if not qs:
            return (0, 0, 0)
        # Prefer ~720px width portrait
        pick = max(qs, key=lambda t: t[0] * t[1])
        for q in qs:
            if 640 <= q[0] <= 800:
                pick = q
                break
        w, ht = pick
        return (1 if ht >= w * 1.1 else 0, -abs(w - 720), w * ht)

    return max(set(hashes), key=score)


# For each poster, find mp4s by distance in HTML (closest wins)
poster_best: dict[str, str] = {}
for ph in full_posters:
    best_mp4 = None
    best_dist = 10**12
    for m in re.finditer(re.escape(ph), html, re.I):
        pos = m.start()
        # search ±1800 chars for mp4 refs
        lo, hi = max(0, pos - 1800), min(len(html), pos + 1800)
        window = html[lo:hi]
        for mm in re.finditer(r"_assets/video/([a-f0-9]+)\.mp4", window, re.I):
            mh = mm.group(1).lower()
            # absolute position of this mp4 match
            abs_pos = lo + mm.start()
            dist = abs(abs_pos - pos)
            if dist < best_dist:
                best_dist = dist
                best_mp4 = mh
        # also look for files array shortly after "id":"VA..." near poster
    if best_mp4:
        poster_best[ph] = best_mp4

print(f"poster→mp4 closest pairs: {len(poster_best)}")
print(f"unique mp4 targets: {len(set(poster_best.values()))}")

# prefix map
prefix_to_full = {ph[:12]: ph for ph in full_posters}
prefix_to_full.update({ph[:10]: ph for ph in full_posters})

g = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))

assignments: list[tuple[dict, str, str]] = []  # item, poster_full, mp4hash
for c in g.get("creatives") or []:
    img = c.get("image") or ""
    if "/video/" not in img and c.get("type") != "video":
        continue
    m = re.search(r"([a-f0-9]{10,})", Path(img).stem, re.I)
    if not m:
        continue
    pref = m.group(1).lower()
    full = prefix_to_full.get(pref[:12]) or prefix_to_full.get(pref[:10])
    if not full:
        for k, v in prefix_to_full.items():
            if k.startswith(pref) or pref.startswith(k):
                full = v
                break
    if not full or full not in poster_best:
        print("  unmatched", pref, Path(img).name)
        # clear bad previous video
        c.pop("video", None)
        continue
    mp4h = poster_best[full]
    assignments.append((c, full, mp4h))

print(f"gallery assignments: {len(assignments)}")
print(f"unique mp4s for gallery: {len({a[2] for a in assignments})}")

needed = {mp4h for _, _, mp4h in assignments}

opener = urllib.request.build_opener()
opener.addheaders = [("User-Agent", "Mozilla/5.0 Chrome/120"), ("Referer", BASE)]

downloaded: dict[str, str] = {}
for i, h in enumerate(sorted(needed)):
    dest = OUT / f"reel_{h[:16]}.mp4"
    if dest.exists() and dest.stat().st_size > 40000:
        downloaded[h] = str(dest.relative_to(ROOT)).replace("\\", "/")
        continue
    url = f"{BASE}_assets/video/{h}.mp4"
    try:
        with opener.open(url, timeout=120) as r:
            data = r.read()
        if len(data) < 15000:
            print("  small", h[:12], len(data))
            continue
        dest.write_bytes(data)
        downloaded[h] = str(dest.relative_to(ROOT)).replace("\\", "/")
        print(f"  ok {len(downloaded)}/{len(needed)} {dest.name} {len(data)//1024}kb")
    except Exception as e:
        print("  FAIL", h[:12], e)

# Clear all previous video fields then set correct ones
for c in g.get("creatives") or []:
    if c.get("video") and "/reels/" in str(c.get("video")):
        # will re-set if assigned
        pass
    # reset playable path; keep type hint
    if "video" in c and str(c.get("video", "")).endswith(".mp4"):
        # only clear our reels folder assignments
        if "canva/reels" in str(c.get("video")):
            del c["video"]

assigned = 0
for c, full, mp4h in assignments:
    if mp4h in downloaded:
        c["video"] = downloaded[mp4h]
        c["type"] = "video"
        assigned += 1
    else:
        c.pop("video", None)

print(f"assigned playable reels: {assigned}")

g["items"] = list(g.get("companies") or []) + list(g.get("creatives") or [])
g["creativesCount"] = len(g.get("creatives") or [])
(ROOT / "data/gallery.json").write_text(
    json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8"
)

s = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
s["creatives"] = g["creatives"]
s["companies"] = g.get("companies") or s.get("companies") or []
s["portfolio"] = list(s["companies"]) + list(s["creatives"])
(ROOT / "data/site.json").write_text(
    json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8"
)

# Save map for debugging
(ROOT / "data/reel_assignments.json").write_text(
    json.dumps(
        [
            {
                "id": c.get("id"),
                "image": c.get("image"),
                "video": c.get("video"),
                "poster": full,
                "mp4": mp4h,
            }
            for c, full, mp4h in assignments
        ],
        indent=2,
    ),
    encoding="utf-8",
)
print("synced site.json + reel_assignments.json")
