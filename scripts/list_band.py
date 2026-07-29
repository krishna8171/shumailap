import re
from pathlib import Path

html = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html").read_text(
    encoding="utf-8", errors="ignore"
)

items = []
pat = (
    r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)'
    r'(?:(?!"A":[0-9.eE+-]+,"B":)[\s\S]){0,900}?"A\?":"d","A":"(MA[A-Za-z0-9_-]+)"'
)
for m in re.finditer(pat, html):
    x, y, w, h = map(float, m.group(1, 2, 3, 4))
    items.append((x, y, w, h, m.group(5)))

band = sorted([i for i in items if 1400 <= i[0] <= 3400], key=lambda t: (t[0], t[1]))
print("media in x 1400-3400:", len(band))
for x, y, w, h, mid in band:
    ar = h / w if w else 0
    kind = "phone" if ar > 1.4 else ("wide" if ar < 0.85 else "sq")
    print(f"  x={x:7.1f} y={y:7.1f} w={w:6.1f} h={h:6.1f} ar={ar:.2f} {kind:5s} {mid}")

# videos in same band via parent walk
print("\nvideos:")
seen = set()
for m in re.finditer(r'"(VA[A-Za-z0-9_-]{6,})"', html):
    vid = m.group(1)
    if vid in seen:
        continue
    back = html[max(0, m.start() - 3000) : m.start()]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    best = None
    score = -1
    for c in coords:
        x, y, w, h = map(float, c.groups())
        if x < 150 or w < 40:
            continue
        sc = w * h + c.start() * 0.01
        if sc > score:
            score = sc
            best = (x, y, w, h)
    if not best:
        continue
    x, y, w, h = best
    if 1400 <= x <= 3400:
        seen.add(vid)
        ar = h / w if w else 0
        print(f"  x={x:7.1f} y={y:7.1f} w={w:6.1f} h={h:6.1f} ar={ar:.2f} {vid}")
