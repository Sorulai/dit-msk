.PHONY: run migrate createsuperuser celery test build run-local migrate-local createsuperuser-local celery-local test-local install-reqs

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

migrate-local:
	python manage.py migrate

createsuperuser-local:
	python manage.py createsuperuser

celery-local:
	celery -A meeting_room_booking worker --loglevel=info

test-local:
	python manage.py test -v 2

install-reqs:
	pip install -r requirements.txt