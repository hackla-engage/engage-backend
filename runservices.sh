#!/bin/bash
pipenv install 
export AWS_REGION=us-east-1
export CouncilTag=test
pipenv run python manage.py migrate
pipenv run python manage.py populate_tags
export CouncilTag=debug
# pipenv run python manage.py scrape_data --years 2018 --committee "Santa Monica City Council"
pipenv run celery -A CouncilTag worker -E -l debug -n worker0&
pipenv run celery -A CouncilTag beat -l debug --scheduler django_celery_beat.schedulers:DatabaseScheduler&
pipenv run python manage.py runserver 0.0.0.0:8000
