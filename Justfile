DOCKER_COMPOSE_DEV := "docker-compose-local.yaml"

#All command section
[private]
default:
	@just --list --unsorted

#Prepare venv and repo for developing
@bootstrap:
	cp .env.dist .env
	python3 -m pip install uv
	uv pip install -e "[dev]"
	pre-commit install

#Lint files
@lint:
	ruff check --fix
	ruff format

#Run docker container
@up:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} up --build -d

@stop:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} stop

@down:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} down

@static:
	mypy --config-file pyproject.toml

@test:
	pytest tests/
