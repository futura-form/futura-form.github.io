#!/usr/bin/env python3
"""Concatena i fogli di stile superstiti in un bundle unico.

L'ordine e' quello originale: la cascata dipende da quello. Le url che
puntavano ad archive.org vengono neutralizzate — i file non esistono
piu' e lasciarle significa un 404 a ogni caricamento.
"""
import argparse
import re
import sys
from pathlib import Path

COMMENTI_WB = [
    re.compile(r"/\*\s*FILE ARCHIVED ON.*?\*/", re.S),
    re.compile(r"/\*\s*playback timings \(ms\):.*?\*/", re.S),
]
URL_ARCHIVIATA = re.compile(
    r"url\(\s*['\"]?(?:https?://web\.archive\.org)?/web/\d+[a-z_]*/[^)'\"]*['\"]?\s*\)",
    re.I)


def ripulisci(testo):
    for c in COMMENTI_WB:
        testo = c.sub("", testo)
    # una url che non puo' risolvere vale quanto nessuna url
    testo = URL_ARCHIVIATA.sub("url(about:blank)", testo)
    return testo.strip()


def concatena(cartella, nomi):
    pezzi = []
    for n in nomi:
        testo = ripulisci(Path(cartella, n).read_text(encoding="utf-8", errors="replace"))
        pezzi.append(f"/* ===== {n} ===== */\n{testo}\n")
    return "\n".join(pezzi)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cartella", default="assets/css")
    ap.add_argument("--out", default="assets/css/site.css")
    ap.add_argument("nomi", nargs="+")
    args = ap.parse_args(argv)
    testo = concatena(args.cartella, args.nomi)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(testo, encoding="utf-8")
    print(f"scritto {args.out}: {len(args.nomi)} fogli, {len(testo)//1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
