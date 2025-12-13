-- create_table.sql
CREATE TABLE IF NOT EXISTS weather_readings (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    lat NUMERIC(9,6),
    lon NUMERIC(9,6),
    temp_c NUMERIC(5,2),
    feels_like_c NUMERIC(5,2),
    pressure_hpa INTEGER,
    humidity_pct INTEGER,
    wind_speed_ms NUMERIC(6,2),
    wind_deg INTEGER,
    cloud_pct INTEGER,
    visibility_m INTEGER,
    rain_1h_mm NUMERIC(6,2) DEFAULT 0.0,
    snow_1h_mm NUMERIC(6,2) DEFAULT 0.0,
    condition_main VARCHAR(50),
    condition_description VARCHAR(100),
    ingested_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_city_observed UNIQUE (city, observed_at)
);

CREATE INDEX IF NOT EXISTS idx_city_observed ON weather_readings(city, observed_at DESC);
