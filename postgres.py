import os
import psycopg2

def get_conn():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

def get_cursor(conn):
    return conn.cursor()

def commit(conn):
    conn.commit()

