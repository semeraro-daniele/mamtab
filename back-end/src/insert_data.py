"""
load_gtfs.py
Carica i file GTFS (formato CSV con estensione .txt) nel database PostgreSQL.

Dipendenze:
    pip install psycopg2-binary pandas dotenv

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Uso:
    python load_gtfs.py
"""

import os
import sys
import time
import pandas as pd
import psycopg2
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

# Configurazione
REQUIRED_ENV = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
if missing:
	raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

DB_CONFIG = {
	"host": os.environ["DB_HOST"],
	"database": os.environ["DB_NAME"],
	"user": os.environ["DB_USER"],
	"password": os.environ["DB_PASSWORD"],
}

DATA_DIR = os.environ.get("GTFS_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "gtfs_data"))

# Ordine di caricamento (rispetta le FK)
# Ogni voce: (nome_file, nome_tabella, colonne_da_usare | None per tutte)
LOAD_ORDER = [
    ("agency.txt",         "agency",         None),
    ("feed_info.txt",      "feed_info",      None),
    ("routes.txt",         "routes",         None),
    ("calendar.txt",       "calendar",       None),
    ("calendar_dates.txt", "calendar_dates", None),
    ("shapes.txt",         "shapes",         None),
    ("stops.txt",          "stops",          None),
    ("trips_clean.txt",    "trips",          None),   # usa trips_clean se disponibile
    ("stop_times.txt",     "stop_times",     None),
    ("transfers.txt",      "transfers",      None),
]

# Colonne che devono diventare booleane nella tabella calendar
CALENDAR_BOOL_COLS = [
    "monday","tuesday","wednesday","thursday",
    "friday","saturday","sunday",
]

# Helpers
def log(msg: str):
    print(f"  {msg}")


def connect() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    # Imposta lo schema di lavoro
    with conn.cursor() as cur:
        cur.execute("SET search_path TO public;")
    conn.commit()
    return conn


def file_path(filename: str) -> str | None:
    """Restituisce il path completo se il file esiste, altrimenti None."""
    p = os.path.join(DATA_DIR, filename)
    return p if os.path.isfile(p) else None


def read_csv(path: str) -> pd.DataFrame:
    """
    Legge un file GTFS (CSV con header) gestendo:
    - encoding UTF-8 con BOM (comune nei feed italiani)
    - righe \r\n (CRLF)
    - campi vuoti → None
    """
    df = pd.read_csv(
        path,
        dtype=str,           # tutto come stringa, le conversioni le facciamo dopo
        encoding="utf-8-sig",
        sep=",",
        low_memory=False,
    )
    # Normalizza i nomi colonna (rimuove spazi accidentali)
    df.columns = [c.strip() for c in df.columns]
    # Sostituisce stringhe vuote con NaN → poi diventano NULL in SQL
    df.replace("", pd.NA, inplace=True)
    return df


def df_to_pg(conn, df: pd.DataFrame, table: str):
    """
    Carica un DataFrame in una tabella PostgreSQL via COPY (veloce)
    con fallback su execute_values se COPY non è disponibile.
    """
    if df.empty:
        log(f"⚠  {table}: file vuoto, skip.")
        return 0

    cols = list(df.columns)
    col_str = ", ".join(f'"{c}"' for c in cols)

    # Metodo veloce: COPY FROM STDIN
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    with conn.cursor() as cur:
        try:
            cur.copy_expert(
                f"COPY {table} ({col_str}) FROM STDIN WITH (FORMAT csv, NULL '\\N')",
                buffer,
            )
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"COPY fallito su {table}: {e}") from e

    return len(df)


def prepare_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """Converte 0/1 → False/True per le colonne booleane di calendar."""
    for col in CALENDAR_BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].map({"1": True, "0": False, True: True, False: False})
    return df


def prepare_stops(df: pd.DataFrame) -> pd.DataFrame:
    """
    stops.parent_station è una FK su stops.stop_id (auto-riferimento).
    Se il valore è NULL va bene; se punta a uno stop non ancora inserito
    causerebbe un errore FK — ma in GTFS di solito le stazioni madri
    vengono prima nel file, quindi va bene così.
    """
    return df


# Logica principale
def truncate_all(conn):
    """Svuota tutte le tabelle in ordine inverso alle FK."""
    tables = [
        "transfers", "stop_times", "trips", "shapes",
        "stops", "calendar_dates", "calendar",
        "routes", "feed_info", "agency",
    ]
    with conn.cursor() as cur:
        for t in tables:
            cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
    conn.commit()
    log("Tabelle svuotate.")


def load_all(conn, truncate: bool = True):
    if truncate:
        truncate_all(conn)

    total_rows = 0

    for filename, table, cols in LOAD_ORDER:
        path = file_path(filename)
        if path is None:
            # Prova senza _clean (es. trips.txt come fallback di trips_clean.txt)
            alt = filename.replace("_clean", "")
            path = file_path(alt)
            if path is None:
                log(f"⚠  {filename} non trovato in {DATA_DIR}, skip.")
                continue
            else:
                log(f"ℹ  Uso {alt} al posto di {filename}")

        t0 = time.time()
        log(f"→  Caricamento {table} da {os.path.basename(path)} …")

        df = read_csv(path)

        # Seleziona solo le colonne richieste (se specificate)
        if cols:
            df = df[[c for c in cols if c in df.columns]]

        # Trasformazioni specifiche per tabella
        if table == "calendar":
            df = prepare_calendar(df)
        elif table == "stops":
            df = prepare_stops(df)

        try:
            n = df_to_pg(conn, df, table)
            conn.commit()
            elapsed = time.time() - t0
            log(f"   ✓  {n:,} righe inserite ({elapsed:.1f}s)")
            total_rows += n
        except Exception as e:
            conn.rollback()
            log(f"   ✗  Errore: {e}")
            raise

    return total_rows


# Entry point 
def main():
    print("\n=== GTFS Loader ===")
    print(f"DB:      {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print(f"Data:    {DATA_DIR}")
    print()

    if not os.path.isdir(DATA_DIR):
        print(f"ERRORE: la cartella '{DATA_DIR}' non esiste.")
        sys.exit(1)

    try:
        conn = connect()
        print("Connessione al DB riuscita.\n")
    except Exception as e:
        print(f"ERRORE di connessione: {e}")
        sys.exit(1)

    try:
        t_start = time.time()
        total = load_all(conn, truncate=True)
        elapsed = time.time() - t_start
        print(f"\n✅  Completato — {total:,} righe totali in {elapsed:.1f}s")
    except Exception as e:
        print(f"\n❌  Caricamento interrotto: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()