export interface Departure {
  stop_id: string;
  stop_name: string;
  linea: string | null;
  percorso: string | null;
  destinazione: string | null;
  direction_id: number | null;
  orario_partenza: string;
  tra: string | null;
}

export interface Stop {
  stop_id: string;
  stop_name: string;
  stop_code: string | null;
  stop_lat: number | null;
  stop_lon: number | null;
  lines: Departure[];
}

export interface StopsResponse {
  query: string;
  risultati: number;
  stops: Stop[];
}