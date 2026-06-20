import os
from prefect import flow
from db import DATA_PATH
from validate import validate
from ingest import setup, ingest
from transform import dbt_run


@flow(name="Listens Pipeline", log_prints=True)
def run(path: str = DATA_PATH) -> None:
    setup()
    clean_path = validate(path)
    inserted = ingest(clean_path)
    dbt_run()
    os.unlink(clean_path)
    print(f"Pipeline complete: {inserted} new records ingested.")


if __name__ == "__main__":
    run()
