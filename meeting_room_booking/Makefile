.PHONY: run migrate createsuperuser celery test build run-local createsuperuser-local celery-local test-local create_init

# Docker commands
run:
	docker-compose up -d web

migrate:
	docker-compose run web python manage.py migrate

createsuperuser:
	docker-compose run web python manage.py createsuperuser

celery:
	docker-compose up -d celery

test:
	docker-compose run tests

build:
	docker-compose build

# Local commands
run-local:
	python manage.py runserver 0.0.0.0:8000

createsuperuser-local:
	python manage.py createsuperuser

celery-local:
	celery -A meeting_room_booking worker --loglevel=info

test-local:
	python manage.py test -v 2

create_init:
	mkdir "media" && pip install -r requirements.txt && python manage.py migrate