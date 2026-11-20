"""Test degli strumenti di verifica in tools/."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent
COMPARE = TOOLS / "compare.py"
SHOOT = TOOLS / "shoot.py"


def run_compare(a, b, *extra):
    return subprocess.run(
        [sys.executable, str(COMPARE), str(a), str(b), *extra],
        capture_output=True, text=True,
    )


class CompareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def png(self, name, size, color):
        p = self.tmp / name
        Image.new("RGB", size, color).save(p)
        return p

    def test_identical_images_report_zero_and_exit_zero(self):
        a = self.png("a.png", (40, 60), (10, 20, 30))
        b = self.png("b.png", (40, 60), (10, 20, 30))
        r = run_compare(a, b)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.0000%", r.stdout)

    def test_one_different_pixel_exits_one(self):
        a = self.png("a.png", (40, 60), (10, 20, 30))
        b = self.png("b.png", (40, 60), (10, 20, 30))
        with Image.open(b) as im:
            im.putpixel((5, 5), (255, 0, 0))
            im.save(b)
        r = run_compare(a, b)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("1 pixel", r.stdout)

    def test_different_heights_are_reported_not_cropped(self):
        a = self.png("a.png", (40, 60), (10, 20, 30))
        b = self.png("b.png", (40, 90), (10, 20, 30))
        r = run_compare(a, b)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("altezza", r.stdout.lower())
        self.assertIn("60", r.stdout)
        self.assertIn("90", r.stdout)

    def test_writes_a_difference_mask_when_asked(self):
        a = self.png("a.png", (40, 60), (10, 20, 30))
        b = self.png("b.png", (40, 60), (10, 20, 30))
        with Image.open(b) as im:
            im.putpixel((5, 5), (255, 0, 0))
            im.save(b)
        mask = self.tmp / "mask.png"
        run_compare(a, b, "--mask", str(mask))
        self.assertTrue(mask.exists(), "la maschera non è stata scritta")
        with Image.open(mask) as m:
            self.assertEqual(m.size, (40, 60))


class ShootTest(unittest.TestCase):
    """Lo screenshot deve avere la larghezza chiesta e non mostrare
    la toolbar Wayback ne' il banner cookie."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def page(self, body):
        p = self.tmp / "page.html"
        p.write_text(
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<style>body{margin:0;background:#fff}</style></head>"
            f"<body>{body}</body></html>",
            encoding="utf-8",
        )
        return p

    def shoot(self, page, out, width):
        return subprocess.run(
            [sys.executable, str(SHOOT), str(page), str(out), "--width", str(width)],
            capture_output=True, text=True,
        )

    def test_screenshot_has_the_requested_width(self):
        page = self.page("<div style='height:300px'>ciao</div>")
        out = self.tmp / "shot.png"
        r = self.shoot(page, out, 400)
        self.assertEqual(r.returncode, 0, r.stderr)
        with Image.open(out) as im:
            self.assertEqual(im.size[0], 400)

    def test_screenshot_is_full_page_not_just_the_viewport(self):
        page = self.page("<div style='height:3000px'>alto</div>")
        out = self.tmp / "shot.png"
        self.shoot(page, out, 400)
        with Image.open(out) as im:
            self.assertGreaterEqual(im.size[1], 3000)

    def test_wayback_toolbar_is_suppressed(self):
        page = self.page(
            "<div id='wm-ipp-base' style='height:200px;background:#ff0000'></div>"
            "<div style='height:300px'></div>"
        )
        out = self.tmp / "shot.png"
        self.shoot(page, out, 400)
        with Image.open(out) as im:
            colors = {c for _, c in im.convert("RGB").getcolors(maxcolors=100000)}
        self.assertNotIn((255, 0, 0), colors, "la toolbar Wayback e' finita nello screenshot")

    def test_fonts_option_actually_changes_the_rendering(self):
        """--fonts deve far arrivare davvero Poppins: senza, il testo cade
        sul sans di sistema e le due immagini non possono coincidere."""
        page = self.page(
            "<p style=\"font-family:'Poppins',sans-serif;font-size:40px\">"
            "Metodo Visione Creativita</p>"
        )
        senza = self.tmp / "senza.png"
        con = self.tmp / "con.png"
        self.shoot(page, senza, 400)
        subprocess.run(
            [sys.executable, str(SHOOT), str(page), str(con), "--width", "400", "--fonts"],
            capture_output=True, text=True,
        )
        with Image.open(senza) as a, Image.open(con) as b:
            self.assertEqual(a.size, b.size)
            self.assertNotEqual(list(a.convert("RGB").getdata()),
                                list(b.convert("RGB").getdata()),
                                "--fonts non ha cambiato nulla: Poppins non e' arrivato")

    def test_cookie_banner_is_suppressed(self):
        page = self.page(
            "<div id='iubenda-cs-banner' style='height:200px;background:#00ff00'></div>"
            "<div style='height:300px'></div>"
        )
        out = self.tmp / "shot.png"
        self.shoot(page, out, 400)
        with Image.open(out) as im:
            colors = {c for _, c in im.convert("RGB").getcolors(maxcolors=100000)}
        self.assertNotIn((0, 255, 0), colors, "il banner cookie e' finito nello screenshot")


if __name__ == "__main__":
    unittest.main()
