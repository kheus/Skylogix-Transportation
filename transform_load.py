import pymongo
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os

# Force load .env (Windows-safe)
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
POSTGRES_URI = os.getenv("POSTGRES_URI")

if not POSTGRES_URI:
    raise RuntimeError("POSTGRES_URI not found. Check your .env file")

def transform_and_load():
    mongo = pymongo.MongoClient(MONGO_URI)
    raw_col = mongo.skylogix.weather_raw
    cutoff = datetime.utcnow() - timedelta(hours=1)

    docs = list(raw_col.find({"updatedAt": {"$gte": cutoff}}))

    if not docs:
        print("No new data to transform")
        return

    conn = psycopg2.connect(POSTGRES_URI)
    cur = conn.cursor()

    for doc in docs:
        w = doc.get("weather", [{}])[0]
        main = doc.get("main", {})
        wind = doc.get("wind", {})
        clouds = doc.get("clouds", {})
        rain = doc.get("rain", {})
        snow = doc.get("snow", {})
        coord = doc.get("coord", {})

        sql = """
        INSERT INTO weather_readings (
            city, country, observed_at, lat, lon, temp_c, feels_like_c,
            pressure_hpa, humidity_pct, wind_speed_ms, wind_deg, cloud_pct,
            visibility_m, rain_1h_mm, snow_1h_mm,
            condition_main, condition_description, ingested_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (city, observed_at)
        DO UPDATE SET
            temp_c = EXCLUDED.temp_c,
            rain_1h_mm = EXCLUDED.rain_1h_mm,
            ingested_at = EXCLUDED.ingested_at;
        """

        cur.execute(sql, (
            doc["name"],
            doc["sys"]["country"],
            datetime.fromtimestamp(doc["dt"]),
            coord.get("lat"), coord.get("lon"),
            main.get("temp"), main.get("feels_like"),
            main.get("pressure"), main.get("humidity"),
            wind.get("speed"), wind.get("deg"),
            clouds.get("all"), doc.get("visibility"),
            rain.get("1h", 0.0), snow.get("1h", 0.0),
            w.get("main"), w.get("description"),
            datetime.utcnow()
        ))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Loaded {len(docs)} records into PostgreSQL")

if __name__ == "__main__":
    transform_and_load()
