# ry.gd

Short links for QR codes. `https://ry.gd/<code>` forwards to the URL listed in `links.txt`.

## Add or change a link

1. Edit `links.txt` — one line per link: `<code>  <destination URL>`
2. Run `python3 build.py` (rebuilds the redirect pages and `qr/<code>.png` / `.svg`)
3. Commit and push. GitHub Pages is live about a minute later.

Changing a destination doesn't change the QR code, so printed codes keep working. Only retire a code if you're sure nothing printed still points at it.

## How it works

Each code gets a folder (`1/index.html`, `2/index.html`, …) holding a tiny page that forwards the visitor right away. Hosting is GitHub Pages, and the custom domain comes from `CNAME`. Unknown codes show `404.html`.
