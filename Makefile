.PHONY: all help bash build logs loc up stop down shell test ra refresh categorize check_category

# make all - Default Target. Does nothing.
all:
	@echo "Flask helper commands."
	@echo "For more information try 'make help'."

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: build = build all containers
build:
	docker-compose build

# target: init = load initial data to database
init:
	docker exec -it dm-api python scripts/initialize.py

# target: attach logs - Runs flask logs in the terminal
attach:
	 docker attach --sig-proxy=false dm-api

# target: print logs - Print api logs in the terminal
logs:
	 docker logs dm-api

# target: loc - Count lines of code.
loc:
	 loc src

# target: restart - Stop and restart api container
restart:
	docker compose restart api
	docker attach --sig-proxy=false dm-api

# target: up - Run local web server.
up:
	 docker compose up -d

# target: stop - Stop all docker containers
stop:
	docker compose stop

# target: down - Remove all docker containers
down:
	docker compose down

# target: bash - bash into container
bash:
	docker exec -it dm-api bash

# target: shell - python shell within container
shell:
	docker exec -it dm-api python3

# target: test - run unit tests
test:
	docker exec -it dm-api coverage run -m pytest --disable-warnings -s
	docker exec dm-api coverage report -i

# target: lint - run pre-commit linting
lint:
	pre-commit autoupdate
	pre-commit run --all-files

# target: refresh - restart the api container
refresh:
	docker restart dm-api

# target: ra - refresh api and attach logs
ra: refresh	attach

# target: categorize - test run categorize lambda function on a specified domain
categorize:
	python -m proxy_harness.categorize

# target: check_category - test run check categories on a specified domain
check_category:
	python -m proxy_harness.check_category
