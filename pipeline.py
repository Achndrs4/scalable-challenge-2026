import os

from prefect import flow

from db import DATA_PATH
from transform import dbt_run
from validate import validate


@flow(name="Listens Data Pipeline", log_prints=True)
def run(path: str = DATA_PATH) -> None:
    # first, do parallel processing on the file in python (for a huge file, you can use a MapReduce to extend this work across several machines)
    clean_path = validate(path)
    try:
        # then, run our data models
        dbt_run(clean_path)
    finally:
        os.unlink(clean_path)
    print("Pipeline complete.")


if __name__ == "__main__":
    run()
