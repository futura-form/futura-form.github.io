"""Test della trasformazione da salvataggio Wayback a pagina pulita."""
import unittest

from clean_page import pulisci

MAPPA = {"New-Logo-Futuraform-sito-web.jpg": "assets/img/new-logo-futuraform-sito-web.jpg"}
WB = "https://web.archive.org/web/20260303152040/"


def doc(head="", body=""):
    return (
        '<!DOCTYPE html>\n'
        '<!-- saved from url=(0072)https://web.archive.org/web/x/https://www.futuraform.it/it/ -->\n'
        '<html lang="en" class=" js csstransforms" style="--wm-toolbar-height: 67px;">'
        f"<head><meta charset='utf-8'><title>T</title>{head}</head><body>{body}</body></html>"
    )


class PulisciTest(unittest.TestCase):
    def pulito(self, **kw):
        return pulisci(doc(**kw), mappa=MAPPA, slug="index")

    def test_rimuove_il_blocco_toolbar_wayback(self):
        out = self.pulito(body='<!-- BEGIN WAYBACK TOOLBAR INSERT --><div id="wm-ipp-base">x</div>'
                               '<!-- END WAYBACK TOOLBAR INSERT --><p>vero</p>')
        self.assertNotIn("wm-ipp-base", out)
        self.assertIn("vero", out)

    def test_rimuove_lo_script_di_init_wayback(self):
        out = self.pulito(head='<script>__wm.init("https://web.archive.org/web");</script>')
        self.assertNotIn("__wm.init", out)

    def test_rimuove_gli_script_di_analytics_archive(self):
        out = self.pulito(head='<script>var v=archive_analytics.values;</script>')
        self.assertNotIn("archive_analytics", out)

    def test_mette_lang_italiano(self):
        self.assertIn('lang="it"', self.pulito())

    def test_toglie_loffset_della_toolbar_dallhtml(self):
        self.assertNotIn("--wm-toolbar-height", self.pulito())

    def test_conserva_le_classi_modernizr(self):
        out = self.pulito()
        self.assertIn("csstransforms", out)

    def test_rimuove_gli_attributi_del_consent_manager(self):
        out = self.pulito(body='<p data-cmp-info="10" data-cmp-ab="2">x</p>')
        self.assertNotIn("data-cmp-", out)

    def test_riscrive_le_immagini_con_la_mappa(self):
        out = self.pulito(body='<img src="./Home-Page_files/New-Logo-Futuraform-sito-web.jpg">')
        self.assertIn('src="assets/img/new-logo-futuraform-sito-web.jpg"', out)

    def test_riscrive_i_link_di_navigazione_sugli_slug_nuovi(self):
        out = self.pulito(body=f'<a href="{WB}https://www.futuraform.it/it/contatti">C</a>')
        self.assertIn('href="contatti.html"', out)

    def test_la_radice_italiana_diventa_la_home(self):
        out = self.pulito(body=f'<a href="{WB}https://www.futuraform.it/it/">H</a>')
        self.assertIn('href="index.html"', out)

    def test_gli_ancoraggi_della_pagina_servizi_restano_ancoraggi(self):
        out = self.pulito(body=f'<a href="{WB}https://www.futuraform.it/it/'
                               'digital-marketing-i-nostri-servizi#sviluppo_web">S</a>')
        self.assertIn('href="servizi.html#sviluppo_web"', out)

    def test_gli_ancoraggi_di_interfaccia_restano_puri(self):
        out = self.pulito(body=f'<a href="{WB}https://www.futuraform.it/it/#">x</a>'
                               f'<a href="{WB}https://www.futuraform.it/it/#close">y</a>')
        self.assertIn('href="#"', out)
        self.assertIn('href="#close"', out)

    def test_i_link_esterni_perdono_il_prefisso_archive(self):
        out = self.pulito(body=f'<a href="{WB}https://www.linkedin.com/company/futuraform">L</a>')
        self.assertIn('href="https://www.linkedin.com/company/futuraform"', out)
        self.assertNotIn("web.archive.org", out)

    def test_mette_favicon_e_font_e_toglie_canonical(self):
        out = self.pulito(head='<link rel="canonical" href="https://web.archive.org/x">'
                               '<link rel="alternate" hreflang="en-GB" href="x">')
        self.assertIn("assets/img/favicon.png", out)
        self.assertIn("fonts.googleapis.com", out)
        self.assertNotIn('rel="canonical"', out)
        self.assertNotIn("hreflang", out)

    def test_non_resta_nessun_riferimento_ad_archive_org(self):
        out = pulisci(
            doc(body=f'<a href="{WB}https://www.futuraform.it/it/blog">B</a>'
                     '<img src="./Home-Page_files/New-Logo-Futuraform-sito-web.jpg">'),
            mappa=MAPPA, slug="index")
        self.assertNotIn("archive.org", out)


    def test_toglie_archive_anche_dalle_stringhe_json_con_slash_escapati(self):
        """Joomla stampa i suoi percorsi in un JSON inline, dove le URL
        hanno gli slash escapati e sfuggono alla riscrittura normale."""
        out = self.pulito(
            body='<script type="application/json" class="joomla-script-options">'
                 '{"system.paths":{"rootFull":"https:\\/\\/web.archive.org\\/web'
                 '\\/20260303152040\\/https:\\/\\/www.futuraform.it\\/"}}</script>')
        self.assertNotIn("archive.org", out)


if __name__ == "__main__":
    unittest.main()
