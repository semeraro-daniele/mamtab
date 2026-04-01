# Mamtab

Mamtab è una web app basata su dati GTFS per esplorare le linee degli autobus della città di Bari. Offre ricerche per linea e per fermata, visualizzazione degli orari e delle corse, e una interfaccia semplice per consultare i dati di trasporto pubblico estratti dal feed GTFS locale.

Caratteristiche principali:
- Visualizzazione delle linee e delle fermate di Bari
- Ricerca per linea e per fermata
- Visualizzazione orari e sequenza delle corse
- Backend Python per importare e interrogare i file GTFS
- Dataset GTFS incluso in `back-end/gtfs_data`

Struttura del progetto:
- Frontend: Applicazione Angular moderna (codice in `src/`)
- Backend: Script Python per import dei GTFS e query (cartella `back-end/src/`)
- Dati GTFS: `back-end/gtfs_data/` (agency.txt, stops.txt, trips.txt, ecc.)

Installazione e sviluppo

1) Avviare il frontend (Angular)

```bash
# dalla root del progetto
ng serve
```

L'app sarà disponibile su http://localhost:4200/ e ricaricherà automaticamente le modifiche.

2) Avviare il backend (Python)

```bash
# dalla root del progetto
python -m back-end.src.main
```
```bash
# dalla folder del progetto
uvicorn main:app --reload
```
Nota: il backend importa e usa i file GTFS presenti in `back-end/gtfs_data/`.

Esempio rapido
- Per esplorare le corse di una linea: usare la sezione "Search by line" nell'interfaccia.
- Per cercare una fermata: usare "Search by stop" e visualizzare gli orari associati.

Contribuire
- Segnalazioni di bug e richieste di funzionalità sono benvenute. Aprire una issue o una pull request.

File utili
- Dati GTFS: `back-end/gtfs_data/`
- Backend Python: `back-end/src/`
- Frontend Angular: `src/`

Licenza
- Non ancora definita!

---