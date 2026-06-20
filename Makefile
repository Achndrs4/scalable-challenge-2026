.PHONY: run venv install pipeline queries generate test dbt clean

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

dbt:
	.venv/bin/dbt run --project-dir dbt --profiles-dir dbt
	.venv/bin/dbt test --project-dir dbt --profiles-dir dbt

clean:
	rm -f listens.db data/large_sample.jsonl
