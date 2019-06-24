#!/bin/bash
pipenv run pip install --upgrade pip
pipenv install 
export CouncilTag=test
pipenv run python manage.py migrate
pipenv run python manage.py populate_tags
pipenv run python manage.py collectstatic --no-input
pipenv run python manage.py runserver 0.0.0.0:8000
