"""Find product-style images that match Koukh al Shay screenshot (food, thermos, tea)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/shots/brands"
OUT.mkdir(parents=True, exist_ok=True)

# Scan all canva media
media_dir = ROOT / "assets/canva/media"
video_dir = ROOT / "assets/canva/video"
candidates = []

for folder in (media_dir, video_dir):
    for p in folder.glob("*"):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        w, h = im.size
        if min(w, h) < 200:
            continue
        small = im.resize((48, 48))
        st = ImageStat.Stat(small)
        mean = sum(st.mean) / 3
        # warm / orange food tones?
        r, g, b = st.mean
        warm = r > g + 5 and r > b + 10
        # bright outdoor product
        bright = mean > 85
        if (warm and mean > 70) or (bright and 0.6 < h / w < 1.5 and p.suffix.lower() in (".jpg", ".jpeg")):
            candidates.append((mean, warm, p, w, h, r, g, b))

candidates.sort(key=lambda t: (-t[1], -t[0]))
print(f"candidates {len(candidates)}")
for mean, warm, p, w, h, r, g, b in candidates[:40]:
    t = Image.open(p).convert("RGB")
    t.thumbnail((220, 220))
    t.save(OUT / f"{p.stem[:40]}.jpg", quality=80)
    print(f"  mean={mean:.0f} warm={warm} {w}x{h} {p.name}")

# Also dump logos
gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))
for co in gal.get("companies") or []:
    p = ROOT / co["image"]
    if p.exists():
        im = Image.open(p).convert("RGB")
        im.thumbnail((320, 120))
        safe = "".join(ch if ch.isalnum() else "_" for ch in co["title"])[:30]
        im.save(OUT / f"LOGO_{safe}.jpg", quality=90)
print("done", OUT)
