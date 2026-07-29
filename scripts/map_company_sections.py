"""Discover company/brand sections on live Canva site."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://byshumail.my.canva.site/"

html = urllib.request.urlopen(
    urllib.request.Request(BASE, headers={"User-Agent": "Mozilla/5.0"}),
    timeout=50,
).read().decode("utf-8", "replace")
print("html", len(html))

# Text content patterns in Canva export
texts = re.findall(r'"A"\s*:\s*"([^"\\]{2,80})(?:\\\\n)?"', html)
# also escaped
texts2 = re.findall(r'"A":"([^"]{2,80})\\\\n"', html)
all_t = []
for t in texts + texts2:
    t = t.replace("\\n", " ").replace("\\\\n", " ").strip()
    if t:
        all_t.append(t)

# unique preserve order
seen = set()
uniq = []
for t in all_t:
    if t not in seen:
        seen.add(t)
        uniq.append(t)

keywords = [
    "Koukh",
    "Nakshatra",
    "alhind",
    "Alhind",
    "Shobhika",
    "Bahja",
    "Revo",
    "NEWIZZ",
    "Newizz",
    "Shay",
    "Gold",
    "Wedding",
    "Realty",
    "Hind",
    "Industr",
    "Final",
    "BTS",
    "Concert",
    "Hanan",
    "Drone",
    "Automobile",
    "WEDDING",
    "Port Folio",
    "Portfolio",
]
print("--- interesting labels ---")
for t in uniq:
    if any(k.lower() in t.lower() for k in keywords):
        print(" ", t)

# Search brand names with context
print("--- brand hits ---")
for brand in [
    "Koukh",
    "Nakshatra",
    "alhind",
    "Shobhika",
    "Bahja",
    "Revo",
    "NEWIZZ",
    "Newizz",
]:
    for m in re.finditer(re.escape(brand), html, re.I):
        ctx = html[max(0, m.start() - 30) : m.end() + 50]
        print(brand, ":", repr(ctx)[:120])
        break

# Layout map sections
layout = json.loads((ROOT / "data/live_layout_map.json").read_text(encoding="utf-8"))
print("--- layout sections ---")
for s in layout["sections"]:
    print(f"  x={s['x']:.0f} y={s['y']:.0f}  {s['key']:15} {s['label']}")

# Look for text elements with x positions near brands in map if available
if "texts" in layout:
    print("texts in layout", len(layout["texts"]))
