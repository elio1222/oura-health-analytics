# Oura Health Analytics

Oura Health Analytics is a FastAPI service that pulls data from the Oura API, stores both raw and processed records in PostgreSQL, computes custom health summaries, and generates AI-assisted insights from recent sleep, readiness, stress, and activity data.

## What This Project Does

- Connects to the Oura API using OAuth.
- Fetches Oura data for:
  - personal info
  - daily sleep
  - sleep periods / routes
  - daily readiness
  - daily stress
  - daily activity
- Stores raw API responses in database-backed raw tables.
- Transforms raw records into processed analytics tables.
- Exposes REST endpoints for querying data and summaries.
- Uses OpenAI structured outputs to generate human-readable health insights.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn
- Docker / Docker Compose
- OpenAI API

## High-Level Architecture

The codebase is organized around four main layers:

1. `app/main.py`
   Runs the FastAPI application and exposes the HTTP endpoints.

2. `app/services/`
   Handles external integrations and business logic:
   - `oura_service.py`: OAuth, token refresh, Oura API fetching
   - `analytics_service.py`: summary calculations and transformed response shaping
   - `ai_service.py`: OpenAI-based insight generation

3. `app/repositories/`
   Handles database reads used by the API.

4. `pipelines/` and `jobs/`
   Run ETL workflows that fetch Oura data, save raw records, transform them, and persist processed data.

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── jobs/
│   └── daily_db_update.py
├── pipelines/
│   ├── etl_facade.py
│   └── health_etl.py
├── scripts/
│   └── init_db.py
├── logs/
├── compose.yaml
├── Dockerfile
└── requirements.txt
```

## Data Flow

### 1. Authentication

When the app starts, it checks for `ACCESS_TOKEN` and `REFRESH_TOKEN`. If they are missing, it triggers the OAuth browser flow through `app/services/oura_service.py`.

The callback endpoint is:

- `GET /callback`

That endpoint exchanges the authorization code for access and refresh tokens and writes them to `.env`.

### 2. Extraction

The ETL pipeline fetches data from the Oura API in monthly windows, starting from the latest stored date in each table. If no history exists yet, it starts from `2024-12-01`.

### 3. Raw Storage

Each dataset is first written to a raw table, including flattened contributor fields from the Oura API response.

### 4. Transformation

Raw rows are transformed into processed tables with project-specific derived metrics, for example:

- `DailySleep`
  - `performance_score`
  - `recovery_score`
  - `consistency_score`
  - `custom_score`
- `DailyReadiness`
  - `vitality_score`
  - `alertness_index`
  - `resilience_score`
  - `balance_quotient`
  - `recovery_potential`
- `DailyStress`
  - `stress_index`
  - `resilience_rating`

### 5. API Access

The FastAPI layer reads processed records from the database and returns:

- raw queried records for date ranges
- 7-day summaries
- transformed sleep route responses
- AI-generated insight reports

## Database Models

The database schema is defined in [app/models/models.py](/Users/eliorocha/dev/projects/oura-health-analytics/app/models/models.py).

Main raw tables:

- `raw_daily_sleep`
- `raw_daily_readiness`
- `raw_daily_stress`
- `raw_daily_activity`
- `raw_sleep_routes`

Main processed tables:

- `daily_sleep`
- `daily_readiness`
- `daily_stress`
- `daily_activity`
- `sleep_routes`

There is also a `user` model defined, although the current API and ETL flow do not appear to populate it.

## API Endpoints

### Basic

- `GET /`
- `GET /callback`
- `GET /user`

### Sleep

- `GET /sleep?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /sleep/latest`
- `GET /sleep/summary`

### Sleep Routes

- `GET /sleep/route?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /sleep/route/latest`
- `GET /sleep/route/latest/summary`
- `GET /sleep/route/insight`

### Readiness

- `GET /readiness/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /readiness/latest`
- `GET /readiness/summary`

### Stress

- `GET /stress/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /stress/latest`
- `GET /stress/summary`

### Activity

- `GET /activity/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /activity/latest`
- `GET /activity/summary`

### Combined Insights

- `GET /insights/summary`
- `GET /insights/ai`

## Environment Variables

The codebase expects these environment variables:

- `CLIENT_ID`
- `CLIENT_SECRET`
- `ACCESS_TOKEN`
- `REFRESH_TOKEN`
- `DATABASE_URI`
- `DOCKER_DATABASE_URI`
- `OPENAI_API_KEY`

Notes:

- `ACCESS_TOKEN` and `REFRESH_TOKEN` are written into `.env` by the OAuth callback flow.
- `DOCKER_DATABASE_URI` is used automatically when the code detects it is running inside Docker.
- `OPENAI_API_KEY` is required for the AI insight endpoints.

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Add at least:

```env
CLIENT_ID=your_oura_client_id
CLIENT_SECRET=your_oura_client_secret
DATABASE_URI=postgresql+psycopg2://user:password@localhost:5432/oura
DOCKER_DATABASE_URI=postgresql+psycopg2://user:password@host.docker.internal:5432/oura
OPENAI_API_KEY=your_openai_api_key
```

You can omit `ACCESS_TOKEN` and `REFRESH_TOKEN` initially and let the OAuth flow create them.

### 4. Initialize the database schema

```bash
python scripts/init_db.py
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`.

## Docker

The repository includes:

- [Dockerfile](/Users/eliorocha/dev/projects/oura-health-analytics/Dockerfile)
- [compose.yaml](/Users/eliorocha/dev/projects/oura-health-analytics/compose.yaml)

Start the container with:

```bash
docker compose up --build
```

Current Docker setup notes:

- The container exposes port `8000`.
- The project directory is mounted into `/app`.
- The compose file currently defines only the API container, not a PostgreSQL service.

## Running the ETL

Initialize tables first:

```bash
python scripts/init_db.py
```

Run all ETL pipelines:

```bash
python pipelines/etl_facade.py
```

Run the scheduled-style job entrypoint:

```bash
python jobs/daily_db_update.py
```

The ETL currently processes these Oura endpoints:

- `daily_sleep`
- `daily_readiness`
- `daily_stress`
- `sleep`
- `daily_activity`

Logs are written under `logs/`, including `etl.log`.

## AI Insight Features

The project has two OpenAI-backed insight paths:

- `GET /sleep/route/insight`
  Analyzes a detailed sleep-period payload and returns structured sleep insights.

- `GET /insights/ai`
  Analyzes the last 7 days of sleep, readiness, stress, and sleep-route data and returns a structured health report.

These flows are implemented in [app/services/ai_service.py](/Users/eliorocha/dev/projects/oura-health-analytics/app/services/ai_service.py).

## Important Implementation Notes

- The API primarily reads from the processed database tables, not directly from Oura.
- Sleep routes are filtered in the repository layer to exclude shorter sessions by requiring `total_sleep_duration >= 9000`.
- The app triggers OAuth automatically at import/startup time when tokens are missing.
- The ETL uses `session.merge(...)` so repeated runs act like upserts for existing primary keys.

## Current Gaps / Caveats

Based on the current repository state:

- There is no existing automated test suite in `tests/`.
- The Docker setup does not include a database container.
- Some code comments indicate known rough edges, especially in the Oura fetch layer.
- A `.env.example` file is not present, so setup is inferred from code.

## Useful Entry Points

- API app: [app/main.py](/Users/eliorocha/dev/projects/oura-health-analytics/app/main.py)
- ETL facade: [pipelines/etl_facade.py](/Users/eliorocha/dev/projects/oura-health-analytics/pipelines/etl_facade.py)
- ETL job: [jobs/daily_db_update.py](/Users/eliorocha/dev/projects/oura-health-analytics/jobs/daily_db_update.py)
- DB init script: [scripts/init_db.py](/Users/eliorocha/dev/projects/oura-health-analytics/scripts/init_db.py)

