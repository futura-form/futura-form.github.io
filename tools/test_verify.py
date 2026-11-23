"""Test dello strumento che difende la rivendicazione centrale."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from verify import differenze_fuori_dai_riquadri


class RiquadriTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def png(self, nome, size, colore, rect=None, colore_rect=None):
        im = Image.new("RGB", size, colore)
        if rect:
            for x in range(rect[0], rect[2]):
                for y in range(rect[1], rect[3]):
                    im.putpixel((x, y), colore_rect)
        p = self.tmp / nome
        im.save(p)
        return p

    def test_una_differenza_dentro_un_riquadro_dichiarato_e_accettata(self):
        a = self.png("a.png", (60, 300), (0, 0, 0))
        b = self.png("b.png", (60, 300), (0, 0, 0), (10, 100, 50, 150), (255, 0, 0))
        fuori = differenze_fuori_dai_riquadri(a, b, riquadri=[(0, 90, 59, 160, "il riquadro previsto")])
        self.assertEqual(fuori, [])

    def test_una_differenza_nella_stessa_riga_ma_in_unaltra_colonna_e_vista(self):
        """Il riquadro copre la colonna della card: una modifica alla
        colonna di fianco cade nelle stesse righe ma non nel riquadro."""
        a = self.png("a.png", (60, 300), (0, 0, 0))
        b = self.png("b.png", (60, 300), (0, 0, 0), (2, 100, 8, 150), (255, 0, 0))
        fuori = differenze_fuori_dai_riquadri(
            a, b, riquadri=[(30, 90, 59, 160, "la colonna della card")])
        self.assertTrue(fuori, "la differenza nella colonna accanto non e' stata vista")

    def test_una_differenza_fuori_dai_riquadri_viene_segnalata(self):
        a = self.png("a.png", (60, 300), (0, 0, 0))
        b = self.png("b.png", (60, 300), (0, 0, 0), (10, 200, 50, 220), (255, 0, 0))
        fuori = differenze_fuori_dai_riquadri(a, b, riquadri=[(0, 90, 59, 160, "il riquadro previsto")])
        self.assertTrue(fuori, "la differenza fuori fascia non e' stata vista")

    def test_vede_una_differenza_di_un_passo_su_un_solo_canale(self):
        """Stesso difetto che compare.py aveva: non deve ripresentarsi."""
        a = self.png("a.png", (60, 300), (10, 20, 30))
        b = self.png("b.png", (60, 300), (10, 20, 30), (10, 200, 50, 220), (10, 20, 34))
        fuori = differenze_fuori_dai_riquadri(a, b, riquadri=[])
        self.assertTrue(fuori, "una differenza di +4 sul blu e' passata inosservata")

    def test_con_una_cucitura_confronta_sotto_allineando_dal_basso(self):
        """La home e' 44px piu' bassa: sotto la cucitura le due immagini
        vanno allineate dal basso, altrimenti il footer traslato sembra
        una differenza e il confronto non dice piu' nulla."""
        a = self.png("a.png", (60, 344), (0, 0, 0), (0, 300, 60, 320), (0, 255, 0))
        b = self.png("b.png", (60, 300), (0, 0, 0), (0, 256, 60, 276), (0, 255, 0))
        fuori = differenze_fuori_dai_riquadri(a, b, riquadri=[], cucitura=200, delta=44)
        self.assertEqual(fuori, [], f"l'allineamento dal basso non ha funzionato: {fuori}")

    def test_senza_cucitura_altezze_diverse_sono_un_errore(self):
        a = self.png("a.png", (60, 344), (0, 0, 0))
        b = self.png("b.png", (60, 300), (0, 0, 0))
        with self.assertRaises(ValueError):
            differenze_fuori_dai_riquadri(a, b, riquadri=[])


class SitoCostruitoTest(unittest.TestCase):
    """L'unico test che guarda il sito reso. Senza di questo una modifica
    a mano a un qualunque HTML o CSS passa l'intera suite."""

    def test_le_cinque_pagine_differiscono_solo_dove_previsto(self):
        import verify
        self.assertEqual(verify.main([]), 0,
                         "una pagina differisce dall'originale fuori dalle "
                         "fasce dichiarate: vedi l'output sopra")


if __name__ == "__main__":
    unittest.main()
