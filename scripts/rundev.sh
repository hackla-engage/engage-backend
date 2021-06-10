#!/bin/sh
export ENGAGE_DATABASE=True
python manage.py makemigrations
python manage.py migrate
export ENGAGE_DATABASE=False
python manage.py collectstatic --no-input
python manage.py runserver 0.0.0.0:8000
