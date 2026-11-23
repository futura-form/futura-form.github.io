# Sito Futuraform

Ricostruzione statica del sito di Futuraform SRL, che non è più online: il
dominio `futuraform.it` risponde con un certificato non valido. Il sito
nasce da cinque pagine italiane salvate dall'Internet Archive e si serve
senza alcun passo di build — si clona e si pubblica.

## La cartella da pubblicare

`build/` contiene esattamente il sito e nient'altro: cinque pagine, gli
asset, e un `.nojekyll`. È quella che va online, ed è versionata perché
i salvataggi da cui nasce non stanno nel repository. Tutto il resto —
`tools/`, `baseline/`, `docs/` — serve a produrla e verificarla, e non
viene pubblicato.

```
build/
├─ index.html
├─ chi-siamo.html · servizi.html · lavori.html · contatti.html
├─ .nojekyll
└─ assets/
   ├─ css/site.css              i dieci fogli del tema concatenati
   ├─ css/pages/<pagina>.css    i blocchi <style> estratti, uno per pagina
   ├─ css/card-contatti.css     la card che sostituisce il form
   ├─ js/                       i nove script rimasti su trentaquattro
   └─ img/                      le immagini, deduplicate
```

## Le pagine

| File | Pagina |
|---|---|
| `index.html` | Home |
| `chi-siamo.html` | Chi siamo |
| `servizi.html` | I nostri servizi |
| `lavori.html` | I nostri lavori |
| `contatti.html` | Contatti |

## In che cosa differisce dall'originale

Sono le uniche differenze volute. A riposo, tutto il resto è identico al
pixel rispetto all'originale archiviato su desktop, e `tools/verify.py`
lo verifica a ogni esecuzione della suite.

1. **Toolbar dell'Internet Archive**: rimossa, con tutti i suoi script.
2. **Pagine mai salvate**: blog, cookie policy, codice etico, le sei
   schede di portfolio e l'intera versione inglese non esistono nei
   salvataggi. Le voci che ci puntavano sono state tolte da menu e
   footer; nella sezione blog della home restano i titoli come testo.
3. **Lightbox del portfolio**: rimossa, perché le immagini ad alta
   risoluzione non sono nei salvataggi. Resta l'effetto hover, con una
   conseguenza: il titolo delle card va a capo più tardi. L'overlay era
   una tabella di due celle e quella del pulsante ZOOM non c'è più,
   quindi il titolo ha più larghezza. Lo stato a riposo non cambia.
4. **Form di contatto**: sostituito in tutte e cinque le pagine da una
   card con i recapiti e un link `mailto:`. Non c'è più un backend a cui
   inviare.
5. **Banner cookie**: rimosso insieme al consent manager, visto che il
   sito non traccia più nulla.

## Servire in locale

```bash
cd build && python3 -m http.server
```

Poi `http://localhost:8000/`. Serve un server HTTP vero: aprendo i file
con `file://` il browser blocca alcuni script per via del CORS e il menu
mobile non si apre.

## Pubblicare su GitHub Pages

Impostazioni del repository → Pages → Source: **GitHub Actions**. Da lì
in poi ogni push su `main` che tocchi `build/` pubblica il sito, tramite
`.github/workflows/pages.yml`. Il workflow non costruisce niente: carica
`build/` così com'è, dopo aver controllato che contenga `index.html` e
`.nojekyll`.

Serve una Action perché Pages, nella modalità "deploy da un branch", sa
servire solo la radice del repository o `docs/`, non una cartella
arbitraria come `build/`.

Tutti i percorsi sono relativi, quindi il sito funziona anche servito da
una sottocartella come `https://utente.github.io/futuraform/`.

L'unica richiesta verso l'esterno è il foglio dei font su
`fonts.googleapis.com`; se non arriva, il testo cade su un sans di
sistema. Tutto il resto sta nel repository.

## Com'è fatto

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
python3 tools/verify.py                             # solo il confronto a pixel
```

`build.py` rifà tutto da zero dentro `build/`: copia e rinomina le
immagini, copia gli script che servono, concatena il bundle CSS, rigenera
le cinque pagine e i loro CSS. Eseguirlo due volte di fila non cambia un
byte. Gli unici file scritti a mano sono in `tools/`:
`tools/card-contatti.css` è il CSS della card, e viene copiato dentro
`build/` dalla ricostruzione.

La suite controlla la trasformazione, le proprietà che il sito deve
mantenere (percorsi relativi, riferimenti agli asset che combaciano
lettera per lettera, nessun link morto, fallback dei font), i
comportamenti che uno screenshot non coglie (menu mobile, carosello,
griglia del portfolio, card contatti) e, tramite `verify.py`, il
confronto a pixel con l'originale.

`verify.py` è la rete di sicurezza: per ogni pagina dichiara i riquadri
in cui le differenze sono ammesse, e con il loro perché, e pretende
identità esatta ovunque altrove. Una modifica a mano a un HTML o a un CSS
lo fa fallire indicando il rettangolo.

Per confrontare una singola pagina a mano:

```bash
python3 tools/shoot.py "Sito-FuturaForm/Home-Page.html" riferimento.png --width 1440 --fonts
python3 tools/shoot.py build/index.html nuova.png --width 1440
python3 tools/compare.py riferimento.png nuova.png
```

La home è 44 px più bassa dell'originale, per via del pulsante rimosso,
quindi `compare.py` da solo non può confrontarla: se ne occupa
`verify.py`, che sotto quella cucitura allinea le due immagini dal basso.

L'opzione `--fonts` serve solo sugli originali: i loro `@font-face`
puntano i woff2 su archive.org e non risolvono, quindi senza quella
opzione il confronto misurerebbe il font invece delle modifiche. Gli
screenshot di riferimento già pronti stanno in `baseline/`.
