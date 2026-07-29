"""Map work images near each company logo on the live Canva layout."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
layout = json.loads((ROOT / "data/live_layout_map.json").read_text(encoding="utf-8"))
gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))

# Known company logos and titles
companies = gal.get("companies") or []
print("Companies:")
for co in companies:
    print(" ", co["title"], co["image"])

# Industries bucket entries with positions
inds = layout["buckets"].get("industries", [])
print("\nIndustries bucket items:")
for e in sorted(inds, key=lambda x: (x.get("x", 0), x.get("y", 0))):
    f = e["file"]
    name = Path(f).name
    print(f"  x={e['x']:7.0f} y={e['y']:6.0f} w={e['w']:6.0f} h={e['h']:6.0f} {name[:50]}")

# Match logos to company and find nearby media (same x band, not logos)
logo_paths = {co["image"]: co for co in companies}

print("\n--- Logo positions ---")
logo_pos = []
for e in inds:
    for co in companies:
        if Path(co["image"]).name in e["file"] or co["image"] in e["file"]:
            logo_pos.append({**e, "company": co["title"], "co": co})
            print(co["title"], "at", e["x"], e["y"], e["w"], e["h"])

# For each logo, collect nearby photo/video entries (not tiny logos)
print("\n--- Nearby work per logo (x within 400, y within 600) ---")
all_entries = []
for bucket, items in layout["buckets"].items():
    for e in items:
        all_entries.append({**e, "bucket": bucket})

# Also list all creatives for manual brand cues
print("\n--- Sample creative files ---")
for c in gal["creatives"][:8]:
    print(c["cat"], Path(c["image"]).name)
