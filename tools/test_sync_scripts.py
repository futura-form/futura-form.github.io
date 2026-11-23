"""Test della copia degli script dai salvataggi."""
import tempfile
import unittest
from pathlib import Path

from sync_scripts import sincronizza


class SincronizzaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.sorgente = self.tmp / "Home-Page_files"
        self.sorgente.mkdir(parents=True)
        self.dest = self.tmp / "build/assets/js"

    def scrivi(self, nome, testo="var x = 1;"):
        (self.sorgente / nome).write_text(testo, encoding="utf-8")

    def test_toglie_il_suffisso_download(self):
        self.scrivi("jquery.min.js.download")
        sincronizza(self.sorgente, self.dest)
        self.assertTrue((self.dest / "jquery.min.js").exists())
        self.assertFalse((self.dest / "jquery.min.js.download").exists())

    def test_salta_gli_script_esclusi(self):
        """La lista e' la stessa che usa clean_page.py per togliere i tag:
        copiare un file che nessuna pagina riferisce lascerebbe peso morto."""
        self.scrivi("jquery.min.js.download")
        self.scrivi("wombat.js.download")
        self.scrivi("iubenda_cs.js.download")
        self.scrivi("script.min.js.download")
        copiati = sincronizza(self.sorgente, self.dest)
        self.assertEqual(copiati, ["jquery.min.js"])

    def test_toglie_gli_script_non_piu_previsti(self):
        self.dest.mkdir(parents=True, exist_ok=True)
        (self.dest / "vecchio.js").write_text("x", encoding="utf-8")
        self.scrivi("jquery.min.js.download")
        sincronizza(self.sorgente, self.dest)
        self.assertFalse((self.dest / "vecchio.js").exists())

    def test_e_idempotente(self):
        self.scrivi("jquery.min.js.download")
        self.assertEqual(sincronizza(self.sorgente, self.dest),
                         sincronizza(self.sorgente, self.dest))


if __name__ == "__main__":
    unittest.main()
