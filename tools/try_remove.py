#!/usr/bin/env python3
"""Prova a togliere un asset dalle pagine e dice se cambia qualcosa.

Rimuove il <link> o lo <script> che lo riferisce da tutte le pagine,
ricattura le cinque schermate, le confronta col riferimento e ripristina
se anche un solo pixel si muove.
"""
import argparse, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGINE = ["index", "chi-siamo", "servizi", "lavori", "contatti"]


def togli(nome):
    """Toglie i tag che riferiscono <nome>. Torna i testi originali."""
    prima = {}
    pattern = re.compile(
        r'[ \t]*<(?:link|script)\b[^>]*(?:href|src)="assets/(?:css|js)/'
        + re.escape(nome) + r'(?:\?[^"]*)?"[^>]*>(?:</script>)?\s*\n?',
        re.I)
    for p in PAGINE:
        f = ROOT / f"{p}.html"
        t = f.read_text(encoding="utf-8")
        prima[p] = t
        f.write_text(pattern.sub("", t), encoding="utf-8")
    return prima


def ripristina(prima):
    for p, t in prima.items():
        (ROOT / f"{p}.html").write_text(t, encoding="utf-8")


def confronta(tmp):
    esiti = {}
    for p in PAGINE:
        shot = Path(tmp) / f"{p}.png"
        subprocess.run([sys.executable, str(ROOT / "tools/shoot.py"),
                        str(ROOT / f"{p}.html"), str(shot), "--width", "1440"],
                       capture_output=True, check=True)
        r = subprocess.run([sys.executable, str(ROOT / "tools/compare.py"),
                            str(ROOT / f"baseline/orig-{p}-1440.png"), str(shot)],
                           capture_output=True, text=True)
        esiti[p] = (r.returncode, r.stdout.strip().splitlines()[0] if r.stdout else "")
    return esiti


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nome", help="nome del file, es. joomla-alert.min.css")
    ap.add_argument("--keep", action="store_true", help="tieni la rimozione anche se cambia")
    args = ap.parse_args(argv)

    prima = togli(args.nome)
    rimosso = sum(1 for p in PAGINE
                  if prima[p] != (ROOT / f"{p}.html").read_text(encoding="utf-8"))
    if rimosso == 0:
        ripristina(prima)
        print(f"{args.nome}: nessun riferimento trovato")
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        esiti = confronta(tmp)

    rotte = [p for p, (rc, _) in esiti.items() if rc != 0]
    if rotte and not args.keep:
        ripristina(prima)
        print(f"{args.nome}: SERVE — cambia {', '.join(rotte)} — ripristinato")
        for p in rotte: print(f"    {p}: {esiti[p][1]}")
        return 1
    if rotte:
        print(f"{args.nome}: rimosso da {rimosso} pagine, MA cambia {', '.join(rotte)}")
        return 1
    print(f"{args.nome}: rimosso da {rimosso} pagine, nessuna differenza")
    return 0


if __name__ == "__main__":
    sys.exit(main())
