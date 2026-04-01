export interface LineDeparture {
  trip_id: string;
  trip_headsign: string | null;
  orario_partenza: string;
  tra: string | null;
}

export interface StopLineDeparture {
  trip_id: string;
  trip_headsign: string | null;
  orario_partenza: string;
}

export interface StopLineDeparturesResponse {
  stop_id: string;
  stop_name: string;
  stop_code: string | null;
  route_id: string;
  route_short_name: string | null;
  route_long_name: string | null;
  direction_id: number;
  direction_headsign: string | null;
  departures: StopLineDeparture[];
}

export interface LineStop {
  stop_id: string;
  stop_name: string;
  stop_code: string | null;
  stop_lat: number | null;
  stop_lon: number | null;
  stop_sequence: number;
  departures: LineDeparture[];
}

export interface LineDirection {
  direction_id: number;
  headsign: string | null;
  stops: LineStop[];
}

export interface LineResponse {
  query: string;
  risultati: number;
  route_id: string;
  route_short_name: string | null;
  route_long_name: string | null;
  directions: LineDirection[];
}

export interface LineInfo {
  route_id: string;
  route_short_name: string | null;
  route_long_name: string | null;
}

export interface LinesResponse {
  lines: LineInfo[];
}