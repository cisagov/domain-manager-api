.PHONY: all help build logs loc up stop down shell test

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

# target: restart - Stop and restart all containers
restart:
	docker-compose stop api
	docker-compose up -d
	docker attach --sig-proxy=false dm-api

# target: up - Run local web server.
up:
	 docker-compose up -d

# target: stop - Stop all docker containers
stop:
	docker-compose stop

# target: down - Remove all docker containers
down:
	docker-compose down

# target: shell - python shell within container
shell:
	docker exec -it dm-api python3

# target: test - run unit tests
test:
	docker exec -it dm-api coverage run -m pytest --disable-warnings
	docker exec dm-api coverage report -i

lint:
	pre-commit autoupdate
	pre-commit run --all-files

refresh:
	docker restart dm-api

ra:	refresh	attach
