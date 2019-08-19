PIP=pip3
PYTHON=python3

.PHONY:
	init test collectstatic run

default: test

.DEFAULT_GOAL: test

init:
	$(PIP) install -r requirements.txt

test: test_bigboxx test_api

test_bigboxx:
	$(PYTHON) ./manage.py test ./bigboxx/tests

test_api:
	$(PYTHON) ./manage.py test ./apps/api/tests

collectstatic:
	rm -rf ./static
	$(PYTHON) ./manage.py collectstatic

migrations:
	$(PYTHON) ./manage.py makemigrations

migrate:
	$(PYTHON) ./manage.py migrate

run: migrate
	$(PYTHON) ./manage.py runserver 0.0.0.0:8800
