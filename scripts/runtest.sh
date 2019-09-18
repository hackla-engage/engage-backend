#!/bin/bash
pip install -r requirements.txt
export ENGAGE_DATABASE=True
python manage.py makemigrations
python manage.py migrate
export ENGAGE_DATABASE=False
python manage.py collectstatic --no-input
if [ -d "tmp" ]; then
    rm -rf tmp
fi
mkdir tmp
python manage.py test -k > tmp/tests-results 2>&1