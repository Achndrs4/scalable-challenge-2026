.PHONY: run venv install pipeline queries generate test test-large lint dbt clean reset

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

test-large:
	.venv/bin/python data/generate.py
	DATA_PATH=data/large_sample.jsonl .venv/bin/python pipeline.py

lint:
	.venv/bin/ruff check .

dbt:
	.venv/bin/dbt run  --project-dir dbt --profiles-dir dbt --vars '{"data_path": "$(DATA_PATH)"}'
	.venv/bin/dbt test --project-dir dbt --profiles-dir dbt --vars '{"data_path": "$(DATA_PATH)"}'

clean:
	-docker compose down
	rm -rf data/large_sample.jsonl dbt/target/ dbt/dbt_packages/ dbt/logs/ .pytest_cache/

reset: clean
	rm -f data/listens.db
