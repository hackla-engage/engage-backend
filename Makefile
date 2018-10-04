DJANGO_CONTAINER := web

.PHONY: all
all: run

.PHONY: run
run:
	docker-compose up

.PHONY: bg
bg:
	docker-compose up -d

.PHONY: open
open:
	open http://localhost:8000

.PHONY: build
build:
	docker-compose build

bash:
	docker-compose run --rm ${DJANGO_CONTAINER} bash

.PHONY: shell
shell:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py shell

dbshell:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py dbshell

createsuperuser:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py createsuperuser

test:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py test -k

.PHONY: migrate
migrate:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py migrate

populate_tags:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py populate_tags

process_comments:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py process_agenda_comments

scrape_data:
	docker-compose run --rm ${DJANGO_CONTAINER} python manage.py scrape_data --years 2018

setup: build migrate