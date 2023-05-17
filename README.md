# Page analyzer
[![hexlet-check](https://github.com/SHArtyom/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SHArtyom/python-project-83/actions/workflows/hexlet-check.yml)
[![lint_check](https://github.com/SHArtyom/python-project-83/actions/workflows/Lint_check.yml/badge.svg)](https://github.com/SHArtyom/python-project-83/actions/workflows/Lint_check.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/da6d168f994cbb579606/maintainability)](https://codeclimate.com/github/SHArtyom/python-project-83/maintainability)

____
## About:
Page analyzer is a small web-interface application for SEO quality assurance tests similar to [PageSpeed Insights](https://pagespeed.web.dev/).
You can check out the application via link below

[Page analyzer](https://python-project-83-production-ac21.up.railway.app/)
____
#### Minimum requirements:
Python 3.9

Installed PostgreSQL 12.14
#### Installation:
Create database tables and structure:
```make init_db```

Setup dependencies:
```make install```

To start gunicorn WSGI run:
```make start```

To start local dev server run:
```make dev```

If you are going to run application locally make sure you put '.env' file in the root directory of the project. The file must contain local variables:
```
DATABASE_URL = {provider}://{user}:{password}@{host}:{port}/{db}
SECRET_KEY = "..."
```
