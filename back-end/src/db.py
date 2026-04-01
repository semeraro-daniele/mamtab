import os
from dotenv import load_dotenv
import logging
import psycopg2
import psycopg2.extras
import psycopg2.sql as sql
from fastapi import HTTPException

import queries

load_dotenv()

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


def get_conn():
	return psycopg2.connect(**DB_CONFIG)


def run_query(where_clause: str, params: dict) -> list[dict]:
	"""Esegue la query principale `DEPARTURES_QUERY` inserendo in modo sicuro
	il blocco `where_clause` usando `psycopg2.sql` e restituendo una lista di dict.
	"""
	try:
		query_sql = sql.SQL(queries.DEPARTURES_QUERY).format(
			where_clause=sql.SQL(where_clause)
		)

		with get_conn() as conn:
			with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
				cur.execute(query_sql, params)
				rows = cur.fetchall()

		return [dict(r) for r in rows]
	except Exception:
		logging.exception("Database error in run_query")
		raise HTTPException(status_code=500, detail="Internal server error")