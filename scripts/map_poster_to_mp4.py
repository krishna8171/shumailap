"""Map poster jpg hashes to mp4 hashes from Canva HTML VA structures."""
import re
import urllib.request
from pathlib import Path

BASE = "https://byshumail.my.canva.site/"
html = urllib.request.urlopen(
    urllib.request.Request(BASE, headers={"User-Agent": "Mozilla/5.0"}),
    timeout=60,
).read().decode("utf-8", "replace")

# Find pairs of poster jpg and mp4 near each other
# posters: _assets/video/HASH.jpg
posters = re.findall(r"_assets/video/([a-f0-9]+)\.jpg", html, re.I)
mp4s = re.findall(r"_assets/video/([a-f0-9]+)\.mp4", html, re.I)
print("poster refs", len(posters), "unique", len(set(posters)))
print("mp4 refs", len(mp4s), "unique", len(set(mp4s)))
print("overlap", len(set(p.lower() for p in posters) & set(m.lower() for m in mp4s)))

# In same VA files array, both may appear
# Search windows around each mp4 for nearby jpg
pairs = []
for m in re.finditer(r"_assets/video/([a-f0-9]+)\.mp4", html, re.I):
    start = max(0, m.start() - 2500)
    end = min(len(html), m.end() + 500)
    window = html[start:end]
    jpgs = re.findall(r"_assets/video/([a-f0-9]+)\.jpg", window, re.I)
    if jpgs:
        pairs.append((jpgs[-1].lower(), m.group(1).lower()))

print("window pairs", len(pairs))
# unique poster -> set of mp4
from collections import defaultdict
p2m = defaultdict(set)
for j, m in pairs:
    p2m[j].add(m)
print("posters with mp4 neighbor", len(p2m))
for i, (j, ms) in enumerate(list(p2m.items())[:8]):
    print(j[:16], "->", [x[:16] for x in ms])

# Save for download script
Path("data/poster_mp4_pairs.json").write_text(
    __import__("json").dumps({k: sorted(v) for k, v in p2m.items()}, indent=2),
    encoding="utf-8",
)
print("wrote data/poster_mp4_pairs.json")
