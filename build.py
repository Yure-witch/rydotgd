#!/usr/bin/env python3
"""Build ry.gd redirect pages (and QR codes) from links.txt.

For each line "<code> <url>" in links.txt this writes <code>/index.html,
a page that immediately forwards the visitor to <url>. Static hosts such as
GitHub Pages serve https://ry.gd/<code> from that file.

If the `qrcode` package is installed, it also writes qr/<code>.png and
qr/<code>.svg pointing at https://ry.gd/<code>.
"""

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOMAIN = "ry.gd"
MARKER = "<!-- ry.gd redirect -->"
CODE_RE = re.compile(r"^[A-Za-z0-9_-]+$")
RESERVED = {"qr", ".git", ".github"}

REDIRECT_PAGE = """<!doctype html>
{marker}
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Redirecting…</title>
<meta http-equiv="refresh" content="0; url={url_attr}">
<link rel="canonical" href="{url_attr}">
<script>location.replace({url_js});</script>
</head>
<body style="font-family: system-ui, sans-serif; padding: 2rem;">
<p>Redirecting to <a href="{url_attr}">{url_text}</a>…</p>
</body>
</html>
"""


def read_links():
    links = {}
    for lineno, raw in enumerate((ROOT / "links.txt").read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):  # (URLs may contain "#", so only whole-line comments)
            continue
        parts = line.split()
        if len(parts) != 2:
            raise SystemExit(f"links.txt line {lineno}: expected '<code> <url>', got: {raw!r}")
        code, url = parts
        if not CODE_RE.match(code) or code.lower() in RESERVED:
            raise SystemExit(f"links.txt line {lineno}: invalid code {code!r}")
        if not url.startswith(("https://", "http://")):
            raise SystemExit(f"links.txt line {lineno}: URL must start with https:// or http://")
        if code in links:
            raise SystemExit(f"links.txt line {lineno}: duplicate code {code!r}")
        links[code] = url
    return links


def write_redirects(links):
    for code, url in links.items():
        page = REDIRECT_PAGE.format(
            marker=MARKER,
            url_attr=html.escape(url, quote=True),
            url_text=html.escape(url),
            url_js=json.dumps(url).replace("</", "<\\/"),
        )
        out = ROOT / code / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)

    # Remove folders for codes that were deleted from links.txt.
    for d in ROOT.iterdir():
        idx = d / "index.html"
        if d.is_dir() and d.name not in links and idx.exists() and MARKER in idx.read_text():
            shutil.rmtree(d)
            print(f"removed  /{d.name}")


def write_qr_codes(links):
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        print("qrcode package not installed; skipping QR images (pip install qrcode pillow)")
        return
    qr_dir = ROOT / "qr"
    qr_dir.mkdir(exist_ok=True)
    for code in links:
        short = f"https://{DOMAIN}/{code}"
        qrcode.make(short, image_factory=qrcode.image.svg.SvgPathImage).save(qr_dir / f"{code}.svg")
        try:
            qrcode.make(short, box_size=20, border=4).save(qr_dir / f"{code}.png")
        except Exception as e:  # Pillow missing
            print(f"PNG for {code} skipped ({e})")
    for f in qr_dir.iterdir():
        if f.suffix in {".png", ".svg"} and f.stem not in links:
            f.unlink()


def main():
    links = read_links()
    write_redirects(links)
    write_qr_codes(links)
    for code, url in links.items():
        print(f"{DOMAIN}/{code}  ->  {url}")


if __name__ == "__main__":
    main()
