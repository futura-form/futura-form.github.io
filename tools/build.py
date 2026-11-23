#!/usr/bin/env python3
"""Ricostruisce l'intero sito dai salvataggi Internet Archive dentro build/.

build/ contiene esattamente i file da pubblicare e nient'altro: niente
strumenti, niente riferimenti, niente sorgenti. Il sito non si modifica a
mano, si rigenera.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SORGENTE = ROOT / "Sito-FuturaForm"
FOGLI_SORGENTE = SORGENTE / "Home-Page_files"
USCITA = ROOT / "build"

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

    USCITA.mkdir(parents=True, exist_ok=True)
    # impedisce a Jekyll di intervenire sui file pubblicati
    (USCITA / ".nojekyll").write_text("", encoding="utf-8")

    subprocess.run(
        [sys.executable, str(ROOT / "tools/sync_images.py"),
         "--destinazione", str(USCITA / "assets/img")],
        check=True)

    subprocess.run(
        [sys.executable, str(ROOT / "tools/sync_scripts.py"),
         "--destinazione", str(USCITA / "assets/js")],
        check=True)

    subprocess.run(
        [sys.executable, str(ROOT / "tools/bundle_css.py"),
         "--cartella", str(FOGLI_SORGENTE), "--out", str(USCITA / "assets/css/site.css"),
         *FOGLI],
        check=True)

    for sorgente, slug in PAGINE:
        subprocess.run(
            [sys.executable, str(ROOT / "tools/clean_page.py"),
             str(SORGENTE / sorgente), str(USCITA / f"{slug}.html"),
             "--slug", slug, "--bundle"],
            check=True, cwd=ROOT)
    # il CSS della card e' scritto a mano, non generato: si copia
    shutil.copy2(ROOT / "tools/card-contatti.css",
                 USCITA / "assets/css/card-contatti.css")
    print(f"ricostruite {len(PAGINE)} pagine in {USCITA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
