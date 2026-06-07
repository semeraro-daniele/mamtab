# Creazione e popolamento del database PostgreSQL (backend Mamtab)

Questo file descrive tutti i passaggi per creare il database, importare lo schema, configurare le variabili d'ambiente e caricare i file GTFS forniti in `back-end/gtfs_data`.

## Prerequisiti
- PostgreSQL installato e in esecuzione (hai già eseguito i comandi di installazione).
- Accesso alla cartella del progetto (es. `/home/utente/mamtab` o la cartella sul server).

---

## 1) Installazione PostegreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib python3-venv python3-pip
sudo systemctl enable --now postgresql
```

## 2) Crea utente e database

```bash
# come utente root/postgres
sudo -u postgres psql -c "CREATE USER mamtab WITH PASSWORD 'root';"

# VIENE FATTO NELLO SCRIPT SQL
sudo -u postgres psql -c "CREATE DATABASE gtfs_db OWNER mamtab;"
```

---

## 2) Importare lo schema SQL

```bash
sudo -u postgres psql -d gtfs_db -f PostgreSQL.sql
```

---

## 3) Configurare le variabili d'ambiente
Nel backend c'è un file di esempio: `back-end/src/.env.example`.

```bash
cd src
cp .env.example .env
# editare .env: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
nano .env
```

Esempio di valori:

```
DB_HOST=localhost
DB_NAME=gtfs_db
DB_USER=mamtab
DB_PASSWORD=root
```

---

## 4) Creare ambiente Python e installare dipendenze

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se `requirements.txt` non è aggiornato, installa almeno `psycopg2-binary pandas python-dotenv`.

---

## 5) Caricare i dati GTFS
Lo script di import è `back-end/src/insert_data.py`. Per impostazione predefinita legge i file da `back-end/gtfs_data`.

```bash
# con venv attivo e da back-end/src
python insert_data.py
```

Lo script stamperà il numero di righe importate e messaggi di log; rispetta l'ordine per le FK e usa COPY per velocità.

---

## 6) Verifica del database

```bash
# elenco tabelle (come superuser)
sudo -u postgres psql -d gtfs_db -c "\dt"

# contare righe nella tabella stops (usando l'utente creato)
psql -U mamtab -h localhost -d gtfs_db -c "SELECT COUNT(*) FROM stops;"
```

Se ottieni errori di autenticazione con `psql -U`, assicurati che `pg_hba.conf` permetta connessioni locali con password e che il servizio sia riavviato.

---


Modifica la porta o il binding se necessario (firewall/selinux).

---

## 8) Note e troubleshooting rapido
- Se `insert_data.py` fallisce per mancanza di dipendenze: installa `psycopg2-binary pandas python-dotenv`.
- Se vedi errori FK: verifica l'ordine dei file GTFS e che non ci siano righe malformate.
- Encoding: i file GTFS italiani spesso hanno BOM — lo script già gestisce `utf-8-sig`.
- Permessi: esegui i comandi `psql` come `postgres` quando modifichi DB a basso livello.

Uninstall PostgreSQL:

```bash
sudo systemctl stop postgresql
sudo apt --purge remove postgresql\* -y
sudo apt autoremove -y
sudo apt autoclean
sudo rm -rf /etc/postgresql
sudo rm -rf /var/lib/postgresql
sudo rm -rf /var/log/postgresql
sudo rm -rf /usr/lib/postgresql
```