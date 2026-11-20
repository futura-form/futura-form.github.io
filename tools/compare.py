#!/usr/bin/env python3
"""Confronta due screenshot pixel per pixel.

Esce con 0 se sono identici, 1 altrimenti. Un'altezza diversa e' gia' una
differenza e viene detta esplicitamente, invece di confrontare in silenzio
la sola parte in comune.
"""
import argparse
import sys

from PIL import Image, ImageChops


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("a", help="immagine di riferimento")
    ap.add_argument("b", help="immagine da confrontare")
    ap.add_argument("--mask", help="dove salvare la maschera delle differenze")
    args = ap.parse_args(argv)

    a = Image.open(args.a).convert("RGB")
    b = Image.open(args.b).convert("RGB")

    if a.size != b.size:
        print(f"DIVERSE: dimensioni {a.size[0]}x{a.size[1]} contro {b.size[0]}x{b.size[1]}")
        if a.size[1] != b.size[1]:
            print(f"  l'altezza cambia: {a.size[1]} contro {b.size[1]} pixel")
        if a.size[0] != b.size[0]:
            print(f"  la larghezza cambia: {a.size[0]} contro {b.size[0]} pixel")
        return 1

    diff = ImageChops.difference(a, b).convert("L")
    changed = sum(1 for px in diff.getdata() if px)
    total = a.size[0] * a.size[1]
    pct = 100.0 * changed / total

    if args.mask:
        diff.point(lambda px: 255 if px else 0).save(args.mask)

    print(f"{pct:.4f}% diversi — {changed} pixel su {total}")
    if changed:
        box = diff.getbbox()
        print(f"  regione interessata: {box}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
