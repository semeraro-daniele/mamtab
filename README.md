# Mamtab

Mamtab è una web app basata su dati GTFS per esplorare le linee degli autobus della città di Bari. Offre ricerche per linea e per fermata, visualizzazione degli orari e delle corse, e una interfaccia semplice per consultare i dati di trasporto pubblico estratti dal feed GTFS locale.

Caratteristiche principali:
- Visualizzazione delle linee e delle fermate di Bari
- Ricerca per linea e per fermata
- Visualizzazione orari e sequenza delle corse
- Backend Python per importare e interrogare i file GTFS
- Dataset GTFS incluso in `mamtab-backend/gtfs_data`

## Struttura del progetto

```
mamtab/
├── docker-compose.yml     # web (nginx + Angular) + api (FastAPI) + db (PostgreSQL)
├── .env.example           # WEB_PORT e credenziali DB -> copiare in .env
├── mamtab-frontend/       # Angular (src/), Dockerfile, nginx.conf
└── mamtab-backend/        # FastAPI (src/), PostgreSQL.sql, gtfs_data/, Dockerfile
```

## Avvio con Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Al primo avvio il backend crea lo schema e importa i dati GTFS: ci può volere qualche minuto, soprattutto su Raspberry.
L'app è disponibile su `http://<host>:<WEB_PORT>`.

Per reimportare i dati GTFS dopo averli aggiornati:

```bash
docker compose up -d --build api
docker compose exec api python insert_data.py
```

## Sviluppo locale

1) Frontend (Angular)

```bash
cd mamtab-frontend
npm install
npm start          # http://localhost:4200
```

2) Backend (Python): vedi [mamtab-backend/DB_SETUP.md](mamtab-backend/DB_SETUP.md) per il database, poi

```bash
cd mamtab-backend/src
uvicorn main:app --reload --port 8000
```

## Esempio rapido
- Per esplorare le corse di una linea: usare la sezione "Search by line" nell'interfaccia.
- Per cercare una fermata: usare "Search by stop" e visualizzare gli orari associati.

## Contribuire
- Segnalazioni di bug e richieste di funzionalità sono benvenute. Aprire una issue o una pull request.

## Licenza
- Non ancora definita!
