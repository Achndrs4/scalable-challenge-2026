.PHONY: run venv install pipeline queries generate test test-large lint dbt clean reset

run:
	docker compose up --build

venv:
	uv venv .venv

install:
	uv sync

pipeline:
	.venv/bin/python pipeline.py

queries:
	.venv/bin/python queries.py

generate:
	.venv/bin/python data/generate.py

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
