# Sito statico Futuraform — design

Data: 2026-11-20

## Intento e perché

Il sito di Futuraform SRL (`futuraform.it`) non è più online: il dominio
risponde con un certificato non valido. Restano cinque pagine italiane
salvate dall'Internet Archive, in `Sito-FuturaForm/`, nel formato
"pagina web completa" del browser.

Lo scopo è ricostruire da quei salvataggi un sito statico vero —
HTML, CSS e JS — navigabile in locale e pubblicabile su GitHub Pages,
**visivamente indistinguibile dall'originale**, ma con un codice
sorgente pulito al posto dell'output grezzo di Joomla più l'iniezione
della toolbar Wayback.

## Obiettivi

1. Le cinque pagine salvate, navigabili tra loro con link relativi:
   Home, Chi siamo, I nostri servizi, I nostri lavori, Contatti.
2. Resa visiva identica all'originale su desktop, tablet e mobile, al
   netto delle quattro differenze volute elencate sotto.
3. Codice leggibile e manutenibile: asset condivisi invece di cinque
   copie, un bundle CSS invece di ventuno file, niente JS morto,
   `<head>` scritto a mano.
4. Pubblicabile su GitHub Pages senza alcun passo di build: si committa
   e si serve.

### Le quattro differenze volute

- Toolbar e iniezione Wayback rimosse.
- Voci di menu e footer che puntano a pagine mai salvate (Blog, Cookie
  Policy, Codice etico, switch lingua EN) **rimosse**, non disattivate.
- Lightbox del portfolio rimossa: le immagini ad alta risoluzione non
  sono nei salvataggi. Resta il solo effetto hover sulle card.
- Form contatti sostituito da una card con link `mailto:`, **su tutte e
  cinque le pagine**: la stessa sezione form compare sopra il footer
  ovunque, non solo in Contatti.
- Banner cookie iubenda assente: senza tracciamento non serve più.

## Non obiettivi

- Le pagine non salvate: blog e suoi tre articoli, cookie policy,
  codice etico, le sei schede portfolio, l'intera versione inglese.
- Qualunque funzionalità lato server. Il form non viene fatto
  funzionare, viene sostituito.
- Redesign, ritocchi al layout, miglioramenti al responsive, interventi
  SEO o di performance che vadano oltre quelli che derivano dalla
  pulizia.
- Un sistema di template o di build. Cinque file HTML che condividono
  header e footer per copia, non per inclusione.

## Anti obiettivi

Cose che renderebbero questo lavoro fallito anche se "funziona":

- Differenze visive percepibili rispetto all'originale.
- Link che restano nel sito senza portare da nessuna parte.
- Una toolchain da installare per rigenerare o modificare il sito.
- Pulizia fatta a occhio, senza verificare che non abbia rotto nulla.

## Vincoli

- L'unica fonte sono i cinque salvataggi. Il sito originale non è
  raggiungibile e non si può confrontare con il vivo.
- Il sito è un Joomla 4 con template Helix Ultimate e SP Page Builder:
  markup generato, classi tipo `sppb-addon-1744014013739`, ventuno
  fogli CSS più una quarantina di blocchi `<style>` inline per pagina,
  trentanove script.
- I font Poppins non sono nei salvataggi: i `.woff2` puntavano a
  `gstatic.com` attraverso archive.org. Vanno ripresi da Google Fonts.
- Manca la favicon. Si usa `Logo-quadrato.png` (400×400), già presente
  nella cartella e non referenziato da nessuna pagina.
- Nessun accesso di rete oltre a Google Fonts. Quello che manca nei
  salvataggi si ricostruisce, non si riscarica dall'archivio.
- GitHub Pages serve file statici e basta.

## Approcci considerati

**1. Pulizia chirurgica.** Tenere markup e CSS esattamente come sono,
togliere solo l'iniezione Wayback, deduplicare le cartelle `_files`,
riscrivere i link. Risultato garantito identico, lavoro breve, ma resta
tutto il peso Joomla: due copie di Bootstrap, CSS della lightbox
rimossa, script mai eseguiti.

**2. Pulizia più riordino — scelto.** Come sopra, più: un bundle CSS,
rimozione del JS morto, `<head>` riscritto, font self-hosted o da CDN,
nomi file leggibili. La fedeltà non si promette, si verifica: screenshot
a confronto prima/dopo su tre larghezze per ogni pagina.

**3. Riscrittura da zero** con HTML semantico e CSS proprio. Scartato:
con un layout prodotto da un page builder la resa pixel-identica
diventa molto difficile da garantire, e va contro il requisito
principale.

Scelta del committente: approccio 2, font ripresi da Google Fonts,
lightbox rimosso lasciando il solo hover, link morti rimossi.

## Struttura

```
/
├─ index.html
├─ chi-siamo.html
├─ servizi.html
├─ lavori.html
├─ contatti.html
├─ assets/
│  ├─ css/
│  │  ├─ site.css          bundle comune a tutte le pagine
│  │  └─ pages/*.css       i blocchi <style> per pagina, estratti
│  ├─ js/
│  │  └─ ...               solo gli script che servono davvero
│  ├─ img/                 immagini deduplicate dalle cinque _files
│  └─ fonts/               se si opta per il self-hosting
├─ .nojekyll
├─ .gitignore
└─ README.md
```

Nomi dei file: slug corti e leggibili invece degli originali Joomla
(`digital-marketing-i-nostri-servizi` diventa `servizi.html`). È una
mia scelta, non una richiesta: il sito originale è offline, quindi non
c'è continuità di URL da preservare. Facile da cambiare se si preferisce
tenere gli slug storici.

La cartella sorgente `Sito-FuturaForm/` resta sul disco come
riferimento ma viene esclusa dal repo con `.gitignore`: non ha motivo
di finire pubblicata su Pages. Anche questa è una mia scelta.

## Come si costruisce

### CSS

I ventuno fogli vanno concatenati **nell'ordine originale** — l'ordine
è semantico, la cascata dipende da quello — dopo aver tolto quelli che
non servono più:

- `banner-styles.css`, `iconochive.css`: sono della toolbar Wayback.
- `magnific-popup.css`, `featherlight.min.css`: sono della lightbox che
  viene rimossa.
- `joomla-alert.min.css`, `system-j4.min.css`: interfaccia
  amministrativa di Joomla, mai usata nel front end.
- `bootstrap(1).min.css`: verificare se è davvero un duplicato di
  `bootstrap.min.css` prima di toglierlo.
- `fa-v4-shims.css`: serve se il markup usa ancora i nomi icona Font
  Awesome v4. Da verificare, non da assumere.

I blocchi `<style>` inline sono specifici di pagina e pieni di ID
generati: vanno estratti in `assets/css/pages/<pagina>.css`, caricato
dopo `site.css`, mantenendo l'ordine.

I font: i file `css` e `css(1)` sono CSS di Google Fonts con URL
riscritti su archive.org. Vanno sostituiti con un `<link>` a
`fonts.googleapis.com`, verificando prima quali famiglie e quali pesi
sono effettivamente usati.

Rinominare le classi generate è esplicitamente permesso dal committente,
ma non è un obiettivo: va fatto solo dove è sicuro e dove migliora
qualcosa. Gli ID `sppb-addon-*` sono il collante tra i blocchi `<style>`
inline e il markup, quindi rinominarli significa toccarli in due posti
insieme.

### JS

Da rimuovere: tutto il blocco Wayback (`bundle-playback`, `wombat`,
`ruffle`, `athena`, `core-it`), il cookie banner iubenda (`1717384`,
`69940543`, `iubenda_cs`), il core Joomla non usato nel front end
(`core.min`, `keepalive`, `messages`, `showon` e le loro varianti es5),
gli script della lightbox (`magnific-popup`, `featherlight`), e i
moduli Bootstrap caricati singolarmente dove è già presente
`bootstrap.bundle.min`.

Candidati a restare: jQuery, `bootstrap.bundle.min`, `sppagebuilder`,
`jquery.parallax`, `spsimpleportfolio` con `jquery.shuffle.modernizr`
per il filtro della griglia, `sp_carousel`, `main`, `script.min`.

Ogni singola rimozione va verificata, non dedotta dal nome.

### HTML

Per ogni pagina: via il blocco Wayback dall'`<head>` e la toolbar dal
`<body>` (`#wm-ipp-base`, `#wm-ipp-print`), via gli attributi
`data-cmp-*` iniettati dal consent manager, via le classi e lo
`style="--wm-toolbar-height"` messi sull'elemento `<html>`.

`<head>` riscritto a mano: charset, viewport, title e description presi
dall'originale, favicon recuperata, canonical rimosso.

`lang="it"` al posto di `lang="en"`: l'originale aveva l'attributo
sbagliato e il contenuto è italiano. Correzione mia, invisibile, utile
agli screen reader.

Tutti gli `href` e `src` riscritti in relativi. Via le voci Blog,
Cookie Policy, Codice etico e lo switch EN da menu e footer. I link
esterni — Facebook, LinkedIn, la privacy policy su iubenda — restano
come sono.

Portfolio: tolto l'elemento `<a>` che apriva la lightbox, mantenendo
intatto il resto del markup della card perché l'effetto hover è già
tutto in CSS e non deve cambiare.

#### La card contatti

Il form `#userForm` compare in tutte e cinque le pagine, nella stessa
sezione sopra il footer. Va sostituito in tutte e cinque.

La card **conserva l'altezza che aveva il form**: la colonna che la
contiene detta l'altezza della sezione, quindi una card più bassa
alzerebbe il footer e scentrerebbe la colonna di fianco su ogni pagina.
Si misura l'altezza resa del form e la si impone alla card, verificando
che a 390 pixel, dove le colonne si impilano, il risultato regga.

Contenuto: i recapiti già presenti nella pagina — email, telefono,
indirizzo — e un pulsante `mailto:` con lo stile del pulsante di invio
originale.

## Scelte fatte da chi ha scritto il documento

Non richieste dal committente, prese per andare avanti. Tutte
reversibili.

**Titoli del portfolio.** Oltre alla lightbox, il titolo di ogni card
punta a una delle sei schede mai salvate. Si toglie l'ancora
mantenendo il titolo e il suo aspetto: le classi che lo stilano si
spostano sull'elemento rimasto, e l'overlay si verifica a hover.

**Switch lingua.** Si rimuove la sola voce EN, lasciando l'indicatore
IT. Togliere l'intero modulo libererebbe la `col-1` dell'header e
farebbe riflusso sul desktop: una differenza visibile non richiesta.
Stesso trattamento nel menu mobile.

**Banner cookie.** La sua assenza è una differenza voluta in più.
Nelle schermate di riferimento si nasconde come si nasconde la toolbar
Wayback. Il pulsante "preferenze cookie" rimasto nel markup, che senza
il suo script non fa nulla, si rimuove.

**Classi Modernizr.** Sull'elemento `<html>` della Home ci sono `js
csstransforms csstransforms3d csstransitions`: sono di Modernizr, non
di Wayback, e si conservano.

**Nomi file con spazi.** Tre immagini hanno spazi nel nome. Si
rinominano con trattini.

**Voce Home del menu.** Nell'originale è vuota e la Home si raggiunge
dal logo. Si lascia com'è: aggiungere una voce sarebbe una differenza
visibile non richiesta.

## Verifica

Non ci si fida dell'occhio. Per ogni pagina, con Playwright:

- Screenshot full page della versione originale, con toolbar Wayback e
  banner cookie nascosti via CSS, e della versione nuova.
- **A 1440 pixel il confronto è diretto.** I salvataggi sono dump del
  DOM dopo l'esecuzione del JS: la griglia del portfolio ha dentro gli
  stili inline calcolati da Shuffle (`height: 705.532px`,
  `translate3d(635px, 0px, 0px)`) alla larghezza di cattura. Quella
  larghezza è il riferimento attendibile.
- **A 768 e 390 pixel il confronto con l'originale non è attendibile**,
  perché riaprire quel file stretto non riproduce ciò che faceva il
  sito vivo. Lì si verifica che la versione nuova si comporti bene da
  sola: niente overflow orizzontale, colonne impilate come previsto,
  menu mobile funzionante, card contatti leggibile.
- Console del browser a zero errori sulla versione nuova.
- Tutti i link interni verificati: nessuno che punti nel vuoto.

Il sito si considera finito quando le uniche differenze sono le quattro
volute.

## Lasciato a chi implementa

- Quali CSS e JS sopravvivono davvero alla potatura: la lista sopra è
  un punto di partenza da verificare file per file.
- Il markup preciso della card contatti.
- Quanto spingersi nella rinomina delle classi generate, dove è sicuro.
- Contenuto di README e `.gitignore`, e l'inizializzazione del repo git.
