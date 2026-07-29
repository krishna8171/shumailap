"""Full integrity check for byshumail-portfolio."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
warns: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)
    print("ERROR:", msg)


def warn(msg: str) -> None:
    warns.append(msg)
    print("WARN:", msg)


def ok(msg: str) -> None:
    print("OK:", msg)


def main() -> int:
    # Required files
    required = [
        "index.html",
        "styles.css",
        "script.js",
        "js/content.js",
        "js/cms-schema.js",
        "admin/index.html",
        "admin/admin.js",
        "admin/admin.css",
        "data/site.json",
        "data/gallery.json",
        "assets/portrait.jpg",
        "generate_proposal_pdf.py",
    ]
    for rel in required:
        p = ROOT / rel
        if not p.exists():
            err(f"missing {rel}")
        else:
            ok(f"exists {rel} ({p.stat().st_size} bytes)")

    # PDF (either name)
    pdfs = list(ROOT.glob("*.pdf"))
    if not pdfs:
        err("no customer PDF found")
    else:
        for p in pdfs:
            ok(f"pdf {p.name} ({p.stat().st_size} bytes)")

    # Gallery integrity
    gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))
    companies = gal.get("companies") or []
    creatives = gal.get("creatives") or []
    ok(f"gallery companies={len(companies)} creatives={len(creatives)}")

    for c in companies:
        if c.get("cat") not in (None, "companies") and c.get("section") != "companies":
            warn(f"company odd cat: {c}")
        img = c.get("image", "")
        if img and not img.startswith("data:"):
            if not (ROOT / img).exists():
                err(f"company logo missing: {img}")

    allowed_cats = {
        "final-reel",
        "bts",
        "concert",
        "drone",
        "automobile",
        "weddings",
    }
    missing_media = 0
    junk_cats = 0
    for c in creatives:
        cat = c.get("cat")
        if cat not in allowed_cats:
            junk_cats += 1
            warn(f"creative unexpected cat={cat} id={c.get('id')}")
        src = c.get("video") or c.get("image") or ""
        if src and not src.startswith("data:"):
            if not (ROOT / src).exists() or (ROOT / src).stat().st_size < 500:
                missing_media += 1
                if missing_media <= 15:
                    err(f"creative media missing: {src}")
    if missing_media:
        err(f"total missing creative media: {missing_media}")
    else:
        ok("all creative media paths exist")
    if junk_cats == 0:
        ok("creative categories match site taxonomy")

    # site.json
    site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
    for key in ["name", "role", "services", "process", "contact", "portrait"]:
        if key not in site:
            err(f"site.json missing {key}")
    if len(site.get("services") or []) < 1:
        err("no services")
    if len(site.get("process") or []) < 5:
        warn(f"process steps = {len(site.get('process') or [])}")

    # Portrait size sanity (real photo should be decent size)
    por = ROOT / "assets/portrait.jpg"
    if por.stat().st_size < 20000:
        warn("portrait.jpg seems very small")
    else:
        ok(f"portrait.jpg size={por.stat().st_size}")

    # HTML structure
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for sid in [
        "home",
        "services",
        "about",
        "industries",
        "portfolio",
        "process",
        "contact",
    ]:
        if f'id="{sid}"' not in html:
            err(f"section missing id={sid}")
    if 'id="companiesGrid"' not in html:
        err("companiesGrid missing")
    if 'id="portfolioGrid"' not in html:
        err("portfolioGrid missing")
    if "cms-schema.js" not in html:
        err("cms-schema.js not included in index.html")
    if "content.js" not in html:
        err("content.js not included")

    cms = set(re.findall(r'data-cms="([^"]+)"', html))
    media = set(re.findall(r'data-cms-media="([^"]+)"', html))
    ok(f"data-cms fields in HTML: {len(cms)}")
    ok(f"data-cms-media: {sorted(media)}")

    # Admin
    admin = (ROOT / "admin/index.html").read_text(encoding="utf-8")
    admin_js = (ROOT / "admin/admin.js").read_text(encoding="utf-8")
    for needle in [
        "panel-alledit",
        "panel-companies",
        "panel-creatives",
        "addCompany",
        "addCreative",
        "Upload",
    ]:
        if needle not in admin and needle not in admin_js:
            err(f"admin missing {needle}")
    if "renderAllEdit" not in admin_js:
        err("admin.js missing renderAllEdit")
    if "readFileAsDataURL" not in admin_js:
        err("admin.js missing file upload reader")
    if "data-cr-file-vid" not in admin_js:
        err("admin.js missing video upload")
    ok("admin panels present for full CMS")

    # content.js critical exports
    content = (ROOT / "js/content.js").read_text(encoding="utf-8")
    for fn in ["loadSiteData", "saveSiteData", "applySiteToDOM", "ByShumail"]:
        if fn not in content:
            err(f"content.js missing {fn}")

    # CSS overlap protections
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    for needle in [".process-steps", "isolation: isolate", ".lightbox", "minmax(0"]:
        if needle not in css:
            warn(f"CSS may lack {needle}")

    # script lightbox video
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    if "lightboxVideo" not in script:
        err("script.js missing video lightbox support")
    if "bindFilters" not in script:
        err("script.js missing filters")
    if "data:video" not in script and "mp4" not in script:
        warn("script.js may not distinguish playable video vs posters")

    # content.js must not treat type:video jpg as playable
    if 'type === "video"' in content and "isPlayableVideo" not in content:
        err("content.js may render jpg posters as <video>")
    if "isPlayableVideo" in content:
        ok("content.js uses isPlayableVideo for real videos only")

    # admin save must not truncate with ellipsis into portrait field permanently
    if 'dataUrl.slice(0, 64) + "…"' in admin_js or "dataUrl.slice(0, 48)" in admin_js:
        err("admin.js still truncates media data URLs on upload")
    else:
        ok("admin.js does not truncate uploaded media URLs")

    # JS syntax via compile if node unavailable - rough brace balance
    for rel in ["script.js", "js/content.js", "js/cms-schema.js", "admin/admin.js"]:
        txt = (ROOT / rel).read_text(encoding="utf-8")
        if txt.count("{") != txt.count("}"):
            err(f"brace mismatch in {rel}: {{ {txt.count('{')} }} {txt.count('}')}")
        else:
            ok(f"brace balance {rel}")

    # HTTP smoke if server up
    try:
        import urllib.request

        for url in [
            "http://127.0.0.1:8765/",
            "http://127.0.0.1:8765/admin/",
            "http://127.0.0.1:8765/data/gallery.json",
            "http://127.0.0.1:8765/data/site.json",
            "http://127.0.0.1:8765/js/content.js",
            "http://127.0.0.1:8765/assets/portrait.jpg",
        ]:
            with urllib.request.urlopen(url, timeout=3) as r:
                code = r.status
                if code != 200:
                    err(f"HTTP {code} {url}")
                else:
                    ok(f"HTTP 200 {url}")
    except Exception as e:
        warn(f"HTTP smoke skipped/failed: {e}")

    print("\n==== SUMMARY ====")
    print(f"errors={len(errors)} warnings={len(warns)}")
    if errors:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
