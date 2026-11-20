# Sito statico Futuraform — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trasformare i cinque salvataggi Wayback in `Sito-FuturaForm/` in un sito statico pulito di cinque pagine, visivamente identico all'originale, pubblicabile su GitHub Pages senza passi di build.

**Architecture:** Si lavora per sottrazione verificata. Prima si fissano le schermate di riferimento dell'originale, poi si pulisce un pezzo alla volta — iniezione Wayback, asset duplicati, CSS, JS, lightbox, form — e dopo ogni pezzo si riconfronta con il riferimento. Niente viene rimosso perché "sembra inutile": viene rimosso e poi dimostrato innocuo.

**Tech Stack:** HTML, CSS, JS serviti staticamente. jQuery, Bootstrap 5, SP Page Builder e SP Simple Portfolio restano come erano. Poppins da Google Fonts. Python 3 con Playwright e Pillow solo come strumenti di verifica, mai come dipendenze del sito.

**Spec:** `docs/superpowers/specs/2026-11-20-sito-statico-futuraform-design.md`

## Global Constraints

- Nessun passo di build. Il repo si clona e si serve così com'è.
- Nessun accesso di rete se non a `fonts.googleapis.com` e `fonts.gstatic.com`.
- Ogni `href` e `src` interno è **relativo**, mai assoluto con `/` iniziale: GitHub Pages serve da `https://<utente>.github.io/<repo>/`.
- L'ordine di caricamento dei CSS non cambia mai: la cascata dipende da quello.
- Le uniche differenze ammesse rispetto all'originale sono le cinque dello spec: toolbar Wayback, link a pagine mai salvate, lightbox portfolio, form contatti, banner cookie.
- Font: `Poppins`, pesi 200, 300, 400, 500, 600, 700, 800, 900.
- Recapiti della card contatti: `info@futuraform.it`, Milano `02.61868229`, `Via Bisceglie 89/91 - 20152 Milano`, `Via di Casalotti 53 - 00166 Roma`. Da riconfermare sulla pagina originale al momento di scriverla.
- Nomi dei file pubblicati tutti minuscoli, con trattini, senza spazi.

## Review Focus

Cinque modi di rompersi che nessuna verifica di task tocca di suo. Ogni riga ha il suo controllo assegnato a un task.

1. **Path assoluti.** Un `/assets/...` funziona in locale e dà 404 su GitHub Pages, che serve da una sottocartella. → Task 10.
2. **Maiuscole nei nomi file.** macOS non distingue `Logo.png` da `logo.png`, GitHub Pages sì: un riferimento sbagliato passa tutte le prove locali e rompe solo online. → Task 2.
3. **Google Fonts irraggiungibile.** Senza rete il `font-family` deve degradare a `sans-serif`, non al serif di default del browser. → Task 2.
4. **Menu mobile.** L'offcanvas dipende dal JS di Bootstrap: se la potatura toglie il bundle sbagliato il menu non si apre più, e negli screenshot desktop non si vede. → Task 6.
5. **Card contatti a 390 px.** Con un'altezza imposta uguale a quella del form, il testo può traboccare dal contenitore sugli schermi stretti. → Task 8.

---

### Task 1: Repo, strumenti di verifica e schermate di riferimento

**Files:**
- Create: `/Users/mizunhi/mizu-repos/futuraform/.gitignore`
- Create: `tools/shoot.py`
- Create: `tools/compare.py`
- Create: `baseline/` (immagini di riferimento, versionate)

**Interfaces:**
- Produces: `tools/shoot.py <pagina.html> <out.png> --width N` che apre un file locale in Chromium headless, aspetta il `networkidle`, inietta il CSS di soppressione e salva uno screenshot full page. `tools/compare.py <a.png> <b.png>` che stampa la percentuale di pixel diversi e salva una maschera delle differenze; esce con codice 0 se la differenza è zero, 1 altrimenti.
- Produces: `baseline/orig-<slug>-1440.png` per i cinque slug `index`, `chi-siamo`, `servizi`, `lavori`, `contatti`.

- [ ] **Step 1: Inizializzare il repo e il `.gitignore`**

`git init` nella cartella di progetto. Il `.gitignore` esclude `.DS_Store`, `Sito-FuturaForm/` (resta in locale come riferimento, non va pubblicata) e `__pycache__/`.

- [ ] **Step 2: Installare gli strumenti di verifica**

`pip install playwright pillow` e `playwright install chromium`. Se l'installazione non è possibile nell'ambiente, fermarsi e dirlo: senza confronto automatico questo piano non ha una condizione di successo.

- [ ] **Step 3: Scrivere `tools/shoot.py`**

Il CSS di soppressione, iniettato prima dello screenshot, nasconde la toolbar Wayback e il banner cookie e azzera l'offset che la toolbar impone:

```css
#wm-ipp-base, #wm-ipp-print, #wm-ipp, .iubenda-cs-container,
#iubenda-cs-banner, .iubenda-tp-btn { display: none !important; }
html { --wm-toolbar-height: 0px !important; }
body { margin-top: 0 !important; }
```

- [ ] **Step 4: Scrivere `tools/compare.py`**

Confronto pixel a pixel con Pillow. Se le due immagini hanno altezze diverse, lo dice esplicitamente invece di confrontare solo la parte comune: un'altezza diversa è già una differenza.

- [ ] **Step 5: Catturare le cinque schermate di riferimento a 1440 px**

Sorgenti: i cinque file in `Sito-FuturaForm/`. Destinazione: `baseline/orig-<slug>-1440.png`.

- [ ] **Step 6: Verificare che il riferimento sia pulito**

Aprire le cinque immagini e controllare a occhio che non ci sia traccia di toolbar Wayback né di banner cookie, e che la pagina sia resa per intero. Se un `networkidle` non arriva perché uno script Wayback resta appeso, usare un'attesa a tempo fisso e annotarlo.

- [ ] **Step 7: Commit**

```bash
git add .gitignore tools/ baseline/
git commit -m "chore: strumenti di verifica e schermate di riferimento"
```

---

### Task 2: Asset condivisi — immagini, favicon, font

**Files:**
- Create: `assets/img/` (immagini deduplicate dalle cinque `_files/`)
- Create: `assets/img/favicon.png` (da `Sito-FuturaForm/Logo-quadrato.png`)

**Interfaces:**
- Produces: una mappa `vecchio nome → assets/img/<nome>` che i Task 3 e 4 usano per riscrivere i `src`. Salvarla in `tools/asset-map.json`.

- [ ] **Step 1: Verificare che i file omonimi siano davvero identici**

Confrontare gli hash dei file con lo stesso nome nelle cinque cartelle `_files/`. Per le immagini ci si aspetta identità piena. Per i CSS ci si aspetta che differiscano **solo** nel commento Wayback in testa: se un file differisce nel corpo, va tenuto separato e la cosa va segnalata.

- [ ] **Step 2: Copiare le immagini in `assets/img/` normalizzando i nomi**

Tutto minuscolo, spazi e `%20` in trattini. I tre con spazi sono `digital marketing_900x500.jpg`, `Accademia tiktok_900x500.jpg`, `passione grecia_900x500.jpg`. Scrivere la mappa in `tools/asset-map.json`.

- [ ] **Step 3: Copiare `Logo-quadrato.png` in `assets/img/favicon.png`**

- [ ] **Step 4: Controllo maiuscole (Review Focus 2)**

Verificare che nessun nome in `assets/` contenga maiuscole, spazi o caratteri percento:

Run: `find assets -name '*[A-Z ]*' -o -name '*%*'`
Expected: nessun risultato.

- [ ] **Step 5: Determinare la dichiarazione dei font**

Dai file `Home-Page_files/css` e `css(1)` risulta la sola famiglia Poppins. I pesi usati nel sito sono 200, 300, 400, 500, 600, 700, 800, 900. Verificare se compaiono corsivi (`font-style: italic` nel markup o nei CSS del tema) e includerli solo se usati. La dichiarazione è un `<link>` a `fonts.googleapis.com` con `display=swap`, che i Task 3 e 4 mettono nel `<head>`.

- [ ] **Step 6: Fallback dei font (Review Focus 3)**

Verificare che ogni regola `font-family: 'Poppins'` nei CSS del tema e nei blocchi inline termini con `, sans-serif`. Dove manca, aggiungerlo: senza rete il testo deve cadere su un sans, non sul serif di default.

- [ ] **Step 7: Commit**

```bash
git add assets/ tools/asset-map.json
git commit -m "feat: asset condivisi deduplicati, favicon e font"
```

---

### Task 3: La Home pulita — il modello per le altre

**Files:**
- Create: `index.html` (da `Sito-FuturaForm/Home-Page.html`)
- Create: `assets/css/` e `assets/js/` con i file ancora **tutti** presenti, solo deduplicati

**Interfaces:**
- Produces: la procedura di pulizia che il Task 4 applica alle altre quattro pagine. Annotarla in `docs/superpowers/plans/procedura-pulizia.md` man mano che la si esegue.

Questo task tocca solo la struttura. CSS e JS restano tutti: si potano nei Task 5 e 6, così che se qualcosa si rompe si sa quale dei due passaggi l'ha rotto.

- [ ] **Step 1: Copiare CSS e JS in `assets/`**

Da una sola delle cartelle `_files/`, tolto il suffisso `.download` dai nomi degli script. Restano fuori i file della toolbar Wayback: `banner-styles.css`, `iconochive.css`, `bundle-playback.js`, `wombat.js`, `ruffle.js`, `athena.js`, `core-it.js`.

- [ ] **Step 2: Rimuovere l'iniezione Wayback da `index.html`**

Via il blocco fra `<!-- BEGIN WAYBACK TOOLBAR INSERT -->` e `<!-- END WAYBACK TOOLBAR INSERT -->` se presente, i `<script>` di `__wm.init` e `archive_analytics`, gli elementi `#wm-ipp-base` e `#wm-ipp-print`, l'attributo `style="--wm-toolbar-height: ..."` sull'elemento `<html>` e tutti gli attributi `data-cmp-ab` e `data-cmp-info`.

Le classi `js csstransforms csstransforms3d csstransitions` sull'elemento `<html>` **restano**: sono di Modernizr.

- [ ] **Step 3: Riscrivere il `<head>`**

`lang="it"` sull'elemento `<html>`. Nel `<head>`: charset, viewport, `<title>` e `<meta name="description">` presi dall'originale, il `<link>` dei font del Task 2, la favicon `assets/img/favicon.png`. Via il `<link rel="canonical">` e i `<link rel="alternate" hreflang>`. Poi i `<link>` dei CSS, **nello stesso ordine dell'originale**, puntati a `assets/css/`.

- [ ] **Step 4: Riscrivere tutti i riferimenti interni**

I `src` delle immagini secondo `tools/asset-map.json`. Gli `href` di navigazione verso gli slug nuovi: `index.html`, `chi-siamo.html`, `servizi.html`, `lavori.html`, `contatti.html`. Gli ancoraggi della pagina servizi diventano `servizi.html#sviluppo_web` e simili. Gli `href="...#"`, `#close`, `#expand` restano ancoraggi puri (`#`, `#close`, `#expand`): sono comandi di interfaccia, non navigazione.

I link esterni — Facebook, LinkedIn, privacy policy iubenda — vanno ripuliti del prefisso `web.archive.org/web/<timestamp>/` e lasciati puntare al loro vero indirizzo.

- [ ] **Step 5: Catturare e confrontare**

Run: `python tools/shoot.py index.html /tmp/new-index-1440.png --width 1440 && python tools/compare.py baseline/orig-index-1440.png /tmp/new-index-1440.png`
Expected: differenza zero. Il banner cookie è ancora presente in entrambe le versioni a questo punto, quindi non introduce scarti.

- [ ] **Step 6: Console pulita**

Verificare che la console non riporti errori né 404. Un 404 qui significa un riferimento sfuggito allo Step 4.

- [ ] **Step 7: Commit**

```bash
git add index.html assets/ docs/
git commit -m "feat: home page ripulita dall'iniezione Wayback"
```

---

### Task 4: Le altre quattro pagine

**Files:**
- Create: `chi-siamo.html`, `servizi.html`, `lavori.html`, `contatti.html`

**Interfaces:**
- Consumes: la procedura del Task 3.

- [ ] **Step 1: Applicare la procedura del Task 3 a ciascuna delle quattro pagine**

Sorgenti: `Chi siamo.html`, `I nostri-servizi.html`, `I nostri lavori.html`, `Contatti.html`.

- [ ] **Step 2: Verificare i CSS e JS aggiuntivi**

La Home carica 23 CSS e 39 JS, le altre 21 e 35. Confrontare le liste: se una pagina riferisce un file non ancora in `assets/`, copiarlo.

- [ ] **Step 3: Catturare e confrontare le quattro pagine a 1440 px**

Expected: differenza zero su tutte e quattro.

- [ ] **Step 4: Console pulita su tutte e quattro**

- [ ] **Step 5: Commit**

```bash
git add *.html assets/
git commit -m "feat: le restanti quattro pagine ripulite"
```

---

### Task 5: Potatura CSS e bundle

**Files:**
- Create: `assets/css/site.css` (bundle comune)
- Create: `assets/css/pages/<slug>.css` (i blocchi `<style>` estratti, uno per pagina)
- Modify: i cinque HTML

- [ ] **Step 1: Stabilire quali fogli restano**

Candidati alla rimozione, ciascuno da verificare e non da dare per scontato:

| File | Motivo | Come si verifica |
|---|---|---|
| `magnific-popup.css`, `featherlight.min.css` | la lightbox sparisce nel Task 7 | rimuovere nel Task 7, non qui |
| `joomla-alert.min.css`, `system-j4.min.css` | interfaccia amministrativa | cercare nel markup le classi che definiscono |
| `bootstrap(1).min.css` | sospetto duplicato | confrontarlo con `bootstrap.min.css` |
| `fa-v4-shims.css` | serve solo con i nomi icona v4 | cercare nel markup classi `fa fa-` senza prefisso `fas`/`far`/`fab` |

- [ ] **Step 2: Rimuovere un foglio alla volta, riconfrontando ogni volta**

Dopo ogni singola rimozione, catturare le cinque pagine e confrontarle. Appena una differenza compare, quel foglio torna dentro e si annota perché.

- [ ] **Step 3: Concatenare i superstiti in `assets/css/site.css`**

Nell'ordine originale esatto, ognuno preceduto da un commento con il nome di provenienza.

- [ ] **Step 4: Estrarre i blocchi `<style>` inline**

Circa quaranta per pagina, pieni di ID generati, specifici della pagina. Vanno in `assets/css/pages/<slug>.css`, caricato dopo `site.css`, mantenendo l'ordine fra loro.

- [ ] **Step 5: Confronto finale sulle cinque pagine**

Expected: differenza zero.

- [ ] **Step 6: Commit**

```bash
git add assets/css/ *.html
git commit -m "refactor: un bundle CSS al posto di ventuno fogli"
```

---

### Task 6: Potatura JS

**Files:**
- Modify: i cinque HTML
- Delete: gli script rimossi da `assets/js/`

- [ ] **Step 1: Rimuovere il blocco consent e il core Joomla non usato**

Via `1717384.js`, `69940543.js`, `iubenda_cs.js` — con loro sparisce il banner cookie, che è una differenza voluta. Via `core.min.js`, `keepalive*.js`, `messages*.js`, `showon*.js`.

- [ ] **Step 2: Risolvere il doppio caricamento di Bootstrap**

Le pagine caricano sia i moduli singoli (`alert`, `button`, `carousel`, `collapse`, `dropdown`, `modal`, `offcanvas`, `popover`, `scrollspy`, `tab`, `toast`, più le varianti `-es5`) sia `bootstrap.bundle.min.js`. Tenere il solo bundle.

- [ ] **Step 3: Verificare il menu mobile (Review Focus 4)**

Con Playwright a 390 px: cliccare il pulsante dell'offcanvas, verificare che il pannello si apra, che contenga le voci di menu e che il pulsante di chiusura lo richiuda. Questo controllo non si vede negli screenshot desktop ed è il modo più probabile in cui questo task rompe qualcosa.

- [ ] **Step 4: Verificare gli altri comportamenti JS**

Carosello che scorre, filtro della griglia portfolio, parallasse allo scroll, effetti di comparsa `animate.css`. Ciascuno a 1440 px.

- [ ] **Step 5: Rimuovere il pulsante preferenze cookie orfano**

Il `<button class="iubenda-tp-btn iubenda-cs-preferences...">` resta nel markup di tutte le pagine e senza il suo script non fa nulla. Via da tutte e cinque.

- [ ] **Step 6: Confronto sulle cinque pagine**

Expected: l'unica differenza rispetto al riferimento è dove stava il banner cookie, che nel riferimento era già soppresso dal CSS dello Step 3 del Task 1 — quindi anche qui differenza zero.

- [ ] **Step 7: Commit**

```bash
git add assets/js/ *.html
git commit -m "refactor: rimosso il JS morto, banner cookie incluso"
```

---

### Task 7: Portfolio — via la lightbox, via i link alle schede

**Files:**
- Modify: `index.html`, `lavori.html`

- [ ] **Step 1: Rimuovere l'ancora della lightbox**

L'elemento `<a class="btn-zoom" data-featherlight="image">` in ogni card. Il resto del markup della card resta intatto: l'effetto hover è tutto in CSS e non deve cambiare.

- [ ] **Step 2: Scollegare i titoli delle card**

Sei occorrenze sulla Home, dentro `<h3 class="sp-simpleportfolio-title">`, che puntano alle schede `component/spsimpleportfolio/item/...` mai salvate. Togliere l'ancora conservando il testo. Se le regole di stile dell'overlay agganciano l'elemento `a`, spostare le classi sull'elemento che resta perché colore e peso non cambino.

- [ ] **Step 3: Rimuovere `magnific-popup.css`, `featherlight.min.css`, i rispettivi JS e `jquery.magnific-popup.min.js`**

- [ ] **Step 4: Verificare l'hover**

Con Playwright, portare il puntatore su ogni card delle due pagine e catturare lo stato hover. Confrontare con lo stesso stato catturato dall'originale. Expected: differenza zero; il puntatore non deve più diventare una lente né aprire nulla al clic.

- [ ] **Step 5: Confronto a riposo sulle due pagine**

Expected: differenza zero.

- [ ] **Step 6: Commit**

```bash
git add index.html lavori.html assets/
git commit -m "feat: portfolio senza lightbox, solo hover"
```

---

### Task 8: La card contatti al posto del form

**Files:**
- Modify: tutti e cinque gli HTML
- Modify: `assets/css/site.css`

- [ ] **Step 1: Misurare l'altezza resa del form**

Con Playwright, l'altezza di `#userForm` e quella della colonna che lo contiene, a 1440, 768 e 390 px. Sono i valori che la card deve riprodurre.

- [ ] **Step 2: Scrivere la card**

Dentro lo stesso contenitore del form, con i recapiti della pagina Contatti — `info@futuraform.it`, telefono e le due sedi — e un pulsante `mailto:info@futuraform.it` con le stesse classi del pulsante di invio originale, così da ereditarne lo stile.

L'altezza si impone con `min-height` sul contenitore della card, ai valori dello Step 1, con un `min-height` diverso per ciascuna delle tre soglie.

- [ ] **Step 3: Sostituire il form in tutte e cinque le pagine**

- [ ] **Step 4: Verificare che nulla si sia spostato**

Expected: sulle cinque pagine, l'unica regione diversa dal riferimento è quella interna al form. Tutto ciò che sta sotto — footer compreso alla stessa altezza — e la colonna di fianco restano dove erano.

- [ ] **Step 5: Traboccamento a 390 px (Review Focus 5)**

Verificare che a 390 px il testo della card stia dentro il contenitore, che il pulsante sia cliccabile e che non si crei scorrimento orizzontale. Se il contenuto supera il `min-height`, la card cresce invece di traboccare.

- [ ] **Step 6: Il link `mailto:` funziona**

Verificare che l'`href` sia esattamente `mailto:info@futuraform.it` e che nessuno script lo intercetti.

- [ ] **Step 7: Commit**

```bash
git add *.html assets/css/
git commit -m "feat: card contatti con mailto al posto del form"
```

---

### Task 9: Via i link a pagine mai salvate

**Files:**
- Modify: tutti e cinque gli HTML

- [ ] **Step 1: Rimuovere la voce Blog dal megamenu e dal menu mobile**

- [ ] **Step 2: Rimuovere Cookie Policy e Codice etico dal footer**

La voce Privacy policy resta: punta a iubenda, è esterna e funziona.

- [ ] **Step 3: Rimuovere la sola voce EN dal selettore lingua**

Resta l'indicatore IT e resta la `col-1` che lo contiene, così la griglia dell'header non riflussa. Stesso trattamento nel menu mobile, dove c'è una coppia IT/EN in `lang-inline`.

- [ ] **Step 4: Lasciare com'è la voce Home vuota**

Il primo `<li class="sp-menu-item">` del menu è vuoto in tutte le pagine: nell'originale la Home si raggiunge dal logo. Non va né riempito né rimosso — sarebbe una differenza visibile non richiesta.

- [ ] **Step 5: Verificare che non resti nessun riferimento al dominio morto**

Run: `grep -rn 'futuraform\.it/it/\|futuraform\.it/en/\|web\.archive\.org' *.html assets/`
Expected: nessun risultato nei file HTML. Nei CSS può restare qualche commento, che va ripulito.

- [ ] **Step 6: Confronto sulle cinque pagine**

Expected: l'unica differenza è dove stavano le voci rimosse. Verificare che il menu non sia riflussato e che il footer non si sia accorciato in modo da spostare altro.

- [ ] **Step 7: Commit**

```bash
git add *.html assets/
git commit -m "feat: rimosse le voci verso pagine mai salvate"
```

---

### Task 10: Verifica finale e pubblicazione

**Files:**
- Create: `README.md`, `.nojekyll`

- [ ] **Step 1: Nessun path assoluto (Review Focus 1)**

Run: `grep -rnE '(href|src)="/[^/]' *.html assets/css/*.css`
Expected: nessun risultato. Un path con `/` iniziale dà 404 su GitHub Pages, che serve da una sottocartella.

- [ ] **Step 2: Tutti i link interni portano da qualche parte**

Con Playwright, visitare le cinque pagine, raccogliere ogni `href` interno e verificare che il file esista e che l'ancoraggio esista nella pagina di destinazione.

- [ ] **Step 3: Nessun 404 sugli asset**

Con Playwright, intercettare le richieste di rete sulle cinque pagine. Expected: nessuna risposta di errore. Le sole richieste verso l'esterno sono a `fonts.googleapis.com` e `fonts.gstatic.com`.

- [ ] **Step 4: Confronto completo**

Le cinque pagine a 1440 px contro il riferimento. Expected: differenze solo nella regione del form e dove stavano le voci rimosse.

- [ ] **Step 5: Tenuta a 768 e 390 px**

Qui non si confronta con l'originale: i salvataggi hanno dentro misure calcolate dal JS alla larghezza di cattura, quindi la baseline stretta non è attendibile. Si verifica che il nuovo stia in piedi da solo — niente scorrimento orizzontale, colonne impilate, menu mobile che si apre, card contatti leggibile, immagini che non escono dal contenitore.

- [ ] **Step 6: Scrivere `README.md` e `.nojekyll`**

Il README dice cos'è il sito, da dove viene, le cinque differenze volute rispetto all'originale, come servirlo in locale (`python -m http.server`) e come attivare GitHub Pages. Il `.nojekyll` impedisce a Jekyll di ignorare file e cartelle che iniziano con l'underscore.

- [ ] **Step 7: Prova da server locale**

`python -m http.server` nella radice, poi le cinque pagine da `http://localhost:8000/`. Expected: tutto come da `file://`, console pulita.

- [ ] **Step 8: Commit**

```bash
git add README.md .nojekyll
git commit -m "docs: README e configurazione per GitHub Pages"
```
