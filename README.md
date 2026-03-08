
# Scouting-Project

## Overview

Scouting-Project is a full-stack data analytics platform designed to aggregate, process, and visualize professional soccer player statistics. The application interfaces with the Sofascore API to construct a localized, high-performance relational database of player metrics, enabling advanced performance analysis and scouting capabilities.

The system is composed of an asynchronous Python backend handling the ETL (Extract, Transform, Load) processes and a modern React frontend for data visualization.

## System Architecture & Data Pipeline

The core value of this application lies in its automated data pipeline, which is designed to be highly resilient and schema-agnostic where possible. The pipeline operates in the following phases:

### 1. Extraction (Async Data Retrieval)

Data extraction is handled via the `sofascore-wrapper` library. The `api.py` module utilizes Python's `asyncio` to concurrently search for player entities, resolve their unique identifiers, and retrieve comprehensive seasonal statistical profiles.

### 2. Transformation & Validation

Raw payload data is rigorously typed and validated using Pydantic (`models.py`). This layer ensures data integrity for deeply nested JSON structures, representing categories such as passing, defending, dribbling, and goalkeeping.

During the transformation phase, the system performs dynamic statistical derivation:

* **Per-90 Calculations:** The pipeline automatically calculates "per 90 minutes" equivalents for all valid cumulative numeric statistics. It applies rule-based filtering to exclude non-cumulative data types (e.g., percentages, raw ratings, appearance counts) from this calculation.
* **Cross-League Aggregation:** For players participating in multiple competitions within a single season, the system aggregates metrics to generate a unified "All Leagues" statistical profile.

### 3. Loading (Dynamic Persistence)

The database layer (`database.py`) is built on PostgreSQL using `psycopg2`. It features dynamic schema management:

* **Schema Inference:** The database table schema is not statically defined. Instead, the application inspects the Pydantic `Statistics` model schema at runtime to generate the `CREATE TABLE` statements, automatically mapping Python types to SQL data types and appending the derived `_per_90` columns.
* **Idempotent Writes:** All database insertions utilize `ON CONFLICT DO UPDATE` (upsert) constraints based on a composite unique key (`name`, `league_name`, `season_year`, `player_position`). This guarantees idempotency, allowing the pipeline to be run repeatedly to update stats without causing data duplication.

## Technical Stack

**Backend**

* **Language:** Python 3.12+
* **Framework:** FastAPI / Uvicorn
* **Data Validation:** Pydantic
* **Database:** PostgreSQL (with `psycopg2-binary`)
* **Concurrency:** `asyncio`

**Frontend**

* **Framework:** React 19
* **Build Tool:** Vite
* **Animations:** Framer Motion
* **Linting:** ESLint

## Repository Structure

* `main.py`: Application entry point and server configuration.
* `api.py`: External API integration and async data fetching logic.
* `models.py`: Comprehensive Pydantic schema definitions for data serialization and validation.
* `database.py`: PostgreSQL connection management, dynamic table initialization, and idempotent ETL operations.
* `frontend/`: Single-page application directory containing the React/Vite source code.

## Local Development Setup

### Database Requirements

Ensure a local PostgreSQL instance is running on port 5432. The backend will automatically attempt to connect to the default `postgres` database to initialize a dedicated `mountakhab` database.

### Backend Initialization

1. Ensure Python 3.12 or higher is installed.
2. Install the required dependencies:
```bash
pip install fastapi psycopg2-binary pydantic sofascore-wrapper uvicorn

```


3. Start the application server:
```bash
python main.py

```



### Frontend Initialization

1. Navigate to the frontend workspace:
```bash
cd frontend

```


2. Install Node.js dependencies:
```bash
npm install

```


3. Start the Vite development server:
```bash
npm run dev

```
