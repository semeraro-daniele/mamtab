-- GTFS Schema per PostgreSQL

-- RESET TABELLE
-- DROP TABLE IF EXISTS transfers CASCADE;
-- DROP TABLE IF EXISTS stop_times CASCADE;
-- DROP TABLE IF EXISTS trips CASCADE;
-- DROP TABLE IF EXISTS shapes CASCADE;
-- DROP TABLE IF EXISTS stops CASCADE;
-- DROP TABLE IF EXISTS calendar_dates CASCADE;
-- DROP TABLE IF EXISTS calendar CASCADE;
-- DROP TABLE IF EXISTS routes CASCADE;
-- DROP TABLE IF EXISTS feed_info CASCADE;
-- DROP TABLE IF EXISTS agency CASCADE;

CREATE DATABASE gtfs_db;

-- AGENCY
CREATE TABLE IF NOT EXISTS agency (
    agency_id           TEXT PRIMARY KEY,
    agency_name         TEXT NOT NULL,
    agency_url          TEXT NOT NULL,
    agency_timezone     TEXT NOT NULL,
    agency_lang         TEXT,
    agency_phone        TEXT,
    agency_fare_url     TEXT,
    agency_email        TEXT
);

-- FEED INFO
CREATE TABLE IF NOT EXISTS feed_info (
    feed_publisher_name TEXT NOT NULL,
    feed_publisher_url  TEXT NOT NULL,
    feed_contact_email  TEXT,
    feed_lang           TEXT NOT NULL,
    default_lang        TEXT,
    feed_start_date     DATE,
    feed_end_date       DATE,
    feed_version        TEXT
);

-- ROUTES
CREATE TABLE IF NOT EXISTS routes (
    route_id            TEXT PRIMARY KEY,
    agency_id           TEXT REFERENCES agency(agency_id) ON DELETE CASCADE,
    route_short_name    TEXT,
    route_long_name     TEXT,
    route_desc          TEXT,
    route_type          INTEGER NOT NULL,
    route_url           TEXT,
    route_color         TEXT,
    route_text_color    TEXT,
    route_sort_order    INTEGER
);

-- CALENDAR
CREATE TABLE IF NOT EXISTS calendar (
    service_id  TEXT PRIMARY KEY,
    monday      BOOLEAN NOT NULL,
    tuesday     BOOLEAN NOT NULL,
    wednesday   BOOLEAN NOT NULL,
    thursday    BOOLEAN NOT NULL,
    friday      BOOLEAN NOT NULL,
    saturday    BOOLEAN NOT NULL,
    sunday      BOOLEAN NOT NULL,
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL
);

-- CALENDAR DATES
CREATE TABLE IF NOT EXISTS calendar_dates (
    service_id      TEXT NOT NULL,
    date            DATE NOT NULL,
    exception_type  INTEGER NOT NULL,  -- 1=aggiunto, 2=rimosso
    PRIMARY KEY (service_id, date)
);

-- SHAPES
CREATE TABLE IF NOT EXISTS shapes (
    shape_id TEXT NOT NULL,
    shape_pt_lat DOUBLE PRECISION NOT NULL,
    shape_pt_lon DOUBLE PRECISION NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DOUBLE PRECISION,
    PRIMARY KEY (shape_id, shape_pt_sequence)
);

-- STOPS
CREATE TABLE IF NOT EXISTS stops (
    stop_id TEXT PRIMARY KEY,
    stop_code TEXT,
    stop_name TEXT,
    stop_desc TEXT,
    stop_lat DOUBLE PRECISION,
    stop_lon DOUBLE PRECISION,
    zone_id TEXT,
    stop_url TEXT,
    location_type INTEGER DEFAULT 0,
    parent_station TEXT REFERENCES stops(stop_id),
    stop_timezone TEXT,
    wheelchair_boarding INTEGER DEFAULT 0,
    level_id TEXT,
    platform_code TEXT
);

CREATE INDEX IF NOT EXISTS idx_stops_latlon ON stops(stop_lat, stop_lon);

-- TRIPS
CREATE TABLE IF NOT EXISTS trips (
    route_id TEXT NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    service_id TEXT NOT NULL,
    trip_id TEXT PRIMARY KEY,
    trip_headsign TEXT,
    trip_short_name TEXT,
    direction_id INTEGER,
    block_id TEXT,
    shape_id TEXT,
    wheelchair_accessible INTEGER DEFAULT 0,
    bikes_allowed INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_trips_route   ON trips(route_id);
CREATE INDEX IF NOT EXISTS idx_trips_service ON trips(service_id);
CREATE INDEX IF NOT EXISTS idx_trips_shape   ON trips(shape_id);

-- STOP TIMES
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id TEXT NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    arrival_time TEXT,
    departure_time TEXT,
    stop_id TEXT NOT NULL REFERENCES stops(stop_id),
    stop_sequence INTEGER NOT NULL,
    stop_headsign TEXT,
    pickup_type INTEGER DEFAULT 0,
    drop_off_type INTEGER DEFAULT 0,
    shape_dist_traveled DOUBLE PRECISION,
    timepoint INTEGER DEFAULT 1,
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE INDEX IF NOT EXISTS idx_stop_times_stop ON stop_times(stop_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_trip ON stop_times(trip_id);

-- TRANSFERS
CREATE TABLE IF NOT EXISTS transfers (
    from_stop_id TEXT REFERENCES stops(stop_id),
    to_stop_id TEXT REFERENCES stops(stop_id),
    transfer_type     INTEGER NOT NULL,
    min_transfer_time INTEGER,
    from_route_id TEXT REFERENCES routes(route_id),
    to_route_id TEXT REFERENCES routes(route_id),
    from_trip_id TEXT REFERENCES trips(trip_id),
    to_trip_id TEXT REFERENCES trips(trip_id)
);

-- VISTE
CREATE OR REPLACE VIEW v_stop_departures AS
SELECT
    s.stop_id, s.stop_name, s.stop_lat, s.stop_lon,
    r.route_short_name, r.route_long_name,
    t.trip_headsign, st.departure_time, t.direction_id
FROM stop_times st
JOIN trips t ON st.trip_id = t.trip_id
JOIN routes r ON t.route_id = r.route_id
JOIN stops s ON st.stop_id = s.stop_id
ORDER BY s.stop_name, st.departure_time;

CREATE OR REPLACE VIEW v_trips_per_route AS
SELECT
    r.route_id, r.route_short_name, r.route_long_name,
    COUNT(t.trip_id) AS num_trips
FROM routes r
LEFT JOIN trips t ON r.route_id = t.route_id
GROUP BY r.route_id, r.route_short_name, r.route_long_name
ORDER BY r.route_sort_order;

-- IMPORT CON COPY (adatta il percorso ai tuoi file)
/*
\COPY agency         FROM 'agency.txt'         CSV HEADER;
\COPY feed_info      FROM 'feed_info.txt'       CSV HEADER;
\COPY routes         FROM 'routes.txt'          CSV HEADER;
\COPY calendar       FROM 'calendar.txt'        CSV HEADER;
\COPY calendar_dates FROM 'calendar_dates.txt'  CSV HEADER;
\COPY shapes         FROM 'shapes.txt'          CSV HEADER;
\COPY stops          FROM 'stops.txt'           CSV HEADER;
\COPY trips          FROM 'trips.txt'           CSV HEADER;
\COPY stop_times     FROM 'stop_times.txt'      CSV HEADER;
\COPY transfers      FROM 'transfers.txt'       CSV HEADER;
*/