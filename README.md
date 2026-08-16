# Marvel Tracker

Tracker responsive per film e serie Marvel, con:
- ricerca;
- filtro Film / Serie;
- sezioni richiudibili;
- progresso salvato nel browser;
- dati separati in `data/marvel.json`;
- aggiornamento automatico tramite GitHub Actions;
- pubblicazione automatica con GitHub Pages.

## Struttura

```text
Marvel_Tracker_GitHub/
├── index.html
├── data/
│   └── marvel.json
├── scripts/
│   └── update_marvel.py
└── .github/
    └── workflows/
        └── pages.yml
```

## Pubblicazione su GitHub

1. Crea un nuovo repository, ad esempio `marvel-tracker`.
2. Carica **tutti i file e le cartelle** di questo progetto.
3. Assicurati che `index.html` sia nella root del repository.
4. Vai in **Settings → Pages**.
5. In **Build and deployment → Source**, seleziona **GitHub Actions**.
6. Apri **Actions** e avvia manualmente `Marvel Tracker - aggiornamento e pubblicazione` se necessario.
7. Al termine troverai il link del sito nella pagina dell'esecuzione del workflow / nelle impostazioni Pages.

## Aggiornamento automatico

Il workflow controlla la pagina di TV Sorrisi e Canzoni ogni giorno alle 05:00 UTC e può essere avviato anche manualmente.

Per prudenza, i titoli nuovi trovati dalla pagina vengono messi nella sezione `sourceUpdates` di `data/marvel.json` invece di modificare automaticamente le fasi curate a mano.

### Importante

La fonte può impedire lo scraping automatico o cambiare la struttura HTML. In quel caso il workflow lascia invariati i dati esistenti e il sito continua a funzionare.

Il contenuto della fonte resta di proprietà del relativo editore. Il tracker usa la pagina come riferimento e non copia testi descrittivi o immagini.

## Test locale

Non aprire `index.html` con doppio clic se il browser blocca `fetch()` dei file locali. Usa, per esempio:

```bash
python3 -m http.server 8000
```

poi visita:

```text
http://localhost:8000
```
