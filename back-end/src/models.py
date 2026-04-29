from typing import Optional, List
from pydantic import BaseModel


# Modelli — /stops
class Departure(BaseModel):
	stop_id: str
	stop_name: str
	linea: Optional[str]
	percorso: Optional[str]
	destinazione: Optional[str]
	direction_id: Optional[int]
	orario_partenza: str
	tra: Optional[str]


class Stop(BaseModel):
	stop_id: str
	stop_name: str
	stop_code: Optional[str]
	stop_lat: Optional[float]
	stop_lon: Optional[float]
	lines: List[Departure] = []


class StopsResponse(BaseModel):
	query: str
	risultati: int
	stops: List[Stop]


# Modelli — /lines
class LineDeparture(BaseModel):
	trip_id: str
	trip_headsign: Optional[str]
	orario_partenza: str
	tra: Optional[str]


class LineStop(BaseModel):
	stop_id: str
	stop_name: str
	stop_code: Optional[str]
	stop_lat: Optional[float]
	stop_lon: Optional[float]
	stop_sequence: int
	departures:  List[LineDeparture] = []


class LineDirection(BaseModel):
	direction_id: int
	headsign: Optional[str]   # capolinea/destinazione principale
	stops: List[LineStop] = []


class LineResponse(BaseModel):
	query: str
	risultati: int          # numero di direzioni trovate
	route_id: str
	route_short_name: Optional[str]
	route_long_name: Optional[str]
	directions: List[LineDirection] = []


# Modelli — /stop-line-departures
class StopLineDeparture(BaseModel):
	trip_id: str
	trip_headsign: Optional[str]
	orario_partenza: str


class StopLineDeparturesResponse(BaseModel):
	stop_id: str
	stop_name: str
	stop_code: Optional[str]
	route_id: str
	route_short_name: Optional[str]
	route_long_name: Optional[str]
	direction_id: int
	direction_headsign: Optional[str]
	departures: List[StopLineDeparture] = []


# Modelli — /lines
class LineInfo(BaseModel):
	route_id: str
	route_short_name: Optional[str]
	route_long_name: Optional[str]


class LinesResponse(BaseModel):
	lines: List[LineInfo]


# Modelli — /stops/nearby
class NearbyStop(BaseModel):
	stop_id: str
	stop_name: str
	stop_code: Optional[str]
	stop_lat: float
	stop_lon: float
	distance: float  # distance in meters


class NearbyStopsResponse(BaseModel):
	lat: float
	lon: float
	radius: int
	risultati: int
	stops: List[NearbyStop]