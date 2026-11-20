#!/usr/bin/env python3
"""Cattura lo screenshot full page di una pagina locale.

Sopprime la toolbar dell'Internet Archive e il banner cookie, cosi' che
l'originale archiviato e la versione ricostruita siano confrontabili.
"""
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FONTS = ("https://fonts.googleapis.com/css2?family=Poppins:"
         "ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;"
         "1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")

SOPPRESSIONE = """
#wm-ipp-base, #wm-ipp-print, #wm-ipp, .wb-autocomplete-suggestions,
.iubenda-cs-container, #iubenda-cs-banner, .iubenda-tp-btn,
.iubenda-cs-overlay { display: none !important; }
html { --wm-toolbar-height: 0px !important; }
body { margin-top: 0 !important; }
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("page", help="file HTML da aprire")
    ap.add_argument("out", help="PNG da scrivere")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900, help="altezza del viewport")
    ap.add_argument("--wait", type=float, default=2.0,
                    help="attesa fissa dopo il caricamento, in secondi")
    ap.add_argument("--hover", help="selettore su cui portare il puntatore")
    ap.add_argument("--fonts", action="store_true",
                    help="inietta Poppins da Google Fonts: serve sugli originali "
                         "archiviati, i cui @font-face puntano su archive.org e non "
                         "risolvono, per confrontarli con la versione nuova")
    args = ap.parse_args(argv)

    url = Path(args.page).resolve().as_uri()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        errori = []
        page.on("pageerror", lambda e: errori.append(str(e)))

        page.goto(url, wait_until="load")
        # networkidle non arriva sempre: gli script Wayback restano appesi.
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        if args.fonts:
            page.add_style_tag(url=FONTS)
        page.add_style_tag(content=SOPPRESSIONE)
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        # Scorre fino in fondo e torna su, per far scattare gli effetti
        # legati allo scroll che altrimenti lascerebbero blocchi invisibili.
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(int(args.wait * 1000))
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        if args.hover:
            page.hover(args.hover)
            page.wait_for_timeout(600)

        page.screenshot(path=args.out, full_page=True)
        browser.close()

    for e in errori:
        print(f"errore di pagina: {e}", file=sys.stderr)
    print(f"scritto {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
