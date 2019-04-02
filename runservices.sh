#!/bin/bash
pipenv run pip install --upgrade pip
pipenv install 
export CouncilTag=test
pipenv run python manage.py migrate
pipenv run python manage.py populate_tags
pipenv run python manage.py collectstatic --no-input
export CouncilTag=celery
pipenv run python manage.py scrape_data --years 2019 --committee "Santa Monica City Council"
pipenv run celery -A CouncilTag worker -E -l debug -n worker0&
pipenv run celery -A CouncilTag beat -l debug --scheduler django_celery_beat.schedulers:DatabaseScheduler&
pipenv run python manage.py runserver 0.0.0.0:8000
