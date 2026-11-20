#!/usr/bin/env python3
"""Elenca errori di console e richieste fallite di una pagina locale."""
import argparse, sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def controlla(path, width=1440):
    errori, falliti, console = [], [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 900})
        pg.on("pageerror", lambda e: errori.append(str(e)))
        pg.on("console", lambda m: console.append(m.text) if m.type == "error" else None)
        pg.on("requestfailed", lambda r: falliti.append((r.url, r.failure)))
        pg.on("response", lambda r: falliti.append((r.url, f"HTTP {r.status}")) if r.status >= 400 else None)
        url = path if path.startswith("http") else Path(path).resolve().as_uri()
        pg.goto(url, wait_until="load")
        try: pg.wait_for_load_state("networkidle", timeout=8000)
        except Exception: pass
        pg.wait_for_timeout(2500)
        b.close()
    return errori, console, falliti


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pages", nargs="+")
    ap.add_argument("--width", type=int, default=1440)
    args = ap.parse_args(argv)
    sporco = False
    for pagina in args.pages:
        errori, console, falliti = controlla(pagina, args.width)
        print(f"--- {pagina}")
        for e in errori: print(f"   errore JS: {e}"); sporco = True
        for c in console: print(f"   console: {c[:160]}"); sporco = True
        for u, f in falliti: print(f"   fallita: {f} {u[:120]}"); sporco = True
        if not (errori or console or falliti): print("   pulita")
    return 1 if sporco else 0


if __name__ == "__main__":
    sys.exit(main())
