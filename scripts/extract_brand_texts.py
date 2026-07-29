"""Extract all readable text labels with approximate coords from Canva HTML."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

BASE = "https://byshumail.my.canva.site/"
html = urllib.request.urlopen(
    urllib.request.Request(BASE, headers={"User-Agent": "Mozilla/5.0"}),
    timeout=50,
).read().decode("utf-8", "replace")

# Canva text: "A":"Some text\\n" with coords nearby
# Look for sequences with text content
pattern = re.compile(
    r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)'
    r'.{0,400}?"A":"([^"]{2,80})\\\\n"',
    re.S,
)

hits = []
for m in pattern.finditer(html):
    x, y, w, h = map(float, m.group(1, 2, 3, 4))
    text = m.group(5).replace("\\n", " ").strip()
    if len(text) < 2:
        continue
    hits.append((x, y, text))

# dedupe by text keeping first
seen = set()
uniq = []
for x, y, t in sorted(hits, key=lambda z: (z[0], z[1])):
    key = t.lower()
    if key in seen:
        continue
    seen.add(key)
    uniq.append((x, y, t))

print(f"unique texts: {len(uniq)}")
for x, y, t in uniq:
    # print all reasonably short labels
    if len(t) < 60:
        print(f"x={x:8.1f} y={y:7.1f}  {t}")

# Save
Path("data/canva_texts.json").write_text(
    __import__("json").dumps([{"x": x, "y": y, "text": t} for x, y, t in uniq], indent=2),
    encoding="utf-8",
)
print("wrote data/canva_texts.json")
