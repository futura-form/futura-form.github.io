#!/usr/bin/env python3
"""Verifica la rivendicazione centrale: le uniche differenze rispetto
all'originale archiviato sono quelle volute.

Per ogni pagina si dichiara dove le differenze sono ammesse e perche'.
Ovunque altrove si pretende identita' esatta, canale per canale. Se
qualcuno modifica un HTML o un CSS a mano, questo strumento se ne
accorge: e' l'unica cosa che lo faccia.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent

# I riquadri sono (x0, y0, x1, y1, motivo) in coordinate della baseline,
# con un margine attorno alla misura. Sono rettangoli e non semplici fasce
# di righe perche' la card occupa una sola colonna: una fascia di righe
# accetterebbe per sbaglio anche le modifiche al testo che le sta di
# fianco. "cucitura" e "delta" servono solo alla home, piu' bassa di 44px
# per il pulsante rimosso: sotto la cucitura le immagini si allineano dal
# basso, altrimenti il footer traslato coprirebbe di rumore il confronto.
ATTESE = {
    "index": {
        "cucitura": 3984,
        "delta": 44,
        "riquadri": [
            (470, 20, 965, 50, "riga del menu: rimossa la voce Blog"),
            (0, 4076, 1439, 4110, "dove stava il pulsante Leggi di piu'"),
            (728, 4244, 1281, 5099, "card contatti al posto del form"),
            (0, 5224, 1439, 5258, "cucitura del footer, risalito di 44px"),
            (1110, 5365, 1248, 5428, "footer: via Cookie Policy e Codice etico"),
        ],
    },
    "chi-siamo": {"riquadri": [
        (470, 20, 965, 50, "riga del menu: rimossa la voce Blog"),
        (760, 1809, 1250, 2595, "card contatti al posto del form"),
        (1110, 2899, 1248, 2962, "footer: via Cookie Policy e Codice etico"),
    ]},
    "servizi": {"riquadri": [
        (470, 20, 965, 50, "riga del menu: rimossa la voce Blog"),
        (760, 7156, 1250, 7942, "card contatti al posto del form"),
        (1110, 8246, 1248, 8309, "footer: via Cookie Policy e Codice etico"),
    ]},
    "lavori": {"riquadri": [
        (470, 20, 965, 50, "riga del menu: rimossa la voce Blog"),
        (760, 7090, 1250, 7877, "card contatti al posto del form"),
        (1110, 8181, 1248, 8244, "footer: via Cookie Policy e Codice etico"),
    ]},
    "contatti": {"riquadri": [
        (470, 20, 965, 50, "riga del menu: rimossa la voce Blog"),
        (760, 280, 1250, 1066, "card contatti al posto del form"),
        (1110, 1370, 1248, 1433, "footer: via Cookie Policy e Codice etico"),
    ]},
}


def _punti_diversi(a, b, ammessi, offset=0, passo=1):
    """I punti in cui le due immagini differiscono, su qualunque canale,
    esclusi quelli dentro un riquadro ammesso."""
    d = ImageChops.difference(a, b)
    px = d.load()
    w, h = d.size
    fuori = []
    for y in range(h):
        vero_y = y + offset
        for x in range(0, w, passo):
            if px[x, y] == (0, 0, 0):
                continue
            if any(x0 <= x <= x1 and y0 <= vero_y <= y1
                   for x0, y0, x1, y1 in ammessi):
                continue
            fuori.append((x, vero_y))
    return fuori


def differenze_fuori_dai_riquadri(percorso_a, percorso_b, riquadri,
                                  cucitura=None, delta=0, passo=1):
    """Torna i riquadri che differiscono fuori da quelli ammessi."""
    ammessi = [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in riquadri]
    with Image.open(percorso_a) as ia, Image.open(percorso_b) as ib:
        a, b = ia.convert("RGB"), ib.convert("RGB")
        if a.size[0] != b.size[0]:
            raise ValueError(f"larghezze diverse: {a.size[0]} e {b.size[0]}")
        if cucitura is None:
            if a.size[1] != b.size[1]:
                raise ValueError(
                    f"altezze diverse ({a.size[1]} e {b.size[1]}) e nessuna "
                    "cucitura dichiarata: il confronto non direbbe nulla")
            punti = _punti_diversi(a, b, ammessi, passo=passo)
        else:
            if a.size[1] - b.size[1] != delta:
                raise ValueError(
                    f"delta atteso {delta}, trovato {a.size[1] - b.size[1]}")
            w = a.size[0]
            punti = _punti_diversi(
                a.crop((0, 0, w, cucitura)), b.crop((0, 0, w, cucitura)),
                ammessi, passo=passo)
            punti += _punti_diversi(
                a.crop((0, cucitura + delta, w, a.size[1])),
                b.crop((0, cucitura, w, b.size[1])), ammessi,
                offset=cucitura, passo=passo)

    blocchi = []
    for x, y in punti:
        if blocchi and y <= blocchi[-1][3] + 2:
            b2 = blocchi[-1]
            b2[0] = min(b2[0], x); b2[2] = max(b2[2], x); b2[3] = y
        else:
            blocchi.append([x, y, x, y])
    return [tuple(b2) for b2 in blocchi]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pagine", nargs="*", default=sorted(ATTESE),
                    help="quali pagine verificare (default: tutte)")
    ap.add_argument("--passo", type=int, default=1,
                    help="campiona una colonna ogni N (1 = tutte)")
    args = ap.parse_args(argv)

    esito = 0
    with tempfile.TemporaryDirectory() as tmp:
        for slug in (args.pagine or sorted(ATTESE)):
            attesa = ATTESE[slug]
            riferimento = ROOT / f"baseline/orig-{slug}-1440.png"
            if not riferimento.exists():
                print(f"{slug}: manca {riferimento}")
                esito = 1
                continue
            shot = Path(tmp) / f"{slug}.png"
            subprocess.run(
                [sys.executable, str(ROOT / "tools/shoot.py"),
                 str(ROOT / f"{slug}.html"), str(shot), "--width", "1440"],
                check=True, capture_output=True)
            try:
                fuori = differenze_fuori_dai_riquadri(
                    riferimento, shot, attesa["riquadri"],
                    cucitura=attesa.get("cucitura"), delta=attesa.get("delta", 0),
                    passo=args.passo)
            except ValueError as e:
                print(f"{slug}: {e}")
                esito = 1
                continue
            if fuori:
                print(f"{slug}: DIFFERENZE NON PREVISTE nei riquadri {fuori[:6]}")
                esito = 1
            else:
                print(f"{slug}: solo le differenze volute "
                      f"({len(attesa['riquadri'])} riquadri dichiarati)")
    return esito


if __name__ == "__main__":
    sys.exit(main())
