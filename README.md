# Data Pipeline Installation Instructions
![Data Architecture](img/architecture.png)


## Design Choices
For insights relating to structure and architecture, please read [Challenge.md](Challenge.md)

## Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — install with `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Setup

**1. Clone the repo and enter the directory**
```bash
git clone <repo-url>
cd scalable-challenge-2026
```

**2. Create your .env file**
Copy the example and verify the data path points to the included sample file:
```bash
cp .env.example .env
```
The `.env.example` is pre-configured to use `data/dataset-sample.jsonl`, which is included in the repo.

**3. Run with Docker Compose (recommended)**

The following command starts two docker containers — a Prefect orchestration server for visually viewing results and the data pipeline.

```bash
make build   # build the image (first time, or after changing dependencies)
make run     # start the stack using the cached image
```

The two services are:

| Service | Role |
|---|---|
| `prefect-server` | Prefect UI to view pipeline status, runs, and restarts [localhost:4200](http://localhost:4200) |
| `data-intake` | Runs the full pipeline (validate → dbt run → dbt test) |

The pipeline container waits for the Prefect server health check before starting. Once complete, the `listens` table is available inside the `db` Docker volume.

**4. Restart Service**
If you want to restart the service, simply run:
```bash
make clean
```
This removes temporary files and brings the Docker containers down.

**5. View the Prefect UI (optional)**

Open [localhost:4200](http://localhost:4200) once the server is healthy (~15 seconds). The UI shows each pipeline stage (Validate JSONL, dbt Transform & Test) with timing, logs, and retry state.

![Prefect UI](img/prefect.png)

**6. Run locally (without Docker)**
Make sure you have completed step 2 (`.env` file). If you don't have `uv` installed yet:
```bash
brew install uv          # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then install dependencies and run:
```bash
uv venv .venv --python 3.11
uv sync
make pipeline  
make queries    
```

## All make commands

| Command | Description |
|---|---|
| `make build` | Build the Docker image |
| `make run` | Start full stack with Docker using the cached image (includes Prefect UI) |
| `make install` | Install Python dependencies locally via uv |
| `make pipeline` | Run ingestion pipeline locally |
| `make queries` | Run analysis queries locally |
| `make dbt DATA_PATH=data/dataset-sample.jsonl` | Run dbt models and tests standalone |
| `make clean` | Remove temporary files and bring Docker containers down |
| `make reset` | Full reset — also deletes the local database |
