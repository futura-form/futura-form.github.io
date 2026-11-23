"""Test della copia e normalizzazione delle immagini dai salvataggi."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from sync_images import normalizza, sincronizza


class NomiTest(unittest.TestCase):
    def test_minuscole_spazi_e_percento(self):
        self.assertEqual(normalizza("Accademia tiktok_900x500.jpg"),
                         "accademia-tiktok-900x500.jpg")
        self.assertEqual(normalizza("digital%20marketing.JPG"),
                         "digital-marketing.jpg")

    def test_niente_trattini_doppi_o_ai_bordi(self):
        self.assertEqual(normalizza("  a -- b .png"), "a-b.png")


class SincronizzaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sorgente = self.tmp / "salvataggi"
        self.dest = self.tmp / "assets/img"

    def salva(self, cartella, nome, colore=(1, 2, 3)):
        d = self.sorgente / cartella
        d.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (4, 4), colore).save(d / nome)

    def test_deduplica_le_copie_identiche(self):
        self.salva("Home-Page_files", "logo.png")
        self.salva("Contatti_files", "logo.png")
        mappa = sincronizza(self.sorgente, self.dest)
        self.assertEqual(len(list(self.dest.iterdir())), 1)
        self.assertEqual(mappa["logo.png"], "assets/img/logo.png")

    def test_normalizza_i_nomi_nella_mappa(self):
        self.salva("Home-Page_files", "Logo Quadrato.png")
        mappa = sincronizza(self.sorgente, self.dest)
        self.assertEqual(mappa["Logo Quadrato.png"], "assets/img/logo-quadrato.png")
        self.assertTrue((self.dest / "logo-quadrato.png").exists())

    def test_due_file_diversi_con_lo_stesso_nome_sono_un_errore(self):
        """Deduplicare in silenzio file diversi perderebbe un'immagine."""
        self.salva("Home-Page_files", "logo.png", (1, 2, 3))
        self.salva("Contatti_files", "logo.png", (9, 9, 9))
        with self.assertRaises(ValueError):
            sincronizza(self.sorgente, self.dest)

    def test_toglie_le_immagini_che_non_sono_piu_nei_salvataggi(self):
        self.dest.mkdir(parents=True, exist_ok=True)
        (self.dest / "vecchia.png").write_bytes(b"x")
        self.salva("Home-Page_files", "logo.png")
        sincronizza(self.sorgente, self.dest)
        self.assertFalse((self.dest / "vecchia.png").exists())

    def test_e_idempotente(self):
        self.salva("Home-Page_files", "logo.png")
        primo = sincronizza(self.sorgente, self.dest)
        secondo = sincronizza(self.sorgente, self.dest)
        self.assertEqual(primo, secondo)


if __name__ == "__main__":
    unittest.main()
