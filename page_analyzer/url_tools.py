import validators
import requests
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup


def validate(url):
    errors = []
    if not validators.url(url):
        errors.append('Некорректный URL')
    elif not url:
        errors.append('URL обязателен')
    elif len(url) > 255:
        errors.append('URL превышает 255 символов')
    return errors


def normalize_url(input_url):
    url_parts = list(urlsplit(input_url))
    normalized = [url_parts[0], url_parts[1], '', '', '']
    return urlunsplit(normalized)


def parse_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    h1_tag = soup.find('h1')
    title_tag = soup.find('title')
    description_tag = soup.find('meta', attrs={'name': 'description'})
    h1 = h1_tag.text.strip() if h1_tag else ''
    title = title_tag.text.strip() if title_tag else ''
    description = description_tag['content'].strip() if description_tag else ''
    return h1, title, description


def get_check_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(e)
    h1, title, description = parse_content(response.text)
    status_code = response.status_code
    return [status_code, h1, title, description]
