"""Proprieta' che il sito costruito deve mantenere a ogni task.

Non sono test di unita': sono le guardie che il piano chiede come
controlli, scritte in modo da poter essere rieseguite.
"""
import re
import unittest
from pathlib import Path

PROGETTO = Path(__file__).resolve().parent.parent
ROOT = PROGETTO / "build"          # il sito pubblicato
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

    AMMESSI = {"assets/css/site.css", "assets/css/card-contatti.css"}

    def test_le_pagine_caricano_solo_i_fogli_previsti(self):
        """Il bundle, il CSS della pagina e quello della card. Qualunque
        altro foglio e' un residuo del vecchio Joomla."""
        estranei = []
        for p in ROOT.glob("*.html"):
            for href in re.findall(r'<link[^>]+href="(assets/css/[^"?]+)', p.read_text(encoding="utf-8")):
                if href not in self.AMMESSI and not href.startswith("assets/css/pages/"):
                    estranei.append(f"{p.name} -> {href}")
        self.assertEqual(estranei, [], f"fogli estranei: {estranei}")

    def test_ogni_riferimento_ad_un_asset_combacia_lettera_per_lettera(self):
        """Non basta Path.exists(): su macOS non distingue le maiuscole,
        mentre GitHub Pages si'. Un src="assets/img/Logo.png" per un file
        che si chiama logo.png passerebbe ogni prova in locale e darebbe
        404 solo una volta pubblicato. E vanno guardati tutti i tipi di
        riferimento, non i soli <link>: src, srcset e url() dei CSS."""
        reali = {str(f.relative_to(ROOT)) for f in (ROOT / "assets").rglob("*") if f.is_file()}
        rotti = []
        for p in list(ROOT.glob("*.html")) + list((ROOT / "assets/css").rglob("*.css")):
            testo = p.read_text(encoding="utf-8", errors="replace")
            riferimenti = re.findall(r'(?:href|src)="(assets/[^"?#]+)', testo)
            for valore in re.findall(r'srcset="([^"]+)"', testo):
                riferimenti += [c.strip().split(" ")[0] for c in valore.split(",") if "assets/" in c]
            riferimenti += [u for u in re.findall(r'url\(\s*["\']?([^)"\']+)', testo)
                            if u.startswith("assets/")]
            for r in set(riferimenti):
                if r not in reali:
                    rotti.append(f"{p.name} -> {r}")
        self.assertEqual(rotti, [], f"riferimenti che non combaciano: {rotti}")


class PercorsiTest(unittest.TestCase):
    def test_nessun_percorso_assoluto(self):
        """GitHub Pages serve da https://utente.github.io/<repo>/: un
        percorso che inizia con / esce dalla sottocartella e da' 404,
        mentre in locale funziona."""
        colpevoli = []
        for p in list(ROOT.glob("*.html")) + list((ROOT / "assets/css").rglob("*.css")):
            testo = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'(?:href|src)="(/[^/"][^"]*)"', testo):
                colpevoli.append(f"{p.name}: {m.group(1)[:50]}")
            for m in re.finditer(r'url\(\s*["\']?(/[^/)"\']+)', testo):
                colpevoli.append(f"{p.name}: url({m.group(1)[:50]})")
        self.assertEqual(colpevoli, [], f"percorsi assoluti: {colpevoli}")

    def test_la_sola_rete_automatica_e_google_fonts(self):
        """Tutto il resto deve stare nel repo. I link a Facebook,
        LinkedIn e iubenda sono cliccati dall'utente, non caricati."""
        automatici = set()
        for p in ROOT.glob("*.html"):
            testo = p.read_text(encoding="utf-8")
            for m in re.finditer(r'<(?:link|script|img|iframe)[^>]+(?:href|src)="(https?://[^"]+)"', testo):
                automatici.add(m.group(1).split("/")[2])
        self.assertEqual(automatici, {"fonts.googleapis.com"},
                         f"richieste automatiche verso l'esterno: {automatici}")

    def test_ogni_ancoraggio_esiste_nella_pagina_di_destinazione(self):
        mancanti = []
        for p in ROOT.glob("*.html"):
            testo = p.read_text(encoding="utf-8")
            for pagina, ancora in re.findall(r'href="([^"#:]*)#([^"]+)"', testo):
                if ancora in ("", "close", "expand"):
                    continue
                dest = ROOT / (pagina or p.name)
                if not dest.exists():
                    mancanti.append(f"{p.name} -> {pagina}#{ancora} (pagina assente)")
                elif f'id="{ancora}"' not in dest.read_text(encoding="utf-8") \
                        and f'name="{ancora}"' not in dest.read_text(encoding="utf-8"):
                    mancanti.append(f"{p.name} -> {pagina or p.name}#{ancora}")
        self.assertEqual(mancanti, [], f"ancoraggi che non esistono: {mancanti}")


class LinkTest(unittest.TestCase):
    def test_nessun_riferimento_al_dominio_spento_o_ad_archive(self):
        colpevoli = []
        for p in list(ROOT.glob("*.html")) + list((ROOT / "assets/css").rglob("*.css")):
            testo = p.read_text(encoding="utf-8", errors="replace")
            for schema in ("futuraform.it/it/", "futuraform.it/en/", "web.archive.org",
                           "/web/2026"):
                if schema in testo:
                    colpevoli.append(f"{p.name}: {schema}")
        self.assertEqual(colpevoli, [], f"riferimenti a destinazioni morte: {colpevoli}")

    def test_ogni_link_interno_punta_a_una_pagina_che_esiste(self):
        rotti = []
        for p in ROOT.glob("*.html"):
            for href in re.findall(r'href="([^"#:]+\.html)(?:#[^"]*)?"', p.read_text(encoding="utf-8")):
                if not (ROOT / href).exists():
                    rotti.append(f"{p.name} -> {href}")
        self.assertEqual(rotti, [], f"link a pagine inesistenti: {rotti}")


if __name__ == "__main__":
    unittest.main()
