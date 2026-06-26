# Creazione e popolamento del database PostgreSQL (backend Mamtab)

Questo progetto usa un unico punto centralizzato per inizializzare PostgreSQL: [`setup_db.py`](src/setup_db.py). Lo script crea il database se manca e applica lo schema da [`PostgreSQL.sql`](PostgreSQL.sql), usando solo l'utente admin configurato nel file ambiente.

## Prerequisiti
- PostgreSQL installato e in esecuzione.
- File GTFS presenti in [`gtfs_data`](gtfs_data).

---

## 1) Configurare le variabili d'ambiente
Copia [`src/.env.example`](src/.env.example) in [`src/.env`](src/.env) e modifica i valori se necessario.

```bash
cd back-end/src
cp .env.example .env
```

Esempio:

```env
DB_HOST=localhost
DB_NAME=gtfs_db
DB_USER=postgres
DB_PASSWORD=root
```

Significato:
- `DB_USER` / `DB_PASSWORD`: utente amministrativo usato sia dal backend sia dagli script locali.

---

## 2) Installare le dipendenze Python
Da [`src`](src):

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Su Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3) Inizializzare PostgreSQL da un solo punto
Da [`back-end/src`](src) esegui:

```bash
python setup_db.py
```

Su Windows PowerShell:

```powershell
& C:/Users/DanieleSemeraro/AppData/Local/Python/bin/python.exe .\back-end\src\setup_db.py
```

Lo script [`setup_db.py`](src/setup_db.py):
- crea il database `gtfs_db` se non esiste;
- applica tabelle e viste definite in [`PostgreSQL.sql`](PostgreSQL.sql);
- ignora dal file SQL le istruzioni che presuppongono l'esistenza del ruolo `mamtab`.

Quindi non devi più lanciare manualmente [`PostgreSQL.sql`](PostgreSQL.sql) nella procedura standard.

---

## 4) Caricare i dati GTFS
Dopo il setup:

```bash
python insert_data.py
```

Lo script [`insert_data.py`](src/insert_data.py) legge i file da [`gtfs_data`](gtfs_data).

---

## 5) Verifica rapida
Elenco tabelle:

```bash
psql -U postgres -h localhost -d gtfs_db -c "\dt"
```

Conteggio fermate:

```bash
psql -U postgres -h localhost -d gtfs_db -c "SELECT COUNT(*) FROM stops;"
```

---

## Note
- Se [`setup_db.py`](src/setup_db.py) fallisce per autenticazione, controlla `DB_USER` e `DB_PASSWORD` nel `.env`.
- [`PostgreSQL.sql`](PostgreSQL.sql) resta la sorgente dello schema, ma viene applicato tramite [`setup_db.py`](src/setup_db.py).
- [`db.py`](src/db.py) e [`insert_data.py`](src/insert_data.py) continuano a usare `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
