"""Comportamenti che gli screenshot a 1440 non possono cogliere.

Il menu mobile vive solo sotto i 992px, il carosello dipende dai cloni
che crea il suo JS, il filtro del portfolio e' tutto interazione.
"""
import functools
import http.server
import socketserver
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = None
_server = None


def setUpModule():
    """Sotto file:// i moduli ES sono bloccati dal CORS e meta' degli
    script non parte: questi comportamenti vanno provati su HTTP."""
    global BASE, _server
    class Silenzioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    handler = functools.partial(Silenzioso, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    _server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    BASE = f"http://127.0.0.1:{_server.server_address[1]}"


def tearDownModule():
    if _server:
        _server.shutdown()
        _server.server_close()


class Pagina:
    def __init__(self, nome, width=1440):
        self.nome, self.width = nome, width

    def __enter__(self):
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch()
        self.page = self.browser.new_page(viewport={"width": self.width, "height": 900})
        self.page.goto(f"{BASE}/{self.nome}", wait_until="load")
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        self.page.wait_for_timeout(1500)
        return self.page

    def __exit__(self, *a):
        self.browser.close()
        self._pw.stop()


class MenuMobileTest(unittest.TestCase):
    """A 390px la navigazione passa tutta dall'offcanvas: se il JS di
    Bootstrap sparisce, il menu non si apre piu' e a 1440 non si vede."""

    def test_il_menu_mobile_si_apre_e_si_chiude(self):
        with Pagina("index.html", width=390) as p:
            corpo = p.locator("body")
            self.assertNotIn("offcanvas-active", corpo.get_attribute("class") or "",
                             "il menu risulta gia' aperto")
            p.locator("#offcanvas-toggler").click()
            p.wait_for_timeout(1500)
            self.assertIn("offcanvas-active", corpo.get_attribute("class") or "",
                          "il menu non si e' aperto")
            self.assertTrue(
                p.locator(".offcanvas-menu a", has_text="Chi siamo").first.is_visible(),
                "il menu aperto non mostra le voci")
            p.locator("a.close-offcanvas").click()
            p.wait_for_timeout(1500)
            self.assertNotIn("offcanvas-active", corpo.get_attribute("class") or "",
                             "il menu non si e' chiuso")

    def test_il_pulsante_del_menu_mostra_licona(self):
        with Pagina("index.html", width=390) as p:
            svg = p.locator("#offcanvas-toggler svg")
            self.assertEqual(svg.count(), 1, "l'icona hamburger non c'e'")
            box = svg.bounding_box()
            self.assertGreater(box["width"], 5, "l'icona e' larga zero")


class CaroselloTest(unittest.TestCase):
    def test_il_carosello_clienti_crea_i_suoi_cloni(self):
        with Pagina("index.html") as p:
            cloni = p.locator(".sppb-carousel-extended-item.clone")
            self.assertGreater(cloni.count(), 0, "il carosello non e' partito")


class PortfolioTest(unittest.TestCase):
    def test_la_griglia_del_portfolio_ha_tutti_i_suoi_elementi(self):
        with Pagina("index.html") as p:
            self.assertEqual(p.locator(".sp-simpleportfolio-item").count(), 6,
                             "il portfolio non ha i suoi sei elementi")

    def test_la_griglia_del_portfolio_e_disposta_da_shuffle(self):
        with Pagina("index.html") as p:
            stile = p.locator(".sp-simpleportfolio-items").first.get_attribute("style") or ""
            self.assertIn("height", stile, "Shuffle non ha calcolato la griglia")


if __name__ == "__main__":
    unittest.main()
