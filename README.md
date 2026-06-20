# ListenBrainz Data Pipeline

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- Python 3.11 ([pyenv](https://github.com/pyenv/pyenv) recommended)

## Setup

**1. Clone the repo and enter the directory**
```bash
git clone <repo-url>
cd scalable-challenge-2026
```

**2. Add the dataset**

Download `sample.jsonl` from the provided Google Drive link and place it at:
```
data/sample.jsonl
```

**3. (Optional) Generate a large test dataset**

`data/generate.py` produces a 100k-record JSONL file with valid records, duplicates, and intentionally invalid records (null keys, bad timestamps) to verify the pipeline's idempotency and error handling at scale:

```bash
python data/generate.py
# outputs data/large_sample.jsonl
# 100,000 valid | 2,000 duplicates | 500 invalid
```

To run the pipeline against it instead of the real dataset:
```bash
DATA_PATH=data/large_sample.jsonl python pipeline.py
```

**4. Run with Docker (recommended)**
```bash
docker compose up --build
```

The Prefect UI is available at [localhost:4200](http://localhost:4200) once the server is healthy (~15 seconds). It's an optional way to view the DAG of the different steps of the data pipeline.

**5. Run locally (without Docker)**
```bash
pyenv install 3.11.9
pyenv local 3.11.9
make install
make pipeline   # run the ingestion pipeline
make queries    # run the analysis queries
```

## All make commands

| Command | Description |
|---|---|
| `make run` | Start full stack with Docker (includes Prefect UI) |
| `make install` | Install Python dependencies locally |
| `make pipeline` | Run ingestion pipeline locally |
| `make queries` | Run analysis queries locally |
| `make generate` | Generate 100k-record test dataset |
| `make clean` | Remove `listens.db` and generated JSONL |
