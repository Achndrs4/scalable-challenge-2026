import os

from prefect import flow

from db import DATA_PATH
from transform import dbt_run
from validate import validate


@flow(name="Listens Pipeline", log_prints=True)
def run(path: str = DATA_PATH) -> None:
    clean_path = validate(path)
    try:
        dbt_run(clean_path)
    finally:
        os.unlink(clean_path)
    print("Pipeline complete.")


if __name__ == "__main__":
    run()
