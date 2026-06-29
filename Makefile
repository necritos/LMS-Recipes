.PHONY: install up down migrate test run lint shell worker

install:
	pip install -e ".[dev]"

up:
	docker compose up -d redis

down:
	docker compose down

worker:
	celery -A config worker -l info

migrate:
	python manage.py migrate

seed-languages:
	python manage.py seed_languages

test:
	pytest

run:
	python manage.py runserver

lint:
	ruff check .
	ruff format --check .

shell:
	python manage.py shell
