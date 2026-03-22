# Air Quality Data Pipeline

A real-time data pipeline that extracts air quality metrics from the Open-Meteo API for Kenyan cities, streams the data through Apache Kafka, stores it in MongoDB and PostgreSQL, and enables downstream analytics.

---

## Architecture

```
Open-Meteo API
      │
      ▼
  extract.py          ← Fetches hourly air quality data (Nairobi, Mombasa)
      │
      ▼
   load.py            ← Loads raw data into MongoDB Atlas (every 1 hour)
      │
      ▼
  MongoDB Atlas       ← Raw staging store (daily collections)
      │
      ▼
mongo_extract.py      ← Reads today's collection from MongoDB
      │
      ▼
kafka_producer.py     ← Publishes records to Kafka topic: air_topic
      │
      ▼
   Apache Kafka       ← Message broker (Dockerised)
      │
      ▼
kafka_consumer.py     ← Consumes messages and inserts into PostgreSQL
      │
      ▼
   PostgreSQL         ← Final analytical store (measurements table)
```

---

## Project Structure

```
air_quality/
├── docker-compose.yml      # Zookeeper, Kafka, Kafka UI
├── extract.py              # Fetches data from Open-Meteo API
├── load.py                 # Loads extracted data into MongoDB
├── mongo_extract.py        # Reads data from MongoDB
├── kafka_producer.py       # Publishes data to Kafka topic
├── kafka_consumer.py       # Consumes from Kafka and loads into PostgreSQL
├── .env                    # Environment variables (credentials) — never committed
├── .gitignore              # Excludes .env, __pycache__, .pyc files from Git
└── README.md
```

---

## Data Source

**Open-Meteo Air Quality API** — free, no API key required.

**Cities monitored:**

| City | Latitude | Longitude |
|------|----------|-----------|
| Nairobi | -1.286389 | 36.817223 |
| Mombasa | -4.0435 | 39.6682 |

**Metrics collected per city (hourly):**

| Metric | Description |
|--------|-------------|
| `pm2_5` | Fine particulate matter (µg/m³) |
| `pm10` | Coarse particulate matter (µg/m³) |
| `ozone` | Ozone concentration (µg/m³) |
| `carbon_monoxide` | CO levels (µg/m³) |
| `nitrogen_dioxide` | NO₂ levels (µg/m³) |
| `sulphur_dioxide` | SO₂ levels (µg/m³) |
| `uv_index` | UV Index |

---

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (local or remote)
- MongoDB Atlas account

---

## Python Dependencies

Install all required packages:

```bash
pip install pandas requests pymongo psycopg2-binary kafka-python python-dotenv
```

---

## Environment Variables

This project uses a `.env` file to manage all credentials securely. The `.env` file is listed in `.gitignore` and is **never committed to GitHub**.

### Step 1 — Create a `.env` file in the project root

```env
# MongoDB
MONGO_USER=your_mongodb_username
MONGO_PASSWORD=your_mongodb_password
MONGO_CLUSTER=cluster0.xxxxx.mongodb.net
MONGO_DB=air_quality_db

# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_DB=air_quality
PG_USER=postgres
PG_PASSWORD=your_pg_password
```

### Step 2 — How credentials are loaded in each file

All three files that need credentials use `python-dotenv` to load the `.env` file automatically at startup:

```python
from dotenv import load_dotenv
import os
load_dotenv()
```

Then credentials are accessed like this:

```python
# MongoDB (load.py and mongo_extract.py)
password = os.getenv("MONGO_PASSWORD")
user     = os.getenv("MONGO_USER")
cluster  = os.getenv("MONGO_CLUSTER")
db_name  = os.getenv("MONGO_DB")

# PostgreSQL (kafka_consumer.py)
host     = os.getenv("PG_HOST")
port     = int(os.getenv("PG_PORT"))
dbname   = os.getenv("PG_DB")
user     = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
```

### `.gitignore` — what is excluded from GitHub

```
__pycache__/
*.pyc
.env
*.egg-info/
.venv/
venv/
```

##  Docker Setup (Kafka)

Start Zookeeper, Kafka, and Kafka UI:

```bash
docker-compose up -d
```

Services started:

| Service | Port | Description |
|---------|------|-------------|
| Zookeeper | 2181 | Kafka coordination |
| Kafka | 9092 | Message broker |
| Kafka UI | 8090 | Web UI to monitor topics |

Access Kafka UI at: **http://localhost:8090**

Stop all services:

```bash
docker-compose down
```

---

##  PostgreSQL Setup

Create the database and table before running the consumer:

```sql
CREATE DATABASE air_quality;

\c air_quality

CREATE TABLE measurements (
    id                SERIAL PRIMARY KEY,
    city              VARCHAR(50),
    time              TIMESTAMP,
    pm2_5             FLOAT,
    pm10              FLOAT,
    ozone             FLOAT,
    carbon_monoxide   FLOAT,
    nitrogen_dioxide  FLOAT,
    sulphur_dioxide   FLOAT,
    uv_index          FLOAT,
    inserted_at       TIMESTAMP DEFAULT NOW()
);
```

---

##  Running the Pipeline

Run each step in a separate terminal window in this order:

### Step 1 — Start Kafka infrastructure
```bash
docker-compose up -d
```

### Step 2 — Extract and load into MongoDB (runs every hour)
```bash
python load.py
```

### Step 3 — Start the Kafka consumer (keep running)
```bash
python kafka_consumer.py
```

### Step 4 — Extract from MongoDB and produce to Kafka
```bash
python kafka_producer.py
```

---

##  File Descriptions

### `extract.py`
Calls the Open-Meteo Air Quality API for Nairobi and Mombasa and returns a combined Pandas DataFrame with hourly readings for all 7 air quality metrics.

### `load.py`
Calls `extracting()` from `extract.py` and inserts the resulting DataFrame into a MongoDB Atlas collection named after today's date (e.g., `measurements2025-03-22`). Repeats every 1 hour indefinitely. Credentials are loaded from `.env`.

### `mongo_extract.py`
Connects to MongoDB Atlas, reads today's measurements collection, and returns a DataFrame. Credentials are loaded from `.env`.

### `kafka_producer.py`
Reads today's data from MongoDB via `mongo_extract.py` and publishes each row as a JSON message to the Kafka topic `air_topic`.

### `kafka_consumer.py`
Subscribes to the `air_topic` Kafka topic and inserts each message into the PostgreSQL `measurements` table in real time. PostgreSQL credentials are loaded from `.env`.

### `docker-compose.yml`
Defines three services: Zookeeper (coordination), Kafka (broker), and Kafka UI (monitoring dashboard at port 8090).

### `.env`
Stores all sensitive credentials for MongoDB and PostgreSQL. This file is excluded from Git via `.gitignore` and must be created manually on each machine where the project is run.

---

## Monitoring

**Kafka UI** — view topics, messages, and consumer groups:
```
http://localhost:8090
```

**Check PostgreSQL data:**
```sql
SELECT city, time, pm2_5, pm10, uv_index
FROM measurements
ORDER BY inserted_at DESC
LIMIT 20;
```

**Check MongoDB collections** via MongoDB Atlas web console or:
```python
python mongo_extract.py
```

---

##  Troubleshooting

| Problem | Fix |
|---------|-----|
| Kafka connection refused | Make sure `docker-compose up -d` is running |
| MongoDB authentication error | Check your password encoding — special characters need `quote_plus()` |
| PostgreSQL connection error | Verify credentials in your `.env` file |
| Empty DataFrame from MongoDB | Check that `load.py` has run today and inserted data |
| `kafka_producer.py` sends 0 records | Run `load.py` first to populate today's MongoDB collection |
| `.env` variables returning `None` | Make sure `.env` is in the same folder as the Python files |


