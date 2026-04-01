"""
main.py - GTFS Departures API (refactored)

Questo file espone gli endpoint e importa funzioni/modelli da
`db.py`, `queries.py`, `models.py` e `utils.py`.

Run:
cd ../src
python3 -m venv venv
source venv/bin/activate
pip install uvicorn fastapi psycopg2-binary python-dotenv pytz

Execution (windows):
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Background (Linux):
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

Stop:
sudo lsof -i :8000
sudo kill -p [ID]
"""

from typing import Optional
import logging
import psycopg2.extras
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import db
import queries
import utils
from models import StopsResponse, LineResponse, StopLineDeparturesResponse, StopLineDeparture, LinesResponse, LineInfo


router = APIRouter(prefix="/api")

app = FastAPI(
    title="GTFS Departures API",
    description="Prossime partenze da una fermata Amtab - cerca per stop_id, nome fermata o numero linea.",
    version="2.0.0",
)

# Basic logging configuration
logging.basicConfig(level=logging.INFO)

# CORS - permette chiamate dall'Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://192.168.1.120"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# STOPS
@router.get(
    "/stops/{query}",
    response_model=StopsResponse,
    summary="Prossime partenze — cerca per nome fermata o stop_id",
)
def stops(query: str):
    query_s = utils.clean_input_query(query)
    if not query_s:
        raise HTTPException(status_code=400, detail="Query non valida dopo sanitizzazione.")

    parole = query_s.split()
    filtri_nome = " AND ".join(
        f"s.stop_name ILIKE %(w{i}s)s" for i, _ in enumerate(parole)
    )

    where = f"(s.stop_id = %(q_exact)s OR ({filtri_nome}))"
    params: dict = {
        "q_exact": query_s,
        "finestra": 3 * 3600,       # limite 3 ore
        "departures_per_stop": 50,  # limite 50 partenze
    }

    for i, parola in enumerate(parole):
        params[f"w{i}s"] = f"%{parola}%"

    rows = db.run_query(where, params)
    fermate = utils.raggruppa_per_fermata(rows)

    return StopsResponse(
        query=query_s,
        risultati=len(fermate),
        stops=fermate,
    )

# LINES — ORDINE CRITICO DELLE ROUTE
@router.get(
    "/lines/{line_id:path}/stops/{stop_id}/departures/{direction_id}/{date}",
    response_model=StopLineDeparturesResponse,
    summary="Tutti gli orari di una linea da una fermata per una data specifica",
)
def stop_line_departures_path_date(
    line_id: str,
    stop_id: str,
    direction_id: int,
    date: str,
):
    return _fetch_stop_line_departures(line_id, stop_id, direction_id, date)


@router.get(
    "/lines/{line_id:path}/stops/{stop_id}/departures/{direction_id}",
    response_model=StopLineDeparturesResponse,
    summary="Tutti gli orari di una linea da una fermata (oggi)",
)
def stop_line_departures_path(
    line_id: str,
    stop_id: str,
    direction_id: int,
):
    return _fetch_stop_line_departures(line_id, stop_id, direction_id, None)


@router.get(
    "/lines",
    response_model=LinesResponse,
    summary="Ottieni tutte le linee disponibili",
)
def all_lines():
    """
    Restituisce l'elenco di tutte le linee disponibili nel sistema.
    """
    try:
        with db.get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(queries.ALL_LINES_QUERY)
                rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        logging.exception("DB error while fetching all lines")
        raise HTTPException(status_code=500, detail="Internal server error")

    lines = [
        LineInfo(
            route_id=row["route_id"],
            route_short_name=row.get("route_short_name"),
            route_long_name=row.get("route_long_name"),
        )
        for row in rows
    ]

    return LinesResponse(lines=lines)


@router.get(
    "/lines/{line_id:path}",
    response_model=LineResponse,
    summary="Fermate e orari di una linea",
)
def lines_by_id(line_id: str):
    query_s = utils.clean_input_query(line_id)
    if not query_s:
        raise HTTPException(status_code=400, detail="Query non valida dopo sanitizzazione.")

    line_exact_list = [query_s]
    if query_s.isdigit():
        if len(query_s) == 1:
            line_exact_list.append(f"0{query_s}")
        elif len(query_s) == 2 and query_s.startswith("0"):
            line_exact_list.append(str(int(query_s)))

    params: dict = {
        "line_exact_list": line_exact_list,
        "line_like": f"%{query_s}%",
    }

    try:
        with db.get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(queries.LINE_STOPS_QUERY, params)
                rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        logging.exception("DB error while fetching line stops")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Raggruppa le fermate per direction
    result = utils.raggruppa_per_linea_stops(rows)
    if result is None:
        # Restituisci una risposta vuota con 200
        return LineResponse(
            query=query_s,
            risultati=0,
            route_id="",
            route_short_name=None,
            route_long_name=None,
            directions=[],
        )

    return result

# INTERNAL LOGIC
def _fetch_stop_line_departures(
    line: str,
    stop_id: str,
    direction_id: int,
    date: Optional[str],
):
    line_s = utils.clean_input_query(line)
    if not line_s:
        raise HTTPException(status_code=400, detail="Parametro 'line_id' non valido.")

    line_exact_list = [line_s]
    if line_s.isdigit():
        if len(line_s) == 1:
            line_exact_list.append(f"0{line_s}")
        elif len(line_s) == 2 and line_s.startswith("0"):
            line_exact_list.append(str(int(line_s)))

    params = {
        "stop_id": stop_id,
        "line_exact_list": line_exact_list,
        "line_like": f"%{line_s}%",
        "direction_id": direction_id,
        "target_date": date,
    }

    try:
        with db.get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(queries.STOP_LINE_DEPARTURES_QUERY, params)
                rows = [dict(r) for r in cur.fetchall()]
    except Exception:
        logging.exception("DB error while fetching stop-line departures")
        raise HTTPException(status_code=500, detail="Internal server error")

    if not rows:
        # Restituisce 200 con array vuoto invece di 404
        return StopLineDeparturesResponse(
            stop_id=stop_id,
            stop_name="",
            stop_code=None,
            route_id="",
            route_short_name=line_s,
            route_long_name=None,
            direction_id=direction_id,
            direction_headsign=None,
            departures=[],
        )

    first = rows[0]

    departures = [
        StopLineDeparture(
            trip_id=row["trip_id"],
            trip_headsign=row.get("trip_headsign"),
            orario_partenza=row["orario_partenza"],
        )
        for row in rows
    ]

    return StopLineDeparturesResponse(
        stop_id=first["stop_id"],
        stop_name=first["stop_name"],
        stop_code=first.get("stop_code"),
        route_id=first["route_id"],
        route_short_name=first.get("route_short_name"),
        route_long_name=first.get("route_long_name"),
        direction_id=first["direction_id"],
        direction_headsign=first.get("trip_headsign"),
        departures=departures,
    )

# HEALTH
@router.get("/health", summary="Healthcheck DB")
def health():
    try:
        with db.get_conn():
            pass
        return {"status": "ok"}
    except Exception:
        logging.exception("DB health check failed")
        raise HTTPException(status_code=503, detail="Service unavailable")


app.include_router(router)
