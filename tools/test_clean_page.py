"""Test della trasformazione da salvataggio Wayback a pagina pulita."""
import re
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


    def test_licona_hamburger_diventa_svg_inline(self):
        """I font icona non sono nei salvataggi: i due glifi usati
        diventano SVG, che non dipendono da nessun file esterno."""
        out = self.pulito(body='<a id="offcanvas-toggler">'
                               '<i class="fa fa-bars" aria-hidden="true" title="Navigation"></i></a>')
        self.assertNotIn("fa-bars", out)
        self.assertIn("<svg", out)
        self.assertIn("currentColor", out)

    def test_licona_di_chiusura_diventa_svg_inline(self):
        out = self.pulito(body='<a class="close-offcanvas" href="#">'
                               '<span class="fa fa-remove"></span></a>')
        self.assertNotIn("fa-remove", out)
        self.assertIn("<svg", out)

    def test_le_icone_svg_restano_invisibili_agli_screen_reader(self):
        out = self.pulito(body='<i class="fa fa-bars" aria-hidden="true"></i>')
        self.assertIn('aria-hidden="true"', out)


class IubendaTest(unittest.TestCase):
    def test_toglie_il_pulsante_preferenze_cookie_rimasto_orfano(self):
        """Senza il suo script e' un comando che non fa nulla."""
        out = pulisci(doc(body='<button class="iubenda-tp-btn iubenda-cs-preferences-link">'
                               'Le tue preferenze</button><p>vero</p>'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("iubenda", out)
        self.assertIn("vero", out)

    def test_regge_i_pulsanti_iubenda_annidati(self):
        """Decomporre il genitore lascia i figli nell'iterazione: senza
        guardia la pulizia si schianta sulle pagine vere."""
        out = pulisci(doc(body='<div class="iubenda-cs-container">'
                               '<div class="iubenda-banner"><button class="iubenda-tp-btn">'
                               'x</button></div></div><p>vero</p>'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("iubenda", out)
        self.assertIn("vero", out)

    def test_toglie_la_configurazione_inline_di_iubenda(self):
        out = pulisci(doc(head='<script>var _iub = _iub || [];'
                               '_iub.csConfiguration = {"siteId":1717384};</script>'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("_iub", out)


class JoomlaTest(unittest.TestCase):
    def test_toglie_lo_script_csrf_che_cerca_il_backend(self):
        """Joomla non c'e' piu': quella chiamata lancia "Joomla is not
        defined" a ogni caricamento e configura l'AJAX per un server
        che non esiste."""
        out = pulisci(doc(body="<script>;(function ($) { $.ajaxSetup({ headers: "
                               "{ 'X-CSRF-Token': Joomla.getOptions('csrf.token') } }); "
                               "})(jQuery);</script><p>vero</p>"),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("Joomla", out)
        self.assertIn("vero", out)


class PortfolioTest(unittest.TestCase):
    CARD = ('<div class="sp-simpleportfolio-overlay-wrapper clearfix">'
            '<img class="sp-simpleportfolio-img" src="x.jpg"/>'
            '<div class="sp-simpleportfolio-overlay"><div class="sp-vertical-middle"><div>'
            '<h3 class="sp-simpleportfolio-title">'
            '<a href="https://www.futuraform.it/it/component/spsimpleportfolio/item/9-x?Itemid=0">'
            'Accademia del Profumo</a></h3>'
            '<div class="sp-simpleportfolio-tags">Grafica</div></div>'
            '<div class="sp-simpleportfolio-btns">'
            '<a class="btn-zoom" data-featherlight="image" href="https://www.futuraform.it/'
            'images/portfolio/x.jpg">Zoom</a></div></div></div></div>')

    def pulito(self):
        return pulisci(doc(body=self.CARD), mappa=MAPPA, slug="index")

    def test_toglie_lancora_della_lightbox(self):
        out = self.pulito()
        self.assertNotIn("featherlight", out)
        self.assertNotIn("btn-zoom", out)

    def test_toglie_il_contenitore_del_pulsante_zoom(self):
        self.assertNotIn("sp-simpleportfolio-btns", self.pulito())

    def test_il_titolo_resta_ma_senza_link(self):
        out = self.pulito()
        self.assertIn("Accademia del Profumo", out)
        self.assertIn("sp-simpleportfolio-title", out)
        self.assertNotIn("spsimpleportfolio/item", out)

    def test_loverlay_e_limmagine_restano_intatti(self):
        out = self.pulito()
        self.assertIn("sp-simpleportfolio-overlay", out)
        self.assertIn("sp-simpleportfolio-img", out)
        self.assertIn("sp-simpleportfolio-tags", out)

    def test_nessuna_ancora_resta_nella_card(self):
        self.assertNotIn("<a ", self.pulito().split("sp-simpleportfolio-overlay-wrapper")[1])


class CardContattiTest(unittest.TestCase):
    FORM = ('<div class="sppb-addon-content"><div class="rsform">'
            '<form id="userForm" method="post" action="/it/contatti">'
            '<input name="Nome"><input name="Cognome">'
            '<button type="submit" class="rsform-submit-button btn btn-primary">'
            'Invia la tua richiesta</button></form></div></div>')

    def pulito(self):
        return pulisci(doc(body=self.FORM), mappa=MAPPA, slug="contatti")

    def test_il_form_sparisce(self):
        out = self.pulito()
        self.assertNotIn("userForm", out)
        self.assertNotIn("<form", out)
        self.assertNotIn("<input", out)

    def test_il_contenitore_rsform_resta_per_non_perdere_la_cornice(self):
        """Il bordo sfumato sta su un wrapper piu' esterno: va toccato
        solo il contenuto, non la scatola."""
        out = self.pulito()
        self.assertIn('class="rsform"', out)
        self.assertIn("sppb-addon-content", out)

    def test_ce_un_link_mailto_allindirizzo_giusto(self):
        self.assertIn('href="mailto:info@futuraform.it"', self.pulito())

    def test_il_pulsante_riusa_le_classi_delloriginale(self):
        out = self.pulito()
        self.assertIn("rsform-submit-button", out)
        self.assertIn("btn-primary", out)

    def test_la_card_porta_i_recapiti(self):
        out = self.pulito()
        for atteso in ("info@futuraform.it", "02.61868229", "Via Bisceglie 89/91",
                       "Via di Casalotti 53"):
            self.assertIn(atteso, out, f"manca {atteso}")

    def test_la_card_ha_la_classe_che_ne_fissa_laltezza(self):
        self.assertIn("futuraform-card", self.pulito())


class LinkMortiTest(unittest.TestCase):
    """Le pagine mai salvate non esistono: blog, cookie policy, codice
    etico, le schede portfolio e tutta la versione inglese."""

    def pulito(self, body):
        return pulisci(doc(body=body), mappa=MAPPA, slug="index")

    def test_toglie_la_voce_blog_dal_menu(self):
        out = self.pulito('<ul class="sp-megamenu-parent">'
                          '<li class="sp-menu-item"><a href="https://www.futuraform.it/it/blog">'
                          'Blog</a></li>'
                          '<li class="sp-menu-item"><a href="https://www.futuraform.it/it/contatti">'
                          'CONTATTI</a></li></ul>')
        self.assertNotIn("Blog", out)
        self.assertIn("CONTATTI", out)
        self.assertEqual(len(re.findall(r"<li[ >]", out)), 1,
                         "doveva restare una sola voce")

    def test_toglie_cookie_policy_e_codice_etico_dal_footer(self):
        out = self.pulito('<ul class="menu">'
                          '<li class="item-565"><a href="https://www.futuraform.it/it/cookie-policy">'
                          'Cookie Policy</a></li>'
                          '<li class="item-567"><a href="https://www.futuraform.it/it/'
                          'codice-etico-futuraform">Codice etico</a></li>'
                          '<li class="item-1"><a href="https://www.iubenda.com/privacy-policy/1">'
                          'Privacy policy</a></li></ul>')
        self.assertNotIn("Cookie Policy", out)
        self.assertNotIn("Codice etico", out)
        self.assertIn("Privacy policy", out)

    def test_toglie_la_voce_en_lasciando_lindicatore_it(self):
        """Togliere l'intero modulo libererebbe la col-1 dell'header e
        farebbe riflusso sul desktop."""
        out = self.pulito('<div class="mod-languages"><ul class="lang-block dropdown-menu">'
                          '<li class="lang-active"><a href="https://www.futuraform.it/it/">IT</a></li>'
                          '<li><a href="https://www.futuraform.it/en/">EN</a></li></ul></div>')
        self.assertNotIn(">EN<", out)
        self.assertIn(">IT<", out)
        self.assertIn("mod-languages", out)

    def test_i_titoli_degli_articoli_restano_come_testo(self):
        out = self.pulito('<h3><a href="https://www.futuraform.it/it/blog/influencer-marketing">'
                          'Influencer Marketing</a></h3>')
        self.assertIn("Influencer Marketing", out)
        self.assertNotIn("<a ", out)

    def test_toglie_il_pulsante_leggi_di_piu(self):
        out = self.pulito('<div class="sppb-text-left"><a class="sppb-btn section-button" '
                          'href="https://futuraform.it/it/blog">Leggi di pi\u00f9</a></div>')
        self.assertNotIn("Leggi di", out)

    def test_non_resta_nessun_link_al_dominio_morto(self):
        out = self.pulito('<a href="https://www.futuraform.it/it/blog">x</a>'
                          '<a href="https://www.futuraform.it/en/">y</a>'
                          '<a href="https://www.futuraform.it/it/cookie-policy">z</a>')
        self.assertNotIn("futuraform.it/it/", out)
        self.assertNotIn("futuraform.it/en/", out)

    def test_toglie_og_url_che_punta_al_dominio_morto(self):
        """Una og:url verso un sito spento manda le condivisioni nel
        vuoto: meglio nessuna che una sbagliata."""
        out = pulisci(doc(head='<meta property="og:url" content="https://www.futuraform.it/it/">'
                               '<meta property="og:title" content="Futuraform">'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("og:url", out)
        self.assertIn("og:title", out)

    def test_toglie_il_meta_generator_con_il_segnaposto_non_espanso(self):
        out = pulisci(doc(head='<meta name="generator" content="HELIX_ULTIMATE_GENERATOR_TEXT">'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("HELIX_ULTIMATE", out)

    def test_non_tocca_i_link_esterni(self):
        out = self.pulito('<a href="https://www.linkedin.com/company/futuraform">LinkedIn</a>'
                          '<a href="https://www.facebook.com/futuraform">Facebook</a>')
        self.assertIn("linkedin.com", out)
        self.assertIn("facebook.com", out)

    def test_non_tocca_la_voce_home_vuota(self):
        """Nell'originale e' vuota e alla home si arriva dal logo:
        riempirla o toglierla sarebbe una differenza visibile."""
        out = self.pulito('<ul class="sp-megamenu-parent">'
                          '<li class="sp-menu-item current-item active"></li></ul>')
        self.assertIn("current-item", out)


class RsformTest(unittest.TestCase):
    def test_toglie_gli_script_inline_di_rsformpro(self):
        """Il form non esiste piu': la sua validazione AJAX e' peso morto,
        e lascia nella pagina un percorso assoluto verso un componente
        Joomla che non c'e'."""
        out = pulisci(doc(body='<script>RSFormPro.Ajax.URL = "/it/component/rsform/'
                               '?task=ajaxValidate&Itemid=561";</script>'
                               '<script>ajaxExtraValidationScript[5] = function(){};</script>'
                               '<p>vero</p>'),
                      mappa=MAPPA, slug="contatti")
        self.assertNotIn("RSFormPro", out)
        self.assertNotIn("ajaxExtraValidationScript", out)
        self.assertNotIn("component/rsform", out)
        self.assertIn("vero", out)

    def test_non_resta_nessun_percorso_assoluto_negli_script_inline(self):
        out = pulisci(doc(body='<script>RSFormPro.Ajax.URL = "\\/it\\/component\\/rsform\\/";'
                               '</script>'), mappa=MAPPA, slug="contatti")
        self.assertNotIn("component", out)


class ConfigJoomlaTest(unittest.TestCase):
    def test_toglie_il_blocco_di_configurazione_joomla(self):
        """Lo leggeva core.min.js, che non c'e' piu'. Dentro ci sono
        percorsi assoluti verso componenti che non esistono."""
        out = pulisci(doc(body='<script type="application/json" '
                               'class="joomla-script-options new">'
                               '{"system.keepalive":{"uri":"\\/it\\/component\\/ajax\\/"}}'
                               '</script><p>vero</p>'),
                      mappa=MAPPA, slug="index")
        self.assertNotIn("joomla-script-options", out)
        self.assertNotIn("component", out)
        self.assertIn("vero", out)


class BundleTest(unittest.TestCase):
    """Con --bundle le pagine caricano un solo foglio comune piu' il
    proprio, e i blocchi <style> inline finiscono in quest'ultimo."""

    def pulito(self, head="", body=""):
        return pulisci(doc(head=head, body=body), mappa=MAPPA, slug="index", bundle=True)

    def test_un_solo_link_al_bundle_comune(self):
        out, _ = self.pulito(head='<link href="assets/css/bootstrap.min.css" rel="stylesheet">'
                                  '<link href="assets/css/custom.css" rel="stylesheet">')
        self.assertEqual(out.count("assets/css/site.css"), 1)
        self.assertNotIn("bootstrap.min.css", out)
        self.assertNotIn("custom.css", out)

    def test_il_css_di_pagina_viene_caricato_dopo_il_bundle(self):
        out, _ = self.pulito(head='<link href="assets/css/custom.css" rel="stylesheet">')
        self.assertLess(out.index("assets/css/site.css"), out.index("assets/css/pages/index.css"))

    def test_i_blocchi_style_finiscono_nel_css_di_pagina_in_ordine(self):
        out, css = self.pulito(
            head='<link href="assets/css/custom.css" rel="stylesheet"><style>h1{color:red}</style>',
            body='<style>h2{color:blue}</style><p>x</p>')
        self.assertNotIn("<style", out)
        self.assertLess(css.index("h1{color:red}"), css.index("h2{color:blue}"))

    def test_senza_bundle_restituisce_solo_il_testo(self):
        out = pulisci(doc(), mappa=MAPPA, slug="index")
        self.assertIsInstance(out, str)


class DestinazioneTest(unittest.TestCase):
    """Il CSS della pagina deve finire accanto all'HTML che lo carica,
    non rispetto alla cartella da cui si lancia il comando."""

    def test_il_css_di_pagina_segue_lhtml_di_destinazione(self):
        import subprocess
        import sys
        import tempfile
        from pathlib import Path as P

        tmp = P(tempfile.mkdtemp())
        sorgente = tmp / "sorgente.html"
        sorgente.write_text(
            '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<title>T</title><link href="assets/css/custom.css" rel="stylesheet">'
            '<style>h1{color:red}</style></head><body><p>x</p></body></html>',
            encoding="utf-8")
        mappa = tmp / "mappa.json"
        mappa.write_text("{}", encoding="utf-8")
        destinazione = tmp / "uscita" / "index.html"
        destinazione.parent.mkdir(parents=True)

        r = subprocess.run(
            [sys.executable, str(P(__file__).resolve().parent / "clean_page.py"),
             str(sorgente), str(destinazione), "--slug", "index",
             "--mappa", str(mappa), "--bundle"],
            capture_output=True, text=True, cwd=str(tmp))
        self.assertEqual(r.returncode, 0, r.stderr)

        atteso = destinazione.parent / "assets/css/pages/index.css"
        self.assertTrue(atteso.exists(),
                        f"il CSS di pagina non e' accanto all'HTML: {atteso}")
        self.assertIn("h1{color:red}", atteso.read_text(encoding="utf-8"))
        self.assertFalse((tmp / "assets/css/pages/index.css").exists(),
                         "il CSS e' finito rispetto alla cartella corrente")


if __name__ == "__main__":
    unittest.main()
