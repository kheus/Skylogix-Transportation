# ingestion.py
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY', '09bdb7f1a2ea114f3f63a2017a89d548')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'skylogix'
COLLECTION_NAME = 'weather_raw'

cities = [
    {'name': 'Nairobi', 'country': 'KE'},
    {'name': 'Lagos', 'country': 'NG'},
    {'name': 'Accra', 'country': 'GH'},
    {'name': 'Johannesburg', 'country': 'ZA'}
]

def fetch_weather(city, country):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error for {city}: {response.text}")

def upsert_to_mongo(data):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Construct unique key: city + observed dt (from API)
    city = data['name']
    dt = data['dt']  # Unix timestamp from API
    observed_at = datetime.utcfromtimestamp(dt)
    doc_id = f"{city}_{dt}"
    
    # Add updatedAt
    data['updatedAt'] = datetime.utcnow()
    
    # Upsert
    collection.update_one(
        {'_id': doc_id},
        {'$set': data},
        upsert=True
    )
    print(f"Upserted data for {city}")

if __name__ == "__main__":
    for city in cities:
        raw_data = fetch_weather(city['name'], city['country'])
        upsert_to_mongo(raw_data)