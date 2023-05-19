from flask import Flask, flash, get_flashed_messages, \
    render_template, request, redirect, url_for
from datetime import datetime as date
from dotenv import load_dotenv
from page_analyzer.db_connect import make_query_get, make_query_set
from page_analyzer.url_tools import validate, normalize_url, get_check_data
import os

MSG_SUCCESS = 'Страница успешно добавлена'
MSG_EXISTS = 'Страница уже существует'
MSG_ADDED = 'Страница успешно добавлена'
MSG_ERROR = 'Произошла ошибка при проверке'
MSG_CHECK = 'Страница успешно проверена'


load_dotenv()


app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def urls():
    if request.method == 'POST':
        input_url = request.form.get('url')
        errors = validate(input_url)
        if errors:
            for error in errors:
                flash(error, 'danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template('index.html', messages=messages,
                                   input_url=input_url), 422
        url = normalize_url(input_url)
        existing_url = make_query_get('SELECT * FROM urls WHERE name=(%s)', url)
        if existing_url:
            flash(MSG_EXISTS, 'info')
            id = existing_url.id
            return redirect(url_for('url_details', id=id))
        make_query_set('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                       url, date.now())
        id = make_query_get('SELECT * FROM urls WHERE name=(%s)', url).id
        flash(MSG_ADDED, 'success')
        return redirect(url_for('url_details', id=id))


@app.get('/urls')
def get_urls():
    query = 'SELECT DISTINCT ON (urls.id) urls.id, name, \
             url_checks.created_at, status_code from urls \
             LEFT JOIN url_checks on urls.id=url_checks.url_id \
             ORDER BY urls.id DESC'
    url_list = make_query_get(query, fetch='all')
    return render_template('urls.html', url_list=url_list)


@app.get('/urls/<int:id>')
def url_details(id: int):
    messages = get_flashed_messages(with_categories=True)
    url = make_query_get('SELECT * FROM urls WHERE id=%s', id)
    checks = make_query_get("SELECT * FROM url_checks WHERE url_id=(%s) ORDER \
                            BY id DESC", id, fetch='all')
    return render_template('url_details.html', url=url,
                           checks=checks, messages=messages)


@app.post('/urls/<int:id>/checks')
def url_checks(id: int):
    url = make_query_get('SELECT name FROM urls WHERE id=%s', id).name
    check_data = get_check_data(url)
    if check_data == 1:
        flash(MSG_ERROR, 'danger')
        return redirect(url_for('url_details', id=id))
    make_query_set('INSERT INTO url_checks (url_id, status_code, h1, \
                   title, description, created_at) \
                   VALUES (%s, %s, %s, %s, %s, %s)',
                   id, *check_data, date.now())
    flash(MSG_CHECK, 'success')
    return redirect(url_for('url_details', id=id))
