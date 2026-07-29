"""
Export the full portfolio site as a multi-page PDF (complete page print).
Uses headless Edge/Chrome print-to-pdf against the local server.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Shumail-Complete-Website.pdf"
URL = "http://127.0.0.1:8765/index.html?pdf=1"


def find_browser() -> str | None:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    for name in ("chrome", "msedge", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return None


def wait_server(url: str, tries: int = 20) -> bool:
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def main() -> int:
    browser = find_browser()
    if not browser:
        print("ERROR: Chrome/Edge not found")
        return 1

    if not wait_server("http://127.0.0.1:8765/"):
        print("ERROR: local server not responding on :8765")
        print("Start with: python -m http.server 8765")
        return 1

    # Ensure print styles + reveal-visible via query param handled in CSS if needed
    out = OUT
    if out.exists():
        out.unlink()

    # Headless print — full document, no header/footer
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",
        "--no-pdf-header-footer",
        f"--print-to-pdf={out}",
        URL,
    ]
    print("Running:", " ".join(cmd[:4]), "…")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        print("browser stderr:", (proc.stderr or "")[-800:])
        print("browser stdout:", (proc.stdout or "")[-400:])

    if not out.exists() or out.stat().st_size < 5000:
        # Fallback path: some Edge builds write relative to cwd
        alt = Path.cwd() / "Shumail-Complete-Website.pdf"
        if alt.exists() and alt != out:
            alt.replace(out)

    if not out.exists() or out.stat().st_size < 5000:
        print("ERROR: PDF not created or too small")
        return 1

    kb = out.stat().st_size / 1024
    print(f"OK: {out} ({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
