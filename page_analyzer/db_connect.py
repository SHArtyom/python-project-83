import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception:
        print("Can't establish connection to database")
    return conn


def make_query_get(query, *args, fetch=''):
    conn = connect()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(query, args)
        data = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
    conn.close()
    return data


def make_query_set(query, *args):
    conn = connect()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(query, args)
    conn.commit()
    conn.close()
    return
