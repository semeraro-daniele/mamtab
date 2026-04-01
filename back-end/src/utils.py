import re
from typing import Optional, List, Dict

from models import (
    Stop,
    Departure,
    LineStop,
    LineDeparture,
    LineDirection,
    LineResponse,
)


def clean_input_query(q: Optional[str]) -> Optional[str]:
    """Pulisce e normalizza la stringa di query lato API.

    - rimuove spazi multipli e caratteri pericolosi come ' " ; e commenti SQL
    - normalizza i numeri singoli 1-9 in 01..09
    - ritorna None se l'input è None
    """
    if q is None:
        return None

    s = q.strip()
    # collapse multiple spaces
    s = re.sub(r"\s+", " ", s)

    parts: list[str] = []
    for token in s.split(" "):
        # if token is a plain integer 1..9, convert to zero-padded form
        if token.isdigit():
            n = int(token)
            if 1 <= n <= 9:
                parts.append(f"0{n}")
                continue
        parts.append(token)

    cleaned = " ".join(parts)

    # remove obvious SQL metacharacters/comments that could interfere
    cleaned = re.sub(r";|--|/\*|\*/|'|\"", "", cleaned)

    return cleaned


def raggruppa_per_fermata(rows: List[Dict]) -> List[Stop]:
    """Raggruppa le righe per fermata, mettendo le partenze dentro lines[]."""
    fermata_map: Dict[str, Stop] = {}
    for row in rows:
        sid = row["stop_id"]
        if sid not in fermata_map:
            fermata_map[sid] = Stop(
                stop_id=row["stop_id"],
                stop_name=row["stop_name"],
                stop_code=row.get("stop_code"),
                stop_lat=row.get("stop_lat"),
                stop_lon=row.get("stop_lon"),
                lines=[],
            )
        fermata_map[sid].lines.append(
            Departure(
                stop_id=row["stop_id"],
                stop_name=row["stop_name"],
                linea=row.get("linea"),
                percorso=row.get("percorso"),
                destinazione=row.get("destinazione"),
                direction_id=row.get("direction_id"),
                orario_partenza=row["orario_partenza"],
                tra=row.get("tra"),
            )
        )
    return list(fermata_map.values())


def raggruppa_per_linea(rows: List[Dict]) -> Optional[LineResponse]:
    """
    Struttura: route → directions[] → stops[] (ordinati per stop_sequence) → departures[]
    Ritorna None se rows è vuoto.
    """
    if not rows:
        return None

    first = rows[0]
    route_id = first["route_id"]
    route_short_name = first["route_short_name"]
    route_long_name = first["route_long_name"]

    # direction_id → { stop_id → LineStop }
    dir_map: Dict[int, Dict[str, LineStop]] = {}
    dir_headsign: Dict[int, Optional[str]] = {}

    for row in rows:
        did = row["direction_id"] if row["direction_id"] is not None else 0
        sid = row["stop_id"]

        # Primo headsign trovato per questa direction
        if did not in dir_headsign:
            dir_headsign[did] = row.get("trip_headsign")

        if did not in dir_map:
            dir_map[did] = {}

        if sid not in dir_map[did]:
            dir_map[did][sid] = LineStop(
                stop_id=sid,
                stop_name=row["stop_name"],
                stop_code=row.get("stop_code"),
                stop_lat=row.get("stop_lat"),
                stop_lon=row.get("stop_lon"),
                stop_sequence=row["stop_sequence"],
                departures=[],
            )

        dir_map[did][sid].departures.append(
            LineDeparture(
                trip_id=row["trip_id"],
                trip_headsign=row.get("trip_headsign"),
                orario_partenza=row["orario_partenza"],
                tra=row.get("tra"),
            )
        )

    # Assembla le direzioni con le fermate ordinate per stop_sequence
    directions: List[LineDirection] = []
    for did in sorted(dir_map.keys()):
        stops_sorted = sorted(dir_map[did].values(), key=lambda s: s.stop_sequence)
        directions.append(LineDirection(
            direction_id=did,
            headsign=dir_headsign[did],
            stops=stops_sorted,
        ))

    return LineResponse(
        query=route_short_name or route_long_name or "",
        risultati=len(directions),
        route_id=route_id,
        route_short_name=route_short_name,
        route_long_name=route_long_name,
        directions=directions,
    )


def raggruppa_per_linea_stops(rows: List[Dict]) -> Optional[LineResponse]:
    """
    Raggruppa i risultati di LINE_STOPS_QUERY in una LineResponse.
    Restituisce None se rows è vuoto.
    """
    if not rows:
        return None

    first = rows[0]
    route_id = first.get("route_id")
    route_short_name = first.get("route_short_name")
    route_long_name = first.get("route_long_name")

    # direction_id -> { stop_id -> LineStop }
    dir_map: Dict[int, Dict[str, LineStop]] = {}
    dir_headsign: Dict[int, Optional[str]] = {}

    for row in rows:
        did = row["direction_id"] if row["direction_id"] is not None else 0
        sid = row["stop_id"]

        if did not in dir_headsign:
            dir_headsign[did] = row.get("trip_headsign")

        if did not in dir_map:
            dir_map[did] = {}

        if sid not in dir_map[did]:
            dir_map[did][sid] = LineStop(
                stop_id=sid,
                stop_name=row.get("stop_name"),
                stop_code=row.get("stop_code"),
                stop_lat=row.get("stop_lat"),
                stop_lon=row.get("stop_lon"),
                stop_sequence=int(row.get("stop_sequence") or 0),
                departures=[],
            )

    directions: List[LineDirection] = []
    for did in sorted(dir_map.keys()):
        stops_sorted = sorted(dir_map[did].values(), key=lambda s: s.stop_sequence)
        directions.append(LineDirection(
            direction_id=did,
            headsign=dir_headsign.get(did),
            stops=stops_sorted,
        ))

    return LineResponse(
        query=route_short_name or route_long_name or "",
        risultati=len(directions),
        route_id=route_id,
        route_short_name=route_short_name,
        route_long_name=route_long_name,
        directions=directions,
    )
