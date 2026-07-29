import re
from pathlib import Path

html = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html").read_text(
    encoding="utf-8", errors="ignore"
)

# Find video fill patterns and surrounding absolute coords of parent image frames
# Look for elements with type that embed videos - "A?":"I" frames containing video

# Pattern: large frames with high X that contain VA references
# Search each VA id occurrence and walk back for largest nearby absolute A (x) value > 500

va_ids = list(dict.fromkeys(re.findall(r'"(VA[A-Za-z0-9_-]{6,})"', html)))
print("unique VA ids", len(va_ids))

samples = []
for vid in va_ids[:15]:
    positions = [m.start() for m in re.finditer(re.escape(f'"{vid}"'), html)]
    for pos in positions[:2]:
        back = html[max(0, pos - 2500) : pos]
        coords = list(
            re.finditer(
                r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
                back,
            )
        )
        # pick coord with largest |x| that looks absolute (x > 200)
        best = None
        for c in coords:
            x = float(c.group(1))
            y = float(c.group(2))
            w = float(c.group(3))
            h = float(c.group(4))
            if x > 200 and w > 50:
                best = (x, y, w, h)
        samples.append((vid, best, len(coords), pos))

print("\nSample video absolute parents:")
for vid, best, n, pos in samples:
    print(f"  {vid}: parent={best} coords_found={n}")

# Count how many get x>1000
abs_count = sum(1 for _, b, _, _ in samples if b and b[0] > 1000)
print("with abs x>1000 among samples", abs_count)

# Industries / Final reel x bands from earlier
# industries x~2068, final-reel x~1627, concert 4059, drone 4457, auto 5031, weddings 7771
