"""Find social/app icon junk in creatives gallery."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
g = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))
out = ROOT / "assets/shots/icons"
out.mkdir(parents=True, exist_ok=True)

suspects = []
for c in g["creatives"]:
    p = ROOT / c["image"]
    if not p.exists():
        print("MISS", c["image"])
        continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    small = im.resize((64, 64))
    st = ImageStat.Stat(small)
    var = sum(st.var) / max(len(st.var), 1)
    px = list(small.getdata())
    n = len(px)
    black = sum(1 for r, g, b in px if r + g + b < 60) / n
    white = sum(1 for r, g, b in px if r + g + b > 600) / n
    # app icons / flat graphics
    score = 0
    reasons = []
    if black > 0.4:
        score += 2
        reasons.append(f"black={black:.2f}")
    if white > 0.35 and black > 0.2:
        score += 2
        reasons.append(f"white={white:.2f}")
    if var < 1200:
        score += 2
        reasons.append(f"var={var:.0f}")
    if p.suffix.lower() == ".png" and (black > 0.3 or white > 0.4):
        score += 1
        reasons.append("png-flat")
    if min(w, h) < 500 and (black > 0.3 or white > 0.3):
        score += 2
        reasons.append("small")
    # pure black frames
    if black > 0.85:
        score += 3
        reasons.append("near-black")
    if score >= 2:
        thumb = im.copy()
        thumb.thumbnail((220, 220))
        name = f"{c['cat']}_{c['id']}_{p.stem[:28]}.jpg"
        thumb.save(out / name, quality=85)
        suspects.append((score, c["cat"], c["id"], c["image"], reasons, f"{w}x{h}"))
        print(score, c["cat"], c["id"], p.name, reasons, f"{w}x{h}")

print("suspects", len(suspects))
print("thumbs in", out)
