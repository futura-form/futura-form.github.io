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
CSS_ESCLUSI = {"banner-styles.css", "iconochive.css", "css", "css(1)"}
JS_ESCLUSI = {"bundle-playback.js", "wombat.js", "ruffle.js", "athena.js", "core-it.js"}
CSS_RINOMINATI = {"bootstrap(1).min.css": "bootstrap-2.min.css"}

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


def pulisci(html, mappa, slug):
    html = BLOCCO_TOOLBAR.sub("", html)
    soup = BeautifulSoup(html, "html.parser")

    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "saved from url" in c or "Wayback Rewrite" in c or "WAYBACK TOOLBAR" in c:
            c.extract()

    for t in soup.select("#wm-ipp-base, #wm-ipp-print, #wm-ipp"):
        t.decompose()

    for s in soup.find_all("script"):
        src = s.get("src", "")
        if "archive.org" in src or (not src and SCRIPT_WAYBACK.search(s.string or "")):
            s.decompose()

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

    for a in soup.find_all("a", href=True):
        a["href"] = _riscrivi_link(a["href"], slug)
    for f in soup.find_all("form", action=True):
        f["action"] = PREFISSO_WB.sub("", f["action"])

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

    out = str(soup)
    out = PREFISSO_WB.sub("", out)
    out = PREFISSO_WB_JSON.sub("", out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("sorgente")
    ap.add_argument("destinazione")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--mappa", default="tools/asset-map.json")
    args = ap.parse_args(argv)

    mappa = json.loads(Path(args.mappa).read_text(encoding="utf-8"))
    html = Path(args.sorgente).read_text(encoding="utf-8", errors="replace")
    Path(args.destinazione).write_text(pulisci(html, mappa, args.slug), encoding="utf-8")
    print(f"scritto {args.destinazione}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
