import os

import duckdb
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "listens.db")
DATA_PATH = os.getenv("DATA_PATH", "data/dataset-sample.jsonl")


def connect(db_path: str = DB_PATH) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(db_path)
