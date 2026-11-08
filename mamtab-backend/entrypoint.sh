#!/bin/sh
set -e

# 1) Crea il database (se manca) e applica lo schema: è idempotente.
python setup_db.py

# 2) Importa i dati GTFS solo al primo avvio (tabella stops vuota).
#    Per reimportarli: docker compose exec api python insert_data.py
if python -c "
import sys, db
with db.get_conn() as c, c.cursor() as cur:
    cur.execute('SELECT COUNT(*) FROM stops')
    sys.exit(0 if cur.fetchone()[0] == 0 else 1)
"; then
    echo 'Database vuoto: importo i dati GTFS...'
    python insert_data.py
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'
