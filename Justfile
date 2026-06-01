set dotenv-load := true

DOCKER_COMPOSE_DEV := "docker-compose-local.yaml"

#All command section
[private]
default:
	@just --list --unsorted

#Prepare venv and repo for developing
@bootstrap:
	cp .env.dist .env
	python3 -m pip install uv
	uv sync --group dev
	pre-commit install
	export $(grep -v '^#' .env | xargs)


#Lint files
@lint:
	ruff check --fix
	ruff format

#Run docker container
@up:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} up --build -d
	export $(grep -v '^#' .env | xargs)

#Stop docker container
@stop:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} stop

#Down docker container
@down:
	docker compose -f {{ DOCKER_COMPOSE_DEV }} down

#Static mypy check
@static:
	mypy --config-file pyproject.toml

#Run tests
@test:
	pytest tests/

#Run tests with HTML coverage report (open htmlcov/index.html)
@cov:
	pytest tests/ --cov-report=html
#Run API server (uvicorn)
@uvicorn:
	PYTHONPATH=src uvicorn trafficmaster.web:create_fastapi_app --factory
