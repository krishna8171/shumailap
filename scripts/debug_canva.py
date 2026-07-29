import re
from pathlib import Path

html = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html").read_text(
    encoding="utf-8", errors="ignore"
)

for label in ["Final Reel", "BTS", "Automobile", "DRONE SHOTS", "WEDDINGS", "Hanan"]:
    i = html.find(label)
    print(f"\n===== {label} at {i} =====")
    if i < 0:
        continue
    snip = html[max(0, i - 400) : i + 200]
    print(snip)

print("\n===== counts =====")
print("A?:d", len(re.findall(r'"A\?":"d"', html)))
print("MA ids", len(re.findall(r'"A":"(MA[A-Za-z0-9_-]+)"', html)))
print("VA ids", len(re.findall(r'"A":"(VA[A-Za-z0-9_-]+)"', html)))

# Find element with Final Reel text - look for full element structure
i = html.find("Final Reel")
# walk back to find "A":x,"B":y for this text element
back = html[max(0, i - 2000) : i]
# last A,B,D,C before text
coords = list(
    re.finditer(
        r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
        back,
    )
)
print("\ncoords before Final Reel:", len(coords))
if coords:
    print("last coord", coords[-1].groups())
    print("context", back[coords[-1].start() : coords[-1].start() + 200])

# How are videos embedded?
i = html.find("VAH")
print("\nfirst VAH", i)
print(html[i : i + 300] if i > 0 else "none")

# look for contentType VIDEO near id
m = re.search(r'"id":"(VA[^"]+)".{0,80}', html)
print("video id sample", m.group(0) if m else None)
