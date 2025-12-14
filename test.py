
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_DSN = os.getenv("POSTGRES_DSN")

print("POSTGRES_URI =", POSTGRES_DSN)
