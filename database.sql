DROP TABLE IF EXISTS urls CASCADE;
DROP TABLE IF EXISTS url_checks CASCADE;

CREATE TABLE urls (
id SERIAL PRIMARY KEY,
name varchar(255) UNIQUE,
created_at date
);

CREATE TABLE url_checks (
id SERIAL PRIMARY KEY,
url_id integer REFERENCES urls(id),
status_code integer,
h1 varchar(255),
title varchar(255),
description text,
created_at date
);
