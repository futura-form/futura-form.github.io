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


if __name__ == "__main__":
    unittest.main()
