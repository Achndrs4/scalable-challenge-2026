.PHONY: run venv install pipeline queries generate test lint dbt clean

run:
	docker compose up --build

venv:
	python -m venv .venv

install:
	.venv/bin/pip install -r requirements.txt

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
	.venv/bin/dbt run --project-dir dbt --profiles-dir dbt
	.venv/bin/dbt test --project-dir dbt --profiles-dir dbt

clean:
	rm -rf data/listens.db data/large_sample.jsonl dbt/target/ dbt/dbt_packages/ dbt/logs/ .pytest_cache/
