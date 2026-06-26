DATA_PATH ?= data/dataset-sample.jsonl

.PHONY: run build venv install pipeline queries test lint dbt clean reset

run:
	docker compose up

build:
	docker compose build

venv:
	uv venv .venv

install:
	uv sync

pipeline:
	.venv/bin/python pipeline.py

queries:
	.venv/bin/python queries.py

test:
	.venv/bin/pytest tests/ -v

lint:
	.venv/bin/ruff check .

dbt:
	.venv/bin/dbt run  --project-dir dbt --profiles-dir dbt --vars '{"data_path": "$(DATA_PATH)"}'
	.venv/bin/dbt test --project-dir dbt --profiles-dir dbt --vars '{"data_path": "$(DATA_PATH)"}'

clean:
	-docker compose down
	rm -rf dbt/target/ dbt/dbt_packages/ dbt/logs/ .pytest_cache/

reset: clean
	rm -f data/listens.db
