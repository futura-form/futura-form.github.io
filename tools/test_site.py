"""Proprieta' che il sito costruito deve mantenere a ogni task.

Non sono test di unita': sono le guardie che il piano chiede come
controlli, scritte in modo da poter essere rieseguite.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


class AssetNameTest(unittest.TestCase):
    """GitHub Pages distingue le maiuscole, macOS no: un nome con una
    maiuscola passa in locale e da' 404 online."""

    def test_asset_filenames_are_web_safe(self):
        cattivi = [
            str(p.relative_to(ROOT))
            for p in ASSETS.rglob("*")
            if p.is_file() and re.search(r"[A-Z\s%]", p.name)
        ]
        self.assertEqual(cattivi, [], f"nomi non sicuri per il web: {cattivi}")


class CssTest(unittest.TestCase):
    def test_ogni_poppins_ha_un_fallback_sans_serif(self):
        """Senza rete Google Fonts non arriva: il testo deve cadere su un
        sans di sistema, non sul serif di default del browser."""
        senza = []
        for p in list((ROOT / "assets/css").rglob("*.css")):
            for m in re.finditer(r"font-family:\s*['\"]?Poppins['\"]?[^;}]*", p.read_text(encoding="utf-8")):
                if "sans-serif" not in m.group(0):
                    senza.append(f"{p.name}: {m.group(0)[:60]}")
        self.assertEqual(senza, [], f"Poppins senza fallback: {senza[:5]}")

    def test_le_pagine_caricano_solo_il_bundle_e_il_css_di_pagina(self):
        estranei = []
        for p in ROOT.glob("*.html"):
            for href in re.findall(r'<link[^>]+href="(assets/css/[^"?]+)', p.read_text(encoding="utf-8")):
                if href != "assets/css/site.css" and not href.startswith("assets/css/pages/"):
                    estranei.append(f"{p.name} -> {href}")
        self.assertEqual(estranei, [], f"fogli estranei: {estranei}")

    def test_nessun_riferimento_a_file_css_inesistente(self):
        rotti = []
        for p in ROOT.glob("*.html"):
            for href in re.findall(r'<link[^>]+href="(assets/[^"?]+)', p.read_text(encoding="utf-8")):
                if not (ROOT / href).exists():
                    rotti.append(f"{p.name} -> {href}")
        self.assertEqual(rotti, [], f"link a file mancanti: {rotti}")


if __name__ == "__main__":
    unittest.main()
