from psycopg2.extras import NamedTupleCursor
from datetime import datetime as date
from dotenv import load_dotenv
import psycopg2
import os


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    return psycopg2.connect(DATABASE_URL)


def get_from_db(query, value=None, fetch=''):
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, (value,))
            data = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
    return data


def add_to_db(query, *args):
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(query, (*args,))
        conn.commit()


def get_url(search_by, value):
    if search_by == 'name':
        query = 'SELECT * FROM urls WHERE name=%s'
    elif search_by == 'id':
        query = 'SELECT * FROM urls WHERE id=%s'
    else:
        raise ValueError('Invalid query parameter in get_url function')
    return get_from_db(query, value)


def get_url_list():
    query ='SELECT DISTINCT ON (urls.id) \
            urls.id, name, url_checks.created_at, status_code \
            FROM urls LEFT JOIN url_checks \
            ON urls.id=url_id \
            ORDER BY urls.id DESC'
    return get_from_db(query, fetch='all')


def add_url_to_base(url):
    query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s);'
    add_to_db(query, url, date.now())
    return


def add_check_to_base(id, check_data):
    query = 'INSERT INTO url_checks \
            (url_id, status_code, h1, title, description, created_at) \
            VALUES (%s, %s, %s, %s, %s, %s)'
    add_to_db(query, id, *check_data, date.now())
    return


def get_urls_with_checks(id):
    query = 'SELECT name, urls.created_at as url_created_at, urls.id, \
            url_checks.id as check_id, status_code, h1, title, \
            description, url_checks.created_at as check_created_at \
            FROM urls LEFT JOIN url_checks \
            ON urls.id=url_id WHERE urls.id=%s \
            ORDER BY url_checks.id DESC'
    return get_from_db(query, id, fetch='all')
