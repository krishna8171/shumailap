"""Map live Canva portfolio: section labels + which MA/VA ids sit under each."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

HTML = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail-live.html")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "live_layout_map.json"

# Exact labels from his site (portfolio strip order roughly L→R)
LABELS = [
    ("industries", "Industries worked with", "Industries worked with"),
    ("final-reel", "Final Reel", "Final Reel"),
    ("bts", "BTS", "BTS\\n"),
    ("concert", "Hanan Shaah Concert", "Hanan Shaah concert"),
    ("automobile", "Automobile", "Automobile"),
    ("weddings", "Weddings & Events", "WEDDINGS & EVENTS"),
    ("drone", "Drone Shots", "DRONE SHOTS"),
]


def find_label(html: str, needle: str):
    i = html.find(needle)
    if i < 0:
        i = html.find(needle.replace("\\n", ""))
    if i < 0:
        return None
    back = html[max(0, i - 600) : i]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    if not coords:
        return None
    x, y, w, h = map(float, coords[-1].groups())
    return {"x": x, "y": y, "w": w, "h": h, "idx": i}


def abs_parent(html: str, pos: int):
    back = html[max(0, pos - 3500) : pos]
    coords = list(
        re.finditer(
            r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)',
            back,
        )
    )
    best, score = None, -1.0
    for c in coords:
        x, y, w, h = map(float, c.groups())
        if x < 100 or w < 30:
            continue
        sc = w * h + c.start() * 0.01
        if sc > score:
            score = sc
            best = (x, y, w, h)
    return best


def media_id_files(html: str) -> dict[str, list[dict]]:
    """id -> list of files by quality"""
    out = defaultdict(list)
    for m in re.finditer(
        r'"id":"(MA[A-Za-z0-9_-]+)","version":\d+,"files":\[\{"url":"(_assets/media/[^"]+)".*?"width":(\d+),"height":(\d+).*?"quality":"([^"]+)"',
        html,
    ):
        mid, url, w, h, q = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
        out[mid].append({"url": url, "w": w, "h": h, "q": q, "area": w * h})
    return out


def best_file(files: list[dict]) -> dict:
    return max(files, key=lambda f: f["area"])


def main():
    html = HTML.read_text(encoding="utf-8", errors="ignore")
    sections = []
    for key, label, needle in LABELS:
        pos = find_label(html, needle)
        if not pos and key == "bts":
            pos = find_label(html, "BTS")
        if pos:
            sections.append({**pos, "key": key, "label": label})
            print(f"{key:12s} x={pos['x']:8.1f} y={pos['y']:7.1f}  {label}")
        else:
            print(f"MISSING {key}")

    sections_sorted = sorted(sections, key=lambda s: (s["x"], s["y"]))

    # placements media
    media_pl = []
    pat = (
        r'"A":([0-9.eE+-]+),"B":([0-9.eE+-]+),"D":([0-9.eE+-]+),"C":([0-9.eE+-]+)'
        r'(?:(?!"A":[0-9.eE+-]+,"B":)[\s\S]){0,900}?"A\?":"d","A":"(MA[A-Za-z0-9_-]+)"'
    )
    for m in re.finditer(pat, html):
        x, y, w, h = map(float, m.group(1, 2, 3, 4))
        media_pl.append({"x": x, "y": y, "w": w, "h": h, "id": m.group(5), "kind": "media"})

    video_pl = []
    seen = set()
    for m in re.finditer(r'"(VA[A-Za-z0-9_-]{6,})"', html):
        vid = m.group(1)
        if vid in seen:
            continue
        parent = abs_parent(html, m.start())
        if not parent:
            continue
        x, y, w, h = parent
        if w < 80 or h < 80:
            continue
        seen.add(vid)
        video_pl.append({"x": x, "y": y, "w": w, "h": h, "id": vid, "kind": "video"})

    def assign(it, secs):
        x, y = it["x"], it["y"]
        # portfolio region only
        if x < 1400:
            return "pre-portfolio"
        # columns by midpoint X; same-column split by Y for final-reel/bts
        cols = []
        for s in sorted(secs, key=lambda s: s["x"]):
            if cols and abs(cols[-1][0]["x"] - s["x"]) < 100:
                cols[-1].append(s)
            else:
                cols.append([s])
        centers = [sum(s["x"] for s in col) / len(col) for col in cols]
        chosen_col = None
        for i, center in enumerate(centers):
            lo = (centers[i - 1] + center) / 2 if i else center - 500
            hi = (center + centers[i + 1]) / 2 if i + 1 < len(centers) else center + 1000
            if lo <= x < hi:
                chosen_col = cols[i]
                break
        if not chosen_col:
            chosen_col = min(cols, key=lambda col: abs(col[0]["x"] - x))
        if len(chosen_col) == 1:
            return chosen_col[0]["key"]
        # stacked Final Reel / BTS
        csorted = sorted(chosen_col, key=lambda s: s["y"])
        for i, s in enumerate(csorted):
            y0 = s["y"] - 50
            y1 = csorted[i + 1]["y"] - 50 if i + 1 < len(csorted) else 1e9
            if y0 <= y < y1:
                return s["key"]
        return csorted[-1]["key"]

    buckets = defaultdict(list)
    for it in media_pl + video_pl:
        buckets[assign(it, sections)].append(it)

    print("\n=== placement counts ===")
    for k, v in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        print(f"  {k:16s} {len(v)}")

    # map ids to best local files via manifest
    man = json.loads((ROOT / "assets/canva/manifest.json").read_text(encoding="utf-8"))
    if isinstance(man, dict):
        man = [man]
    media_local = {
        m["id"]: m["file"].replace("\\", "/")
        for m in man
        if isinstance(m, dict) and m.get("type") == "media" and m.get("ok")
    }
    # video posters
    vid_local = {}
    for m in re.finditer(
        r'"id":"(VA[A-Za-z0-9_-]+)".{0,3500}?"posterframes":\[\{"A":"(_assets/video/([^"]+))"\}',
        html,
    ):
        vid, fname = m.group(1), m.group(3)
        stem = Path(fname).stem[:12]
        for f in (ROOT / "assets/canva/video").glob("*"):
            if stem in f.name:
                vid_local[vid] = f"assets/canva/video/{f.name}"
                break

    catalog = media_id_files(html)

    result = {"sections": sections_sorted, "buckets": {}}
    for key, items in buckets.items():
        entries = []
        seen_f = set()
        for it in sorted(items, key=lambda z: (z["y"], z["x"])):
            if it["kind"] == "media":
                f = media_local.get(it["id"])
                meta = catalog.get(it["id"], [])
                best = best_file(meta) if meta else None
            else:
                f = vid_local.get(it["id"])
                best = None
            if not f or f in seen_f:
                continue
            seen_f.add(f)
            entries.append(
                {
                    "id": it["id"],
                    "kind": it["kind"],
                    "file": f,
                    "x": round(it["x"], 1),
                    "y": round(it["y"], 1),
                    "w": round(it["w"], 1),
                    "h": round(it["h"], 1),
                    "ar": round(it["h"] / it["w"], 2) if it["w"] else 0,
                    "remote": best["url"] if best else None,
                    "dim": f"{best['w']}x{best['h']}" if best else None,
                }
            )
        result["buckets"][key] = entries
        print(f"\n{key}: {len(entries)} unique files")
        for e in entries[:8]:
            print(f"  {e['kind']:5s} x={e['x']:7.1f} y={e['y']:6.1f} ar={e['ar']} {Path(e['file']).name}")

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
