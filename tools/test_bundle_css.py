"""Test della concatenazione dei fogli di stile."""
import tempfile
import unittest
from pathlib import Path

from bundle_css import concatena


class ConcatenaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def scrivi(self, nome, testo):
        p = self.tmp / nome
        p.write_text(testo, encoding="utf-8")
        return p

    def test_rispetta_lordine_dato(self):
        self.scrivi("a.css", "a{color:red}")
        self.scrivi("b.css", "b{color:blue}")
        out = concatena(self.tmp, ["b.css", "a.css"])
        self.assertLess(out.index("b{color:blue}"), out.index("a{color:red}"))

    def test_nomina_ogni_sorgente_in_un_commento(self):
        self.scrivi("a.css", "a{color:red}")
        out = concatena(self.tmp, ["a.css"])
        self.assertIn("a.css", out)

    def test_neutralizza_le_url_verso_archive_org(self):
        """I font icona non esistono piu': lasciare le url produce 404
        a ogni caricamento, senza cambiare nulla a schermo."""
        self.scrivi("a.css", "@font-face{src:url(/web/20260227172126im_/"
                             "https://futuraform.it/fonts/fa-solid-900.woff2)}")
        out = concatena(self.tmp, ["a.css"])
        self.assertNotIn("archive", out)
        self.assertNotIn("/web/2026", out)

    def test_conserva_le_url_data(self):
        self.scrivi("a.css", "a{background:url(data:image/svg+xml,%3csvg/%3e)}")
        out = concatena(self.tmp, ["a.css"])
        self.assertIn("data:image/svg+xml", out)

    def test_toglie_i_commenti_di_coda_wayback(self):
        self.scrivi("a.css", "a{color:red}\n/*\n     FILE ARCHIVED ON 17:21:27 Feb 27, 2026 AND\n*/\n")
        out = concatena(self.tmp, ["a.css"])
        self.assertNotIn("FILE ARCHIVED ON", out)
        self.assertIn("a{color:red}", out)


if __name__ == "__main__":
    unittest.main()
