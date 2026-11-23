# Sito Futuraform

Ricostruzione statica del sito di Futuraform SRL, che non è più online: il
dominio `futuraform.it` risponde con un certificato non valido. Il sito
nasce da cinque pagine italiane salvate dall'Internet Archive e si serve
senza alcun passo di build — si clona e si pubblica.

## Le pagine

| File | Pagina |
|---|---|
| `index.html` | Home |
| `chi-siamo.html` | Chi siamo |
| `servizi.html` | I nostri servizi |
| `lavori.html` | I nostri lavori |
| `contatti.html` | Contatti |

## In che cosa differisce dall'originale

Sono le uniche differenze volute. Tutto il resto è identico al pixel
rispetto all'originale archiviato, su desktop.

1. **Toolbar dell'Internet Archive**: rimossa, con tutti i suoi script.
2. **Pagine mai salvate**: blog, cookie policy, codice etico, le sei
   schede di portfolio e l'intera versione inglese non esistono nei
   salvataggi. Le voci che ci puntavano sono state tolte da menu e
   footer; nella sezione blog della home restano i titoli come testo.
3. **Lightbox del portfolio**: rimossa, perché le immagini ad alta
   risoluzione non sono nei salvataggi. Resta l'effetto hover.
4. **Form di contatto**: sostituito in tutte e cinque le pagine da una
   card con i recapiti e un link `mailto:`. Non c'è più un backend a cui
   inviare.
5. **Banner cookie**: rimosso insieme al consent manager, visto che il
   sito non traccia più nulla.

## Servire in locale

```bash
python3 -m http.server
```

Poi `http://localhost:8000/`. Serve un server HTTP vero: aprendo i file
con `file://` il browser blocca alcuni script per via del CORS e il menu
mobile non si apre.

## Pubblicare su GitHub Pages

Impostazioni del repository → Pages → Source: *Deploy from a branch*,
branch `main`, cartella `/ (root)`. Il file `.nojekyll` impedisce a
Jekyll di ignorare le cartelle che iniziano con l'underscore.

Tutti i percorsi sono relativi, quindi il sito funziona anche servito da
una sottocartella come `https://utente.github.io/futuraform/`.

L'unica richiesta verso l'esterno è il foglio dei font su
`fonts.googleapis.com`; se non arriva, il testo cade su un sans di
sistema. Tutto il resto sta nel repository.

## Com'è fatto

```
index.html, chi-siamo.html, …   le cinque pagine
assets/css/site.css             i dieci fogli del tema concatenati
assets/css/pages/<pagina>.css   i blocchi <style> estratti, uno per pagina
assets/css/card-contatti.css    la card che sostituisce il form
assets/js/                      i dieci script rimasti su trentaquattro
assets/img/                     le immagini, deduplicate
```

Il markup è quello generato da Joomla 4 con Helix Ultimate e SP Page
Builder, ripulito: niente più iniezione Wayback, un bundle CSS al posto
di ventuno fogli, e solo gli script che servono davvero. Le due icone
usate dal menu mobile sono SVG inline, perché i font delle icone non
erano nei salvataggi.

## Rigenerare e verificare

Il sito non si modifica a mano: si rigenera dai salvataggi, che stanno in
`Sito-FuturaForm/` e non sono versionati.

```bash
python3 tools/build.py                              # ricostruisce tutto
python3 -m unittest discover -s tools -p 'test_*.py' # la suite completa
```

La suite controlla la trasformazione, le proprietà che il sito deve
mantenere (percorsi relativi, nessun link morto, fallback dei font) e i
comportamenti che uno screenshot non coglie: menu mobile, carosello,
griglia del portfolio, card contatti.

Per confrontare una pagina con l'originale archiviato:

```bash
python3 tools/shoot.py "Sito-FuturaForm/Home-Page.html" riferimento.png --width 1440 --fonts
python3 tools/shoot.py index.html nuova.png --width 1440
python3 tools/compare.py riferimento.png nuova.png
```

L'opzione `--fonts` serve solo sugli originali: i loro `@font-face`
puntano i woff2 su archive.org e non risolvono, quindi senza quella
opzione il confronto misurerebbe il font invece delle modifiche. Gli
screenshot di riferimento già pronti stanno in `baseline/`.
