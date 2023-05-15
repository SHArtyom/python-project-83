from flask import Flask, flash, get_flashed_messages, \
    render_template, request, redirect, url_for
from psycopg2.extras import NamedTupleCursor
import psycopg2
import datetime
import validators
import os
import requests
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
    errors = []
    if not validators.url(url):
        errors.append('Некорректный URL')
    if not url:
        errors.append('URL обязателен')
    if len(url) > 255:
        errors.append('Длина URL не должна превышеть 255 символов')
    return errors


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
            for error in errors:
                flash(error, 'danger')
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
            cursor.execute('SELECT DISTINCT ON (urls.id) urls.id, name, \
                           url_checks.created_at, status_code from urls \
                           LEFT JOIN url_checks on urls.id=url_checks.url_id \
                           ORDER BY urls.id DESC')
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
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM url_checks WHERE url_id=(%s) \
                       ORDER BY id DESC', (id,))
        checks = cursor.fetchall()
    conn.close()
    return render_template('url_details.html', url=url,
                           checks=checks, messages=messages)


@app.route('/urls/<id>/checks', methods=['POST'])
def url_checks(id):
    conn = connect()
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
        url = cursor.fetchone().name
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_details', id=id))
    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute('INSERT INTO url_checks \
                       (url_id, status_code, created_at) VALUES (%s, %s, %s)',
                       (id, response.status_code, datetime.datetime.now()))
    conn.commit()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_details', id=id))
