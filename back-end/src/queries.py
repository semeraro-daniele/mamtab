# Query SQL — /stops
DEPARTURES_QUERY = """
WITH candidati AS (
	-- Raccoglie tutte le partenze candidate nel range temporale
	-- per le fermate che matchano il where_clause.
	-- Assegna un numero di riga per fermata, ordinato per orario,
	-- così possiamo limitare le partenze PER FERMATA (non globalmente).
	SELECT
		s.stop_id,
		s.stop_name,
		s.stop_code,
		s.stop_lat::float,
		s.stop_lon::float,
		r.route_short_name AS linea,
		r.route_long_name  AS percorso,
		t.trip_headsign    AS destinazione,
		t.direction_id,
		st.departure_time  AS departure_time_raw,
		-- Normalizza orari GTFS oltre mezzanotte (es. 25:30 → 01:30)
		CASE
			WHEN split_part(st.departure_time, ':', 1)::int >= 24
			THEN to_char(
				make_interval(secs =>
					split_part(st.departure_time, ':', 1)::int * 3600 +
					split_part(st.departure_time, ':', 2)::int * 60  +
					split_part(st.departure_time, ':', 3)::int
				) - interval '24 hours',
				'HH24:MI'
			)
			ELSE to_char(
				make_time(
					split_part(st.departure_time, ':', 1)::int,
					split_part(st.departure_time, ':', 2)::int,
					split_part(st.departure_time, ':', 3)::int
				),
				'HH24:MI'
			)
		END AS orario_partenza,
		to_char(
			make_interval(
				hours => split_part(st.departure_time, ':', 1)::int,
				mins  => split_part(st.departure_time, ':', 2)::int,
				secs  => split_part(st.departure_time, ':', 3)::int
			) - ((localtime + interval '1 hour') - '00:00:00'::time),
			'HH24:MI'
		) AS tra,
		-- Rango per fermata: 1 = prossima partenza, 2 = seconda, ecc.
		ROW_NUMBER() OVER (
			PARTITION BY s.stop_id
			ORDER BY
				split_part(st.departure_time, ':', 1)::int * 3600 +
				split_part(st.departure_time, ':', 2)::int * 60  +
				split_part(st.departure_time, ':', 3)::int
		) AS rn

	FROM stop_times st
	JOIN trips  t ON st.trip_id  = t.trip_id
	JOIN routes r ON t.route_id  = r.route_id
	JOIN stops  s ON st.stop_id  = s.stop_id

	WHERE
		{where_clause}

		AND t.service_id IN (
			SELECT service_id
			FROM calendar_dates
			WHERE date = current_date
			  AND exception_type = 1
		)

		AND (
			split_part(st.departure_time, ':', 1)::int * 3600 +
			split_part(st.departure_time, ':', 2)::int * 60  +
			split_part(st.departure_time, ':', 3)::int
		)
		BETWEEN
			EXTRACT(EPOCH FROM (localtime + interval '1 hour'))::int - 600
		AND
			EXTRACT(EPOCH FROM (localtime + interval '1 hour'))::int + %(finestra)s

		-- Escludi solo le fermate dove il bus NON fa salire passeggeri
		-- (pickup_type=1 significa "no pickup" — tipicamente i capolinea di arrivo).
		-- È più preciso di confrontare stop_sequence con il MAX del trip,
		-- perché non esclude fermate che sono capolinea di UNA linea ma
		-- fermata intermedia di un'altra.
		AND st.pickup_type != 1

		-- Escludi i trip dove il capolinea di destinazione è la fermata stessa
		AND t.trip_headsign != s.stop_name
)

SELECT
	stop_id,
	stop_name,
	stop_code,
	stop_lat,
	stop_lon,
	linea,
	percorso,
	destinazione,
	direction_id,
	orario_partenza,
	tra
FROM candidati
-- Limita a %(departures_per_stop)s partenze per fermata
WHERE rn <= %(departures_per_stop)s
ORDER BY stop_name, departure_time_raw;
"""


# Query SQL — /lines (fermate della linea con orari di partenza)
LINE_QUERY = """
SELECT
	r.route_id,
	r.route_short_name,
	r.route_long_name,
	t.direction_id,
	t.trip_headsign,
	t.trip_id,
	s.stop_id,
	s.stop_name,
	s.stop_code,
	s.stop_lat::float,
	s.stop_lon::float,
	st.stop_sequence,
	-- Normalizza orari GTFS oltre mezzanotte (es. 25:30 → 01:30)
	CASE
		WHEN split_part(st.departure_time, ':', 1)::int >= 24
		THEN to_char(
			make_interval(secs =>
				split_part(st.departure_time, ':', 1)::int * 3600 +
				split_part(st.departure_time, ':', 2)::int * 60  +
				split_part(st.departure_time, ':', 3)::int
			) - interval '24 hours',
			'HH24:MI'
		)
		ELSE to_char(
			make_time(
				split_part(st.departure_time, ':', 1)::int,
				split_part(st.departure_time, ':', 2)::int,
				split_part(st.departure_time, ':', 3)::int
			),
			'HH24:MI'
		)
	END AS orario_partenza,
	to_char(
		make_interval(
			hours => split_part(st.departure_time, ':', 1)::int,
			mins  => split_part(st.departure_time, ':', 2)::int,
			secs  => split_part(st.departure_time, ':', 3)::int
		) - (localtime - '00:00:00'::time),
		'HH24:MI'
	) AS tra

FROM stop_times st
JOIN trips t ON st.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
JOIN stops s ON st.stop_id = s.stop_id

WHERE
	(r.route_short_name = ANY(%(line_exact_list)s) OR r.route_long_name ILIKE %(line_like)s)

	AND t.service_id IN (
		SELECT service_id FROM calendar_dates
		WHERE date = current_date AND exception_type = 1
	)

	AND (
		split_part(st.departure_time, ':', 1)::int * 3600 +
		split_part(st.departure_time, ':', 2)::int * 60  +
		split_part(st.departure_time, ':', 3)::int
	)
	BETWEEN
		EXTRACT(EPOCH FROM localtime)::int - 600
	AND
		EXTRACT(EPOCH FROM localtime)::int + %(finestra)s

ORDER BY t.direction_id, st.stop_sequence, st.departure_time
LIMIT %(limit)s;
"""


# Query SQL — /lines (tutte le fermate della linea, indipendentemente dagli orari)
LINE_STOPS_QUERY = """
-- Seleziona, per ogni direction della route cercata, un trip rappresentativo
-- valido per la data odierna, e poi restituisce le fermate di quel trip
-- nell'ordine di percorrenza (stop_sequence).
WITH rep_trips AS (
	SELECT DISTINCT ON (t.direction_id)
		t.direction_id,
		t.trip_id,
		t.trip_headsign,
		r.route_id,
		r.route_short_name,
		r.route_long_name
		FROM trips t
		JOIN routes r ON t.route_id = r.route_id
		-- Non filtrare per `calendar_dates` qui: vogliamo mostrare la linea indipendentemente da festivo/feriale
		WHERE (r.route_short_name = ANY(%(line_exact_list)s) OR r.route_long_name ILIKE %(line_like)s)
	-- Ordina per direction_id e poi per qualche criterio stabile (qui trip_id)
	ORDER BY t.direction_id, t.trip_id
)

SELECT
	rt.route_id,
	rt.route_short_name,
	rt.route_long_name,
	rt.direction_id,
	rt.trip_headsign,
	s.stop_id,
	s.stop_name,
	s.stop_code,
	s.stop_lat::float,
	s.stop_lon::float,
	st.stop_sequence
FROM rep_trips rt
JOIN stop_times st ON st.trip_id = rt.trip_id
JOIN stops s ON st.stop_id = s.stop_id
ORDER BY rt.direction_id, st.stop_sequence;
"""


# Query SQL — /stop-line-departures (tutti gli orari di una linea da una fermata nella giornata)
STOP_LINE_DEPARTURES_QUERY = """
SELECT
	r.route_id,
	r.route_short_name,
	r.route_long_name,
	s.stop_id,
	s.stop_name,
	s.stop_code,
	s.stop_lat::float,
	s.stop_lon::float,
	t.direction_id,
	t.trip_headsign,
	t.trip_id,
	-- Normalizza orari GTFS oltre mezzanotte (es. 25:30 → 01:30)
	CASE
		WHEN split_part(st.departure_time, ':', 1)::int >= 24
		THEN to_char(
			make_interval(secs =>
				split_part(st.departure_time, ':', 1)::int * 3600 +
				split_part(st.departure_time, ':', 2)::int * 60  +
				split_part(st.departure_time, ':', 3)::int
			) - interval '24 hours',
			'HH24:MI'
		)
		ELSE to_char(
			make_time(
				split_part(st.departure_time, ':', 1)::int,
				split_part(st.departure_time, ':', 2)::int,
				split_part(st.departure_time, ':', 3)::int
			),
			'HH24:MI'
		)
	END AS orario_partenza,
	st.departure_time AS departure_time_raw

FROM stop_times st
JOIN trips t ON st.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
JOIN stops s ON st.stop_id = s.stop_id

WHERE
	s.stop_id = %(stop_id)s
	AND (r.route_short_name = ANY(%(line_exact_list)s) OR r.route_long_name ILIKE %(line_like)s)
	AND t.direction_id = %(direction_id)s
	
	AND t.service_id IN (
		SELECT service_id FROM calendar_dates
		WHERE date = COALESCE(%(target_date)s::date, current_date) AND exception_type = 1
	)
	
	AND st.pickup_type != 1

ORDER BY
	-- Ordina gli orari mettendo quelli dopo mezzanotte (00:00-05:59) alla fine
	CASE
		WHEN split_part(st.departure_time, ':', 1)::int < 6
		THEN split_part(st.departure_time, ':', 1)::int * 3600 +
		     split_part(st.departure_time, ':', 2)::int * 60 +
		     split_part(st.departure_time, ':', 3)::int + 86400
		ELSE split_part(st.departure_time, ':', 1)::int * 3600 +
		     split_part(st.departure_time, ':', 2)::int * 60 +
		     split_part(st.departure_time, ':', 3)::int
	END;
"""


# Query SQL — /lines (tutte le linee disponibili)
ALL_LINES_QUERY = """
SELECT
	r.route_id,
	r.route_short_name,
	r.route_long_name,
	CASE
		WHEN r.route_short_name ~ '^[0-9]+$'
		THEN LPAD(r.route_short_name, 10, '0')
		ELSE r.route_short_name
	END AS sort_key
FROM routes r
WHERE r.route_short_name IS NOT NULL
GROUP BY r.route_id, r.route_short_name, r.route_long_name
ORDER BY sort_key;
"""