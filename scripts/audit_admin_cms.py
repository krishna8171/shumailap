"""Audit: every site text/media must be editable in admin."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")
schema = (ROOT / "js/cms-schema.js").read_text(encoding="utf-8")
admin_js = (ROOT / "admin/admin.js").read_text(encoding="utf-8")
admin_html = (ROOT / "admin/index.html").read_text(encoding="utf-8")
content_js = (ROOT / "js/content.js").read_text(encoding="utf-8")
site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
gal = json.loads((ROOT / "data/gallery.json").read_text(encoding="utf-8"))

cms = sorted(set(re.findall(r'data-cms="([^"]+)"', html)))
cms_media = sorted(set(re.findall(r'data-cms-media="([^"]+)"', html)))
schema_paths = sorted(set(re.findall(r'path:\s*"([^"]+)"', schema)))

print("SITE data-cms:", len(cms))
print("SITE data-cms-media:", cms_media)
print("SCHEMA paths:", len(schema_paths))

missing_schema = sorted(set(cms) - set(schema_paths))
print("\nOn site but NOT in CMS schema:", missing_schema or "OK none")

# Dynamic content managed outside schema
print("\nDynamic (separate admin panels):")
print("  companies:", len(gal.get("companies") or site.get("companies") or []))
print("  creatives:", len(gal.get("creatives") or site.get("creatives") or []))
print("  services:", len(site.get("services") or []))
print("  process:", len(site.get("process") or []))
print("  stats:", len(site.get("stats") or []))

checks = {
    "addCompany button": "addCompany" in admin_html,
    "addCreative button": "addCreative" in admin_html,
    "bulk multi image upload": "bulkCrImages" in admin_js and "multiple" in admin_js,
    "bulk multi video upload": "bulkCrVideos" in admin_js,
    "company work multi add": "data-co-work-img" in admin_js,
    "company work multi video": "data-co-work-vid" in admin_js,
    "reload full content": "reloadFullBtn" in admin_html,
    "siteRootPrefix fix": "siteRootPrefix" in content_js,
    "mergeSiteData": "mergeSiteData" in content_js,
    "renderAllEdit": "renderAllEdit" in admin_js,
    "saveSiteData": "saveSiteData" in content_js,
    "isPlayableVideo / reels": "isPlayableVideo" in content_js or "reel-video" in content_js,
}
print("\nAdmin capability checks:")
for k, v in checks.items():
    print(("  OK  " if v else "  FAIL") , k)

# Service cards hardcoded in HTML?
svc_h3 = len(re.findall(r'class="service-card"', html))
print(f"\nService cards in HTML: {svc_h3} (edited via Services panel / applySiteToDOM)")
print(f"Process steps in HTML: {len(re.findall(r'class=\"step\"', html))}")

# Badge 3 Available for hire - hardcoded?
if "Available for hire" in html and "badge-3" in html:
    if "badge3" not in schema and "hero.badge3" not in schema_paths:
        print("GAP: badge-3 'Available for hire' not in CMS schema")

# Achievements applied?
if "achievements" in content_js:
    print("OK: achievements applied in content.js")
else:
    print("GAP: achievements not applied")

# company work render
if "company-block" in content_js or "company-work" in content_js:
    print("OK: company work blocks rendered")
else:
    print("GAP: company work render missing")
