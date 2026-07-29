"""Remove social/app icon junk from creatives gallery + sync site.json."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Confirmed junk from screenshots + icon scan
JUNK_SUBSTRINGS = (
    "media_000_MAA9p5KWXCY",  # white circles
    "media_001_MAD2U3W6DDA",  # process number 1 circles
    "media_002_MADnBoBFUeY",  # Gmail
    "media_003_MAE1AuWxAmE",  # LinkedIn
    "media_004_MAE3Aa_nr44",  # email envelope circles
    "media_006_MAEjDAuyytM",  # clapperboard / reels icons
    "media_007_MAElfTPish0",  # IG
    "media_009_MAFfKYTpv5s",  # WA
    "MAFShx0XtCw",  # arrows
    "MAFMK3m-Qqw",  # sparkles
    "MAFTBi1WAvo",  # process bars
    "MAFTBmGra3o",
    "MAE8_lt1Pww",  # empty phone
)

gpath = ROOT / "data/gallery.json"
spath = ROOT / "data/site.json"
g = json.loads(gpath.read_text(encoding="utf-8"))
s = json.loads(spath.read_text(encoding="utf-8"))


def is_junk(path: str) -> bool:
    name = Path(path).name
    return any(j in name or j in path for j in JUNK_SUBSTRINGS)


before = len(g.get("creatives") or [])
removed = []
creatives = []
for c in g.get("creatives") or []:
    img = c.get("image") or c.get("video") or ""
    if is_junk(img):
        removed.append((c.get("cat"), img))
        continue
    creatives.append(c)

print("removed:")
for r in removed:
    print(" ", r)
print(f"creatives {before} -> {len(creatives)}")
print(Counter(c.get("cat") for c in creatives))

companies = g.get("companies") or s.get("companies") or []
g["creatives"] = creatives
g["items"] = list(companies) + creatives
g["count"] = len(g["items"])
g["creativesCount"] = len(creatives)
g["companiesCount"] = len(companies)
gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8")

s["creatives"] = creatives
s["companies"] = companies
s["portfolio"] = list(companies) + creatives
if g.get("categories"):
    s["portfolioCategories"] = g["categories"]
spath.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
print("synced gallery.json + site.json")
