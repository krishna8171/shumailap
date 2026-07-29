from pathlib import Path
import re

html = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html").read_text(
    encoding="utf-8", errors="ignore"
)

# Find text content patterns
for label in [
    "Industries worked with",
    "Final Reel",
    "BTS",
    "Hanan Shaah concert",
    "Automobile",
    "WEDDINGS & EVENTS",
    "DRONE SHOTS",
    "Port Folio",
    "Creating Visuals",
    "NEWIZZ",
    "Revo",
    "ACHIEVEMENTS",
    "Expertise",
    "MY CREATIVE",
]:
    i = html.find(label)
    print(f"{label!r:30s} idx={i}")

print("\n--- sample text blobs ---")
# extract all A":"...\\n" short strings
blobs = re.findall(r'"A":"([^"]{2,80})\\n"', html)
uniq = []
seen = set()
for b in blobs:
    t = b.replace("\\n", " ").strip()
    if t in seen:
        continue
    if not re.search(r"[A-Za-z]{3,}", t):
        continue
    if re.match(r"^(MA|VA|TA|LB|PB|YA)", t):
        continue
    seen.add(t)
    uniq.append(t)

for t in uniq:
    print(" •", t)
