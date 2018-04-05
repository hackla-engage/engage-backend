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
	docker-compose run ${DJANGO_CONTAINER} bash

.PHONY: shell
shell:
	docker-compose run ${DJANGO_CONTAINER} python manage.py shell --settings=CouncilTag.docker_settings

dbshell:
	docker-compose run ${DJANGO_CONTAINER} python manage.py dbshell --settings=CouncilTag.docker_settings

createsuperuser:
	docker-compose run ${DJANGO_CONTAINER} python manage.py createsuperuser --settings=CouncilTag.docker_settings

.PHONY: migrate
migrate:
	docker-compose run ${DJANGO_CONTAINER} python manage.py migrate --settings=CouncilTag.docker_settings

populate_tags:
	docker-compose run ${DJANGO_CONTAINER} python manage.py populate_tags --settings=CouncilTag.docker_settings

scrape_data:
	docker-compose run ${DJANGO_CONTAINER} python manage.py scrape_data --settings=CouncilTag.docker_settings

setup: build migrate