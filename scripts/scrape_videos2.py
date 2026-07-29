import re
import urllib.request

html = urllib.request.urlopen(
    urllib.request.Request(
        "https://byshumail.my.canva.site/",
        headers={"User-Agent": "Mozilla/5.0"},
    ),
    timeout=40,
).read().decode("utf-8", "replace")

# contexts around .mp4
for m in list(re.finditer(r".{0,80}\.mp4.{0,80}", html, re.I))[:15]:
    print(repr(m.group(0))[:200])
    print("---")

# escaped forms
for pat in [r"mp4", r"\\\\.mp4", r"%2Emp4", r"video%2F"]:
    print(pat, len(re.findall(pat, html)))

# look for VA blobs with file refs
vas = re.findall(r'"VA[A-Za-z0-9_-]{6,}"', html)
print("VA quotes", len(vas), "unique", len(set(vas)))

# search binary-ish video refs in json
for m in list(re.finditer(r'"type"\s*:\s*"video"[^}]{0,400}', html, re.I))[:5]:
    print("TYPE", m.group(0)[:300])
    print("---")
