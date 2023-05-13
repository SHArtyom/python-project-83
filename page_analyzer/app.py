from flask import Flask, flash, get_flashed_messages, \
    render_template, request, redirect, url_for
from psycopg2.extras import NamedTupleCursor
import psycopg2
import datetime
import validators
import os
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def connect():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print('Connected to database')
    except Exception:
        print('Can`t establish connection to database')
    return conn


def validate(url):
    if not validators.url(url):
        return 'Некорректный URL'
    elif len(url) > 255:
        return 'Длина URL не должна превышеть 255 символов'
    return


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        url = request.form.get('url')
        errors = validate(url)
        if errors:
            flash(errors, 'danger')
            return redirect(url_for('index'))
        conn = connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name=(%s)', (url,))
            existing_url = cursor.fetchone()
        if existing_url:
            flash('Страница уже существует', 'info')
            id = existing_url.id
            return redirect(url_for('url_details', id=id))
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('INSERT INTO urls \
                           (name, created_at) VALUES (%s, %s)',
                           (url, datetime.datetime.now()))
        conn.commit()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name=(%s)', (url,))
            id = cursor.fetchone().id
        conn.close()
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_details', id=id))
    if request.method == 'GET':
        conn = connect()
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('SELECT * FROM urls ORDER BY id DESC')
            url_list = cursor.fetchall()
        conn.close()
        return render_template('urls.html', url_list=url_list)


@app.route('/urls/<id>', methods=['GET'])
def url_details(id):
    messages = get_flashed_messages(with_categories=True)
    conn = connect()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls WHERE id=%s', (id,))
        url = cursor.fetchone()
    conn.close()
    return render_template('url_details.html', url=url, messages=messages)
