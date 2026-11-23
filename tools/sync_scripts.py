#!/usr/bin/env python3
"""Copia in build/assets/js gli script che le pagine usano davvero.

La lista di cosa non passa e' quella di clean_page.py, che toglie i tag
corrispondenti dalle pagine: tenere le due liste separate farebbe
divergere il markup dai file sul disco.
"""
import argparse
import shutil
import sys
from pathlib import Path

from clean_page import JS_ESCLUSI

ROOT = Path(__file__).resolve().parent.parent


def sincronizza(sorgente, destinazione):
    """Copia gli script non esclusi togliendo il suffisso .download."""
    destinazione = Path(destinazione)
    destinazione.mkdir(parents=True, exist_ok=True)
    copiati = []
    for f in sorted(Path(sorgente).iterdir()):
        if not f.is_file():
            continue
        nome = f.name[:-len(".download")] if f.name.endswith(".download") else f.name
        if not nome.endswith(".js") or nome in JS_ESCLUSI:
            continue
        shutil.copy2(f, destinazione / nome)
        copiati.append(nome)

    for f in sorted(destinazione.iterdir()):
        if f.is_file() and f.name not in copiati:
            f.unlink()

    return copiati


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sorgente", default=str(ROOT / "Sito-FuturaForm/Home-Page_files"))
    ap.add_argument("--destinazione", default=str(ROOT / "build/assets/js"))
    args = ap.parse_args(argv)
    copiati = sincronizza(args.sorgente, args.destinazione)
    print(f"{len(copiati)} script in {args.destinazione}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
