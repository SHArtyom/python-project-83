install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run flake8 page_analyzer

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

dev:
	poetry run flask --app page_analyzer:app --debug run

init_db:
	db_create schema-load

db_create:
	createdb page_seo || echo 'skip'

schema-load:
	psql page_seo < database.sql

