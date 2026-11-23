#!/usr/bin/env python3
"""Copia le immagini dai salvataggi in assets/img, normalizzando i nomi.

Le cinque cartelle _files contengono le stesse immagini ripetute. Qui si
deduplicano e si rinominano per il web: tutto minuscolo, niente spazi,
niente percento. GitHub Pages distingue le maiuscole, macOS no, e un
nome con una maiuscola passerebbe ogni prova in locale per poi dare 404
una volta pubblicato.

Produce anche tools/asset-map.json, la mappa che clean_page.py usa per
riscrivere i src delle pagine.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
ESTENSIONI = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}


def normalizza(nome):
    stem, _, ext = nome.rpartition(".")
    stem = unquote(stem).replace("%20", " ")
    stem = re.sub(r"[\s_]+", "-", stem.strip().lower())
    stem = re.sub(r"[^a-z0-9.\-]", "-", stem)
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    return f"{stem}.{ext.lower()}"


def sincronizza(sorgente, destinazione):
    """Copia, deduplica e rinomina. Torna la mappa nome originale -> percorso."""
    destinazione.mkdir(parents=True, exist_ok=True)
    mappa, impronte = {}, {}

    for cartella in sorted(p for p in Path(sorgente).iterdir() if p.is_dir()):
        for f in sorted(cartella.iterdir()):
            if not f.is_file() or f.suffix.lower() not in ESTENSIONI:
                continue
            nuovo = normalizza(f.name)
            impronta = hashlib.sha256(f.read_bytes()).hexdigest()
            if nuovo in impronte and impronte[nuovo] != impronta:
                raise ValueError(
                    f"due file diversi finirebbero su {nuovo}: "
                    f"{f} contro una copia gia' vista")
            if nuovo not in impronte:
                shutil.copy2(f, destinazione / nuovo)
                impronte[nuovo] = impronta
            mappa[f.name] = f"assets/img/{nuovo}"

    # un'immagine tolta dai salvataggi non deve restare appesa in assets
    for f in sorted(destinazione.iterdir()):
        if f.is_file() and f.name not in impronte and f.name != "favicon.png":
            f.unlink()

    return dict(sorted(mappa.items()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sorgente", default=str(ROOT / "Sito-FuturaForm"))
    ap.add_argument("--destinazione", default=str(ROOT / "build/assets/img"))
    ap.add_argument("--mappa", default=str(ROOT / "tools/asset-map.json"))
    ap.add_argument("--favicon", default="Logo-quadrato.png",
                    help="file nella radice dei salvataggi da usare come favicon")
    args = ap.parse_args(argv)

    sorgente = Path(args.sorgente)
    destinazione = Path(args.destinazione)
    mappa = sincronizza(sorgente, destinazione)

    favicon = sorgente / args.favicon
    if favicon.is_file():
        shutil.copy2(favicon, destinazione / "favicon.png")
    elif not (destinazione / "favicon.png").exists():
        print(f"attenzione: manca {favicon}, nessuna favicon", file=sys.stderr)

    Path(args.mappa).write_text(
        json.dumps(mappa, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(set(mappa.values()))} immagini in {destinazione}, "
          f"{len(mappa)} nomi mappati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
