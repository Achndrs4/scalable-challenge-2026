import os

from prefect import flow

from db import DATA_PATH
from ingest import ingest, setup
from transform import dbt_run
from validate import validate


@flow(name="Listens Pipeline", log_prints=True)
def run(path: str = DATA_PATH) -> None:
    setup()
    clean_path = validate(path)
    try:
        inserted = ingest(clean_path)
        dbt_run()
    finally:
        os.unlink(clean_path)
    print(f"Pipeline complete: {inserted} new records ingested.")


if __name__ == "__main__":
    run()
