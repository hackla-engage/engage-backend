#!/bin/sh
python manage.py makemigrations
python manage.py migrate
export ENGAGE_DATABASE=False
python manage.py runserver 0.0.0.0:8000
