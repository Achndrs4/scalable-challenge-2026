import shutil
import subprocess

from prefect import task


@task(name="dbt Transform & Test", retries=2, retry_delay_seconds=10)
def dbt_run() -> None:
    dbt = shutil.which("dbt") or ".venv/bin/dbt"
    flags = ["--project-dir", "dbt", "--profiles-dir", "dbt"]
    subprocess.run([dbt, "run",  *flags], check=True)
    subprocess.run([dbt, "test", *flags], check=True)
