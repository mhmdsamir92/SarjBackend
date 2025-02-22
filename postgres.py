import os
import psycopg2

conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])

def get_cursor():
    return conn.cursor()

def commit():
    conn.commit()

def close_connection():
    conn.close()

