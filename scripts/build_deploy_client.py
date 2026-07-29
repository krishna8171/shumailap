"""Build deploy-client/ folder for Netlify Drop (~50MB, no heavy reels)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deploy-client"

SKIP_DIR_NAMES = {
    "reels",
    "shots",
    "candidates",
    "pdf-preview",
    "__pycache__",
    ".git",
    "scripts",
    "deploy-client",
}


def should_skip(rel: Path) -> bool:
    if any(part in SKIP_DIR_NAMES for part in rel.parts):
        return True
    if rel.suffix.lower() in {".pyc", ".py"}:
        return True
    return False


def strip_reel_videos(obj):
    if isinstance(obj, dict):
        v = obj.get("video")
        if isinstance(v, str) and "reels/" in v.replace("\\", "/"):
            obj.pop("video", None)
        for val in obj.values():
            strip_reel_videos(val)
    elif isinstance(obj, list):
        for val in obj:
            strip_reel_videos(val)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for name in ("index.html", "styles.css", "script.js"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, OUT / name)

    for d in ("admin", "js", "data", "assets"):
        src = ROOT / d
        if not src.exists():
            continue
        for p in src.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT)
            if should_skip(rel):
                continue
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)

    for name in ("data/gallery.json", "data/site.json"):
        fp = OUT / name
        if not fp.exists():
            continue
        data = json.loads(fp.read_text(encoding="utf-8"))
        strip_reel_videos(data)
        fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # small guide inside package
    (OUT / "HOW-TO-OPEN.txt").write_text(
        "SHUMAIL PORTFOLIO — deploy package for graphics / client team\n"
        "============================================================\n"
        "\n"
        "1) Upload this ENTIRE folder to https://app.netlify.com/drop\n"
        "2) Open the HTTPS link Netlify gives you\n"
        "3) Admin CMS: /admin/   user=admin   pass=shumail2026\n"
        "\n"
        "Local preview (on this PC):\n"
        "  python -m http.server 8765\n"
        "  open http://127.0.0.1:8765/\n"
        "\n"
        "Hero (full-width, black bg, no over-zoom — object-fit contain):\n"
        "  assets/hero/best-01.jpg … best-08.jpg  stills\n"
        "  assets/hero/live-01.mp4 … live-04.mp4  short work clips (autoplay muted)\n"
        "  Replace those files to change the top live showcase.\n"
        "\n"
        "Company logos: managed in Admin → Industries (logos only).\n"
        "Creatives grid: Admin → Creatives / data/gallery.json\n"
        "\n"
        "Note: full canva/reels library is stripped for Netlify size;\n"
        "hero live-*.mp4 clips stay in assets/hero/. Posters still show in grid.\n",
        encoding="utf-8",
    )

    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    files = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"OK: {OUT}")
    print(f"Size: {total / 1024 / 1024:.1f} MB  Files: {files}")


if __name__ == "__main__":
    main()
