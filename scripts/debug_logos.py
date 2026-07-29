import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rebuild_gallery import (  # noqa
    analyze,
    find_label_pos,
    is_junk,
    is_logo,
    load_maps,
    media_placements,
)

html = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html").read_text(
    encoding="utf-8", errors="ignore"
)
media_map, _ = load_maps(html)
m_pl = media_placements(html)
place = {}
for it in m_pl:
    p = media_map.get(it["id"])
    if not p:
        continue
    sc = it["w"] * it["h"]
    if p not in place or sc > place[p]["score"]:
        place[p] = {**it, "score": sc}

root = Path(__file__).resolve().parents[1]
for f in sorted((root / "assets/canva/media").glob("*.png")):
    rel = f"assets/canva/media/{f.name}"
    try:
        a = analyze(f)
    except Exception as e:
        print(f.name, "ERR", e)
        continue
    if is_junk(a, f):
        continue
    if not is_logo(a, f):
        continue
    meta = place.get(rel, {"x": 0, "y": 0})
    print(
        f"{f.name:42s} x={meta['x']:7.1f} white={a['white']:.2f} "
        f"black={a['black']:.2f} ar={a['ar']:.2f} var={a['variance']:.0f}"
    )
