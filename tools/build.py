#!/usr/bin/env python3
"""Ricostruisce l'intero sito dai salvataggi Internet Archive.

Tutto cio' che sta in assets/ e nelle cinque pagine HTML e' prodotto da
qui: il sito non si modifica a mano, si rigenera.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SORGENTE = ROOT / "Sito-FuturaForm"
FOGLI_SORGENTE = SORGENTE / "Home-Page_files"

# nell'ordine originale: la cascata dipende da questo
FOGLI = [
    "bootstrap.min.css", "animate.min.css", "sppagebuilder.css",
    "spsimpleportfolio.css", "bootstrap(1).min.css", "custom.css",
    "template.css", "default.css", "template.min.css", "front.min.css",
]

PAGINE = [
    ("Home-Page.html", "index"),
    ("Chi siamo.html", "chi-siamo"),
    ("I nostri-servizi.html", "servizi"),
    ("I nostri lavori.html", "lavori"),
    ("Contatti.html", "contatti"),
]


def main():
    if not SORGENTE.is_dir():
        print(f"manca {SORGENTE}: servono i salvataggi originali", file=sys.stderr)
        return 1

    subprocess.run(
        [sys.executable, str(ROOT / "tools/bundle_css.py"),
         "--cartella", str(FOGLI_SORGENTE), "--out", str(ROOT / "assets/css/site.css"),
         *FOGLI],
        check=True)

    for sorgente, slug in PAGINE:
        subprocess.run(
            [sys.executable, str(ROOT / "tools/clean_page.py"),
             str(SORGENTE / sorgente), str(ROOT / f"{slug}.html"),
             "--slug", slug, "--bundle"],
            check=True, cwd=ROOT)
    print(f"ricostruite {len(PAGINE)} pagine")
    return 0


if __name__ == "__main__":
    sys.exit(main())
