import json
import shutil
import subprocess

from prefect import task


@task(name="dbt Transform & Test", retries=2, retry_delay_seconds=10)
def dbt_run(path: str) -> None:
    dbt = shutil.which("dbt") or ".venv/bin/dbt"
    flags = ["--project-dir", "dbt", "--profiles-dir", "dbt", "--vars", json.dumps({"data_path": path})]
    # creates relevant tables/views in DBT
    subprocess.run([dbt, "run", *flags], check=True)
    # checks that the data is valid
    subprocess.run([dbt, "test", *flags], check=True)
