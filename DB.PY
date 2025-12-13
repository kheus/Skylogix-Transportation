# create database via python
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'skylogix_db'),
    user=os.getenv('POSTGRES_USER', 'skylogix_user'),
    password=os.getenv('POSTGRES_PASSWORD', 'skylogix_pass'),
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432')
)

conn.autocommit = True
cur = conn.cursor() 

cur.execute("CREATE DATABASE skylogix_db;")

cur.close()
conn.close()

# create table via python
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'skylogix_db'),
    user=os.getenv('POSTGRES_USER', 'skylogix_user'),
    password=os.getenv('POSTGRES_PASSWORD', 'skylogix_pass'),
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432')
)

conn.autocommit = True
cur = conn.cursor()

with open('create_table.sql', 'r') as f:
    sql = f.read()
    cur.execute(sql)
conn.commit()

cur.close()
conn.close()

print("Database and table created successfully.")