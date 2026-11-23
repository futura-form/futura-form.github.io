#!/usr/bin/env python3
"""Da salvataggio Internet Archive a pagina statica pulita.

Toglie l'iniezione Wayback, riscrive <head>, e porta ogni riferimento
interno su percorsi relativi dentro assets/.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment

FONTS = ("https://fonts.googleapis.com/css2?family=Poppins:"
         "ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;"
         "1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")

# percorso del sito originale -> file del sito nuovo
PAGINE = {
    "": "index.html",
    "it": "index.html",
    "it/": "index.html",
    "it/contatti": "contatti.html",
    "it/futuraform-chi-siamo": "chi-siamo.html",
    "it/digital-marketing-i-nostri-servizi": "servizi.html",
    "it/i-nostri-lavori": "lavori.html",
}

# file che non passano nel sito nuovo
CSS_ESCLUSI = {
    "banner-styles.css", "iconochive.css",   # toolbar Wayback
    "css", "css(1)",                          # font con URL su archive.org
    "joomla-alert.min.css", "system-j4.min.css",  # interfaccia Joomla, verificato inutilizzata
    "font-awesome.min.css", "fa-v4-shims.css", "stellar-icon.css",  # icone -> SVG inline
    "magnific-popup.css", "featherlight.min.css",  # lightbox rimossa
}
JS_ESCLUSI = {
    "bundle-playback.js", "wombat.js", "ruffle.js", "athena.js", "core-it.js",  # Wayback
    "69940543.js", "1717384.js", "iubenda_cs.js",                # consent manager
    "core.min.js", "showon-es5.min.js", "showon.min.js",         # core Joomla non usato
    "keepalive-es5.min.js", "keepalive.min.js",
    "messages-es5.min.js", "messages.min.js",
    "bootstrap-es5.min.js", "alert.min.js", "button.min.js",     # moduli singoli: c'e' il bundle
    "carousel.min.js", "collapse.min.js", "dropdown.min.js",
    "modal.min.js", "offcanvas.min.js", "popover.min.js",
    "scrollspy.min.js", "tab.min.js", "toast.min.js",
    "jquery.magnific-popup.min.js", "featherlight.min.js",       # lightbox rimossa
    "script.min.js",                          # libreria RSFormPro: il form non c'e' piu'
}
CSS_RINOMINATI = {"bootstrap(1).min.css": "bootstrap-2.min.css"}

# I font icona non sono nei salvataggi e i CSS li cercano su archive.org.
# Nel markup si usano solo questi due glifi: diventano SVG inline, misurati
# in em cosi' da ereditare dimensione e colore come faceva il font.
STILE_ICONA = "width:1em;height:1em;vertical-align:-.125em;fill:currentColor"
ICONE = {
    "fa-bars": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" '
        f'style="{STILE_ICONA}"><path d="M16 132h416c8.8 0 16-7.2 16-16V76c0-8.8-7.2-16-16-16H16'
        'C7.2 60 0 67.2 0 76v40c0 8.8 7.2 16 16 16zm0 160h416c8.8 0 16-7.2 16-16v-40c0-8.8-7.2-16'
        '-16-16H16c-8.8 0-16 7.2-16 16v40c0 8.8 7.2 16 16 16zm0 160h416c8.8 0 16-7.2 16-16v-40c0'
        '-8.8-7.2-16-16-16H16c-8.8 0-16 7.2-16 16v40c0 8.8 7.2 16 16 16z"/></svg>'
    ),
    "fa-remove": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 352 512" '
        f'style="{STILE_ICONA}"><path d="M242.7 256l100.1-100.1c12.3-12.3 12.3-32.2 0-44.5l-22.2'
        '-22.2c-12.3-12.3-32.2-12.3-44.5 0L176 189.3 75.9 89.2c-12.3-12.3-32.2-12.3-44.5 0L9.2 '
        '111.5c-12.3 12.3-12.3 32.2 0 44.5L109.3 256 9.2 356.1c-12.3 12.3-12.3 32.2 0 44.5l22.2 '
        '22.2c12.3 12.3 32.2 12.3 44.5 0L176 322.7l100.1 100.1c12.3 12.3 32.2 12.3 44.5 0l22.2'
        '-22.2c12.3-12.3 12.3-32.2 0-44.5L242.7 256z"/></svg>'
    ),
}

# Il form puntava a un backend Joomla che non esiste piu'. Lo sostituisce
# una card con un mailto, della stessa altezza del form perche' la colonna
# che lo conteneva detta l'altezza della sezione.
EMAIL = "info@futuraform.it"
CARD_CONTATTI = """
<div class="futuraform-card">
  <p class="futuraform-card-occhiello">Parliamone</p>
  <p class="futuraform-card-testo">Raccontaci cosa ti serve in due righe.
     Ti risponde una persona, non un modulo.</p>
  <ul class="futuraform-card-recapiti">
    <li><span>E-mail</span><a href="mailto:info@futuraform.it">info@futuraform.it</a></li>
    <li><span>Telefono</span><a href="tel:+390261868229">(+39) 02.61868229</a></li>
  </ul>
  <ul class="futuraform-card-sedi">
    <li><span>Sede legale</span>Via Goldoni, 51 &ndash; 20129 Milano</li>
    <li><span>Milano</span>Via Bisceglie 89/91 &ndash; 20152 Milano</li>
    <li><span>Roma</span>Via di Casalotti 53 &ndash; 00166 Roma</li>
  </ul>
  <a class="rsform-submit-button btn btn-primary futuraform-card-azione"
     href="mailto:info@futuraform.it">Scrivici una mail</a>
</div>
"""

PREFISSO_WB = re.compile(r"https?://web\.archive\.org/web/\d+[a-z_]*/")
# stessa cosa dentro il JSON inline di Joomla, dove gli slash sono escapati
PREFISSO_WB_JSON = re.compile(r"https?:\\/\\/web\.archive\.org\\/web\\/\d+[a-z_]*\\/")
BLOCCO_TOOLBAR = re.compile(
    r"<!--\s*BEGIN WAYBACK TOOLBAR INSERT\s*-->.*?<!--\s*END WAYBACK TOOLBAR INSERT\s*-->",
    re.S | re.I)
SCRIPT_WAYBACK = re.compile(r"__wm\.|archive_analytics|RufflePlayer|wbhack")


def _nome_asset(url):
    """Estrae il nome del file da un riferimento ./<Pagina>_files/<nome>."""
    m = re.search(r"_files/(.+)$", url)
    return unquote(m.group(1)) if m else None


def _riscrivi_asset(url, mappa):
    """Riscrive un riferimento a ./<Pagina>_files/<nome>. None = togli il tag."""
    nome = _nome_asset(url)
    if nome is None:
        return url
    if nome.endswith(".download"):
        nome = nome[: -len(".download")]
    if nome in CSS_ESCLUSI or nome in JS_ESCLUSI:
        return None
    if nome in mappa:
        return mappa[nome]
    if nome.endswith(".css"):
        return "assets/css/" + CSS_RINOMINATI.get(nome, nome)
    if nome.endswith(".js"):
        return "assets/js/" + nome
    return "assets/img/" + nome


def _riscrivi_link(href, slug):
    """Riscrive un href di navigazione. Torna None per lasciarlo com'e'."""
    pulito = PREFISSO_WB.sub("", href)
    m = re.match(r"https?://(?:www\.)?futuraform\.it/(.*)$", pulito)
    if not m:
        return pulito
    resto = m.group(1)
    percorso, _, frammento = resto.partition("#")
    destinazione = PAGINE.get(percorso.rstrip("/") or "") or PAGINE.get(percorso)
    if destinazione is None:
        return pulito  # pagina mai salvata: la toglie il Task 9
    if frammento or resto.endswith("#"):
        if destinazione == f"{slug}.html":
            return f"#{frammento}"
        return f"{destinazione}#{frammento}" if frammento else destinazione
    return destinazione


DOMINIO_MORTO = re.compile(r"^https?://(?:www\.)?futuraform\.it/", re.I)


def _togli_link_morti(soup):
    """Porta via i link alle pagine mai salvate: blog, cookie policy,
    codice etico, schede portfolio, versione inglese. Cosa si toglie
    dipende da che ruolo ha il link.

    - voce di un menu: va via tutta la voce, altrimenti resta un
      elemento di lista vuoto che occupa spazio;
    - titolo dentro un'intestazione: resta il testo, che e' contenuto;
    - tutto il resto (pulsanti): va via il link.
    """
    for a in list(soup.find_all("a", href=True)):
        if a.attrs is None or not DOMINIO_MORTO.match(a["href"]):
            continue
        voce = a.find_parent("li")
        if voce is not None and voce.find_parent(["ul", "ol"]) is not None:
            voce.decompose()
            continue
        if a.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"]) is not None:
            a.unwrap()
            continue
        a.decompose()


def pulisci(html, mappa, slug, bundle=False):
    html = BLOCCO_TOOLBAR.sub("", html)
    soup = BeautifulSoup(html, "html.parser")

    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "saved from url" in c or "Wayback Rewrite" in c or "WAYBACK TOOLBAR" in c:
            c.extract()

    for t in soup.select("#wm-ipp-base, #wm-ipp-print, #wm-ipp"):
        t.decompose()

    # il blocco di configurazione Joomla lo leggeva core.min.js, rimosso
    for s in soup.select("script.joomla-script-options"):
        s.decompose()

    for s in soup.find_all("script"):
        src = s.get("src", "")
        testo = s.string or ""
        if "archive.org" in src or (not src and SCRIPT_WAYBACK.search(testo)):
            s.decompose()
        elif not src and ("_iub" in testo or "Joomla." in testo
                          or "RSFormPro" in testo
                          or "ajaxExtraValidationScript" in testo):
            s.decompose()

    # Senza il suo script il pulsante delle preferenze cookie non fa nulla.
    # Si itera su una copia e si salta chi e' gia' sparito insieme al padre.
    for t in list(soup.find_all(class_=True)):
        if t.attrs is None:
            continue
        if any("iubenda" in c for c in t.get("class") or []):
            t.decompose()

    html_tag = soup.find("html")
    if html_tag:
        html_tag["lang"] = "it"
        stile = html_tag.get("style", "")
        if "--wm-toolbar-height" in stile:
            resto = re.sub(r"--wm-toolbar-height\s*:[^;]*;?", "", stile).strip()
            if resto:
                html_tag["style"] = resto
            else:
                del html_tag["style"]
        if html_tag.get("class"):
            html_tag["class"] = [c for c in html_tag["class"] if c]

    for t in soup.find_all(True):
        for a in [a for a in t.attrs if a.startswith("data-cmp-")]:
            del t[a]

    for t in soup.find_all(["link", "script", "img", "source", "iframe"]):
        for attr in ("href", "src"):
            val = t.get(attr)
            if not val or "_files/" not in val:
                continue
            nuovo = _riscrivi_asset(val, mappa)
            if nuovo is None:
                t.decompose()
                break
            t[attr] = nuovo
        else:
            if t.get("srcset"):
                parti = []
                for p in t["srcset"].split(","):
                    p = p.strip()
                    url, _, desc = p.partition(" ")
                    n = _riscrivi_asset(url, mappa) if "_files/" in url else PREFISSO_WB.sub("", url)
                    if n:
                        parti.append(f"{n} {desc}".strip())
                t["srcset"] = ", ".join(parti)

    for t in soup.find_all(["i", "span"], class_=True):
        classi = t.get("class")
        for nome, svg in ICONE.items():
            if nome in classi:
                icona = BeautifulSoup(svg, "html.parser")
                for attr in ("aria-hidden", "title", "aria-label"):
                    if t.get(attr):
                        icona.svg[attr] = t[attr]
                if not icona.svg.get("aria-hidden"):
                    icona.svg["aria-hidden"] = "true"
                t.replace_with(icona)
                break

    # Il form di contatto e' in tutte e cinque le pagine, sopra il footer.
    for form in soup.find_all("form", id="userForm"):
        contenitore = form.find_parent(class_="rsform") or form.parent
        contenitore.clear()
        contenitore.append(BeautifulSoup(CARD_CONTATTI, "html.parser"))

    # Portfolio: via la lightbox, resta il solo effetto hover. Le immagini
    # ad alta risoluzione non sono nei salvataggi e le schede di dettaglio
    # non sono mai state salvate.
    for btns in soup.select(".sp-simpleportfolio-btns"):
        btns.decompose()
    for a in soup.select("a[data-featherlight], a.btn-zoom"):
        a.decompose()
    for titolo in soup.select(".sp-simpleportfolio-title"):
        for a in titolo.find_all("a"):
            a.unwrap()

    for a in soup.find_all("a", href=True):
        a["href"] = _riscrivi_link(a["href"], slug)

    _togli_link_morti(soup)
    for f in soup.find_all("form", action=True):
        f["action"] = PREFISSO_WB.sub("", f["action"])

    # og:url puntava al dominio spento: una condivisione finirebbe nel
    # vuoto. Il meta generator porta un segnaposto mai espanso.
    for m in list(soup.find_all("meta")):
        if m.attrs is None:
            continue
        if m.get("property") == "og:url":
            m.decompose()
        elif m.get("name") == "generator":
            m.decompose()

    head = soup.find("head")
    if head:
        for l in head.find_all("link", rel=True):
            rel = " ".join(l.get("rel"))
            if rel in ("canonical", "alternate") or l.get("hreflang"):
                l.decompose()
            elif "icon" in rel:
                l.decompose()
        icona = soup.new_tag("link", rel="icon", type="image/png", href="assets/img/favicon.png")
        font = soup.new_tag("link", rel="stylesheet", href=FONTS)
        primo = head.find(["link", "style", "script"])
        if primo:
            primo.insert_before(icona)
            icona.insert_after(font)
        else:
            head.append(icona)
            head.append(font)

    css_pagina = None
    if bundle:
        css_pagina = _raccogli_stili(soup, slug)

    out = str(soup)
    out = PREFISSO_WB.sub("", out)
    out = PREFISSO_WB_JSON.sub("", out)
    return (out, css_pagina) if bundle else out


def _raccogli_stili(soup, slug):
    """Sostituisce i <link> dei singoli fogli con il bundle, e sposta i
    blocchi <style> — testa e corpo, in ordine di documento — nel CSS
    della pagina, caricato subito dopo."""
    links = [l for l in soup.find_all("link", href=True)
             if l["href"].startswith("assets/css/")]
    blocchi = []
    for st in soup.find_all("style"):
        blocchi.append(st.decode_contents())
        st.decompose()

    bundle = soup.new_tag("link", rel="stylesheet", href="assets/css/site.css")
    pagina = soup.new_tag("link", rel="stylesheet", href=f"assets/css/pages/{slug}.css")
    card = soup.new_tag("link", rel="stylesheet", href="assets/css/card-contatti.css")
    if links:
        links[0].insert_before(bundle)
        bundle.insert_after(pagina)
        pagina.insert_after(card)
        for l in links:
            l.decompose()
    else:
        soup.find("head").append(bundle)
        bundle.insert_after(pagina)
        pagina.insert_after(card)
    return "\n".join(b.strip() for b in blocchi if b.strip()) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sorgente")
    ap.add_argument("destinazione")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--mappa", default="tools/asset-map.json")
    ap.add_argument("--bundle", action="store_true",
                    help="un solo site.css piu' il CSS della pagina")
    args = ap.parse_args(argv)

    mappa = json.loads(Path(args.mappa).read_text(encoding="utf-8"))
    html = Path(args.sorgente).read_text(encoding="utf-8", errors="replace")
    risultato = pulisci(html, mappa, args.slug, bundle=args.bundle)
    if args.bundle:
        testo, css = risultato
        # accanto all'HTML di destinazione, non rispetto alla cartella
        # da cui si lancia il comando: e' l'HTML che lo carica
        css_path = Path(args.destinazione).parent / f"assets/css/pages/{args.slug}.css"
        css_path.parent.mkdir(parents=True, exist_ok=True)
        css_path.write_text(css, encoding="utf-8")
        print(f"scritto {args.destinazione} e {css_path}")
    else:
        testo = risultato
        print(f"scritto {args.destinazione}")
    Path(args.destinazione).write_text(testo, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
