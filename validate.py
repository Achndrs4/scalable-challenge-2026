import json
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from prefect import task
from db import DATA_PATH


def _validate_chunk(lines: list) -> tuple:
    valid = []
    rejected = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            rejected += 1
            continue
        try:
            if isinstance(json.loads(stripped), dict):
                valid.append(stripped)
            else:
                rejected += 1
        except json.JSONDecodeError:
            rejected += 1
    return valid, rejected


@task(name="Validate JSONL", retries=2, retry_delay_seconds=10)
def validate(path: str = DATA_PATH) -> str:
    workers = os.cpu_count() or 4

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    chunk_size = max(1, len(lines) // workers)
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(_validate_chunk, chunks))

    valid_lines = [line for chunk_valid, _ in results for line in chunk_valid]
    total_rejected = sum(rejected for _, rejected in results)

    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".jsonl", delete=False)
    tmp.writelines(f"{line}\n" for line in valid_lines)
    tmp.close()

    print(f"Validated {len(lines):,} lines: {len(valid_lines):,} valid, {total_rejected:,} malformed rejected")
    return tmp.name
