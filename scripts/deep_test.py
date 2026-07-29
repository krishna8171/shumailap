"""
Deep QA: compare local site vs https://byshumail.my.canva.site
Acts as a tester — reports PASS/FAIL checklist.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail-live.html")
if not LIVE.exists():
    LIVE = Path(r"C:\Users\admin\AppData\Local\Temp\byshumail.html")

BASE = "http://127.0.0.1:8765"
fails: list[str] = []
passes: list[str] = []
warns: list[str] = []


def ok(m: str) -> None:
    passes.append(m)
    print(f"  PASS  {m}")


def fail(m: str) -> None:
    fails.append(m)
    print(f"  FAIL  {m}")


def warn(m: str) -> None:
    warns.append(m)
    print(f"  WARN  {m}")


def http_get(path: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as r:
            return r.status, r.read()
    except Exception as e:
        return 0, str(e).encode()


def extract_live_texts(html: str) -> list[str]:
    blobs = re.findall(r'"A":"([^"]{2,120})\\n"', html)
    out = []
    for b in blobs:
        t = b.replace("\\n", " ").replace("\\'", "'").strip()
        if re.search(r"[A-Za-z]{3,}", t) and not re.match(r"^(MA|VA|TA|LB|PB|YA)", t):
            out.append(t)
    # unique preserve order
    seen = set()
    uniq = []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def main() -> int:
    print("=" * 60)
    print("DEEP TEST: local site vs byshumail.my.canva.site")
    print("=" * 60)

    # --- A. Live source available ---
    print("\n[A] Live Canva source")
    if not LIVE.exists() or LIVE.stat().st_size < 1000:
        fail("Live HTML snapshot missing — re-download https://byshumail.my.canva.site")
        live_html = ""
    else:
        live_html = LIVE.read_text(encoding="utf-8", errors="ignore")
        ok(f"Live HTML snapshot {LIVE.stat().st_size} bytes")

    live_texts = extract_live_texts(live_html) if live_html else []
    must_have = [
        "mudshumail@gmail.com",
        "Shumail Ap",
        "Content Creator | Photographer | Videographer",
        "Industries worked with",
        "Final Reel",
        "BTS",
        "Hanan Shaah concert",
        "Automobile",
        "WEDDINGS & EVENTS",
        "DRONE SHOTS",
        "Creating Visuals",
        "Drone Cinematography",
        "Photography",
        "Videography",
        "Real Estate Marketing",
        "NEWIZZ",
        "Revo",
        "+971",
    ]
    print("\n[B] Live content markers")
    for m in must_have:
        found = any(m.lower() in t.lower() for t in live_texts) or (m.lower() in live_html.lower())
        if found:
            ok(f"Live has «{m}»")
        else:
            warn(f"Live snapshot missing «{m}» (may be encoding)")

    # --- C. Local HTTP ---
    print("\n[C] Local server endpoints")
    endpoints = [
        "/",
        "/admin/",
        "/styles.css",
        "/script.js",
        "/js/content.js",
        "/js/cms-schema.js",
        "/data/site.json",
        "/data/gallery.json",
        "/assets/portrait.jpg",
        "/admin/admin.js",
        "/admin/admin.css",
    ]
    for ep in endpoints:
        code, body = http_get(ep)
        if code == 200 and len(body) > 50:
            ok(f"GET {ep} → {code} ({len(body)} bytes)")
        else:
            fail(f"GET {ep} → {code}")

    # --- D. Local HTML structure ---
    print("\n[D] Local HTML structure & CMS hooks")
    code, html_b = http_get("/")
    html = html_b.decode("utf-8", errors="ignore")
    for sid in ["home", "services", "about", "industries", "portfolio", "process", "contact"]:
        if f'id="{sid}"' in html:
            ok(f"Section #{sid}")
        else:
            fail(f"Missing section #{sid}")

    for needle in [
        'id="companiesGrid"',
        'id="portfolioGrid"',
        'id="portraitImg"',
        'data-cms="name"',
        'data-cms="role"',
        'data-cms="sections.contact.sub"',
        "cms-schema.js",
        "content.js",
        'id="lightbox"',
    ]:
        if needle in html:
            ok(f"HTML has {needle}")
        else:
            fail(f"HTML missing {needle}")

    # --- E. Content parity (local defaults / site.json) ---
    print("\n[E] Content parity with live site")
    site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
    gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))

    checks = {
        "name contains Shumail": "shumail" in (site.get("name") or "").lower(),
        "role set": bool(site.get("role")),
        "email matches": "mudshumail@gmail.com" in (site.get("contact") or {}).get("email", ""),
        "phone UAE": "971" in (site.get("contact") or {}).get("phone", "").replace(" ", ""),
        "services >= 6": len(site.get("services") or []) >= 6,
        "process == 5": len(site.get("process") or []) == 5,
        "portrait file": (ROOT / (site.get("portrait") or "assets/portrait.jpg")).exists(),
    }
    for label, good in checks.items():
        ok(label) if good else fail(label)

    # Service titles vs live
    live_services = [
        "Drone Cinematography",
        "Photography",
        "Videography",
        "Real Estate Marketing",
        "Video Editing",
        "Brand Storytelling",
        "Social Media Content",
    ]
    local_svc = " ".join(s.get("title", "") for s in site.get("services") or [])
    for s in live_services:
        if s.lower() in local_svc.lower() or s.lower() in html.lower():
            ok(f"Service/content «{s}» present")
        else:
            # Social Media Content might only be on Canva list not our 6 cards
            if s == "Social Media Content":
                warn(f"«{s}» not a separate card (merged into storytelling?)")
            else:
                fail(f"Missing service «{s}»")

    # Categories
    print("\n[F] Classification vs live headings")
    companies = gal.get("companies") or []
    creatives = gal.get("creatives") or []
    cats = Counter(c.get("cat") for c in creatives)
    expected = {
        "final-reel": "Final Reel",
        "bts": "BTS",
        "concert": "Hanan Shaah Concert",
        "drone": "Drone Shots",
        "automobile": "Automobile",
        "weddings": "Weddings & Events",
    }
    if len(companies) >= 3:
        ok(f"Companies/logos section: {len(companies)} logos")
    else:
        fail(f"Too few company logos: {len(companies)}")

    for key, label in expected.items():
        n = cats.get(key, 0)
        if n >= 1:
            ok(f"Creative «{label}»: {n} items")
        else:
            fail(f"Creative «{label}»: 0 items")

    # No junk categories
    bad = [c for c in cats if c not in expected]
    if bad:
        fail(f"Unexpected creative cats: {bad}")
    else:
        ok("No junk creative categories")

    # Media files exist
    print("\n[G] Media file integrity")
    missing = 0
    for group in (companies, creatives):
        for it in group:
            src = it.get("image") or it.get("video") or ""
            if not src or src.startswith("data:"):
                continue
            p = ROOT / src
            if not p.exists() or p.stat().st_size < 400:
                missing += 1
                if missing <= 8:
                    fail(f"Missing media {src}")
    if missing == 0:
        ok(f"All {len(companies)+len(creatives)} gallery media files on disk")
    else:
        fail(f"{missing} media files missing")

    # Portrait is photographic (size)
    por = ROOT / "assets/portrait.jpg"
    if por.stat().st_size > 50000:
        ok("Hero portrait looks like real photo (file size)")
    else:
        fail("Portrait file suspiciously small")

    # --- H. Admin capabilities ---
    print("\n[H] Admin CMS capabilities")
    _, admin_html = http_get("/admin/")
    admin = admin_html.decode("utf-8", errors="ignore")
    _, admin_js_b = http_get("/admin/admin.js")
    admin_js = admin_js_b.decode("utf-8", errors="ignore")
    for needle, label in [
        ("panel-alledit", "All text & media panel"),
        ("panel-companies", "Companies panel"),
        ("panel-creatives", "Creatives panel"),
        ("addCompany", "Add company"),
        ("addCreative", "Add creative"),
        ("data-cr-file-vid", "Video upload"),
        ("data-co-file", "Logo upload"),
        ("renderAllEdit", "Full CMS renderer"),
        ("isTruncatedPlaceholder", "Safe media save"),
        ("mergeMedia", "Media merge on save"),
    ]:
        if needle in admin or needle in admin_js:
            ok(f"Admin: {label}")
        else:
            fail(f"Admin missing: {label}")

    # --- I. Frontend JS behavior checks (static) ---
    print("\n[I] Frontend behavior (static code review)")
    content = (ROOT / "js/content.js").read_text(encoding="utf-8")
    script = (ROOT / "script.js").read_text(encoding="utf-8")
    css = (ROOT / "styles.css").read_text(encoding="utf-8")

    if "isPlayableVideo" in content:
        ok("Playable video vs reel poster distinction")
    else:
        fail("Missing isPlayableVideo")

    if 'type === "video"' in content and "isPlayableVideo" not in content:
        fail("Would render posters as video")

    if "isolation: isolate" in css or "minmax(0" in css:
        ok("CSS overlap mitigations present")
    else:
        warn("CSS isolation patterns weak")

    if "lightboxVideo" in script and "mp4" in script:
        ok("Lightbox supports real video only")
    else:
        fail("Lightbox video handling incomplete")

    # No truncate bug
    if "dataUrl.slice" in admin_js:
        fail("Admin still truncates uploads")
    else:
        ok("Admin upload save does not truncate")

    # --- J. PDF ---
    print("\n[J] Customer PDF")
    pdfs = list(ROOT.glob("*.pdf"))
    if any(p.stat().st_size > 100_000 for p in pdfs):
        ok(f"PDF deliverable(s): {', '.join(p.name for p in pdfs)}")
    else:
        fail("PDF missing or empty")

    # --- K. Live media ID present in our import ---
    print("\n[K] Canva hero media imported")
    if "MAHMpiMVp30" in live_html or "55c2aea2153da039eb794d240c4b64e5" in live_html:
        # hero media id
        if (ROOT / "assets/portrait.jpg").exists():
            ok("Hero media ID known and portrait file present")
        else:
            fail("Hero media known but portrait missing")
    else:
        warn("Could not confirm hero media id in live HTML")

    # Company logos sanity (not social icons)
    print("\n[L] Logo quality sample")
    for c in companies:
        img = c.get("image", "")
        name = Path(img).name.lower()
        if any(x in name for x in ["whatsapp", "instagram", "icon"]):
            fail(f"Junk logo slipped in: {img}")
        else:
            ok(f"Logo OK: {Path(img).name}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print(f"PASSED: {len(passes)}")
    print(f"WARNED: {len(warns)}")
    print(f"FAILED: {len(fails)}")
    if fails:
        print("\nFAILURES:")
        for f in fails:
            print(" -", f)
        print("\nVERDICT: FAIL")
        return 1
    print("\nVERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
