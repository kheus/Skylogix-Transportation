import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

# Force load .env (Windows-safe)
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY not found. Check your .env file")

DB_NAME = "skylogix"
COLLECTION_NAME = "weather_raw"

cities = [
    {"name": "Nairobi", "country": "KE"},
    {"name": "Lagos", "country": "NG"},
    {"name": "Accra", "country": "GH"},
    {"name": "Johannesburg", "country": "ZA"},
]

def fetch_weather(city, country):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city},{country}&appid={API_KEY}"
    )
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error for {city}: {response.text}")

def upsert_to_mongo(data):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    city = data["name"]
    dt = data["dt"]
    doc_id = f"{city}_{dt}"

    data["updatedAt"] = datetime.utcnow()

    collection.update_one(
        {"_id": doc_id},
        {"$set": data},
        upsert=True,
    )

    print(f"Upserted data for {city}")

if __name__ == "__main__":
    for city in cities:
        raw_data = fetch_weather(city["name"], city["country"])
        upsert_to_mongo(raw_data)
