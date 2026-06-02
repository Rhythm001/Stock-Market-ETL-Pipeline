<<<<<<< HEAD


=======
>>>>>>> 5cb2eed (Final changes)
# Stock Market ETL + Analytics Dashboard

An end-to-end data engineering pipeline that extracts stock market data, transforms and stores it in PostgreSQL, orchestrates workflows using **Apache Airflow** and **Docker Compose**, and visualizes analytics through an interactive **Streamlit dashboard**.

This project demonstrates practical data engineering concepts including workflow orchestration, data validation, SQL transformations, modular pipeline design, and containerized deployment.

---

## Architecture

```text
Stock Data Extraction
        ↓
Raw Data Load (PostgreSQL)
        ↓
Technical Indicator Transformations
        ↓
Data Quality Validation
        ↓
Airflow Orchestration
        ↓
Streamlit Analytics Dashboard
```

---

## Dashboard

### Pipeline Health
![Pipeline Health](assets/pipeline-health.png)

### Stock Deep Dive
![Stock Deep Dive](assets/deep-dive.png)

### Stock Comparison
![Stock Comparison](assets/comparison.png)

## Airflow DAG Execution

![Airflow DAG Success](assets/airflow-success.png)

---

## Features

- Automated ETL orchestration using Apache Airflow
- PostgreSQL raw + enriched analytical layers
- Technical indicator computation (SMA, RSI, Bollinger Bands)
- Interactive Streamlit analytics dashboard
- Pipeline operational monitoring
- Comparative stock scoring engine
- Dockerized backend infrastructure
- Modular transformation pipeline
- Data quality validation checks
- Logging and exception handling
- Linux (WSL) development environment

---

## Tech Stack

- Python
- Apache Airflow
- PostgreSQL
- SQLAlchemy
- Pandas
- Docker
- Docker Compose
- Linux (WSL)
- Git
- VS Code

---

## Project Structure

```text
Stock-Market-ETL-Pipeline/
│
├── README.md
├── assets/
│   ├── airflow-success.png
│   ├── pipeline-health.png
│   ├── deep-dive.png
│   └── comparison.png
│
├── dags/
│   └── stock_etl_dag.py
│
├── src/
│   ├── __init__.py
│   ├── extractor.py
│   ├── loader.py
│   ├── logger.py
│   ├── pipeline.py
│   ├── quality_checks.py
│   ├── report_generator.py
│   └── transformer.py
│
├── sql/
│   ├── create_tables.sql
│   ├── transform_indicators.sql
│   └── queries/
│
├── tests/
│
├── docker-compose.yml
├── dockerfile
├── requirements.txt
│
├── app.py
├── pages/
│   ├── 1_Pipeline_Health.py
│   ├── 2_Stock_Deep_Dive.py
│   └── 3_Stock_Stack_Comparison.py
│
└── .streamlit/
    └── config.toml
```

---

## Workflow

### 1. Extract
Fetch historical stock market data from source APIs.

### 2. Load
Store raw stock data in PostgreSQL.

### 3. Transform
Apply SQL transformations to create enriched analytical datasets.

### 4. Validate
Run automated quality checks:

- Null value detection
- Invalid price validation
- Ticker completeness checks

### 5. Report
Generate a timestamped JSON report covering pipeline metadata, row counts, data freshness, per-ticker technical indicator snapshots, and anomaly detection (volume spikes, RSI overbought/oversold signals). Overall pipeline status is rolled up to a single `PASS` or `WARN` flag.

### 6. Orchestrate
Schedule and monitor execution through Apache Airflow (runs weekdays at 06:00 UTC).

---

## Setup Instructions

### Clone Repository

```bash
git clone https://github.com/Rhythm001/Stock-Market-ETL-Pipeline.git
cd Stock-Market-ETL-Pipeline
```

### Configure Environment

Create a `.env` file:

```env
DB_URL=postgresql://username:password@host:5432/database
```

### Run the Pipeline

```bash
docker compose up --build
```

### Run Dashboard

```bash
# Linux / macOS
export DB_URL="postgresql://postgres:password@localhost:5432/stock_market"
streamlit run app.py
```

```powershell
# Windows (PowerShell)
$env:DB_URL="postgresql://postgres:password@localhost:5433/stock_market"
streamlit run app.py
```

### Access Airflow UI

```
http://localhost:8080
```

Trigger DAG: `stock_market_etl`

---

## Validation Results

Successful execution confirms:

- Data extraction completed
- Raw data successfully loaded
- Transformations executed
- Quality checks passed
- Reports generated
- DAG completed successfully

---

## Sample Output

**Pipeline Report (JSON)**

```json
{
  "pipeline_meta": {
    "report_generated_at": "2026-06-02T19:00:00+00:00",
    "last_ingestion_at": "2026-06-02 18:45:00",
    "latest_trade_date": "2026-05-30",
    "earliest_trade_date": "2026-01-02"
  },
  "row_counts": {
    "raw_rows": 650,
    "enriched_rows": 599,
    "tickers_latest_date": 10,
    "ticker_completeness_ok": true
  },
  "quality_summary": {
    "null_close_prices": 0,
    "invalid_prices": 0,
    "all_passed": true
  },
  "freshness": {
    "latest_trade_date": "2026-05-30",
    "lag_days": 3,
    "freshness_ok": true
  },
  "anomalies": [
    "Volume spike: AAPL on 2026-05-30 (z=2.84)",
    "RSI overbought: MSFT (RSI=72.3)"
  ],
  "status": "PASS"
}
```

---

## Key Learnings

- ETL pipeline architecture
- Workflow orchestration with Airflow
- PostgreSQL integration and SQL transformations
- Data quality engineering
- Dockerized data pipelines
- Debugging distributed workflow failures

---

## Future Improvements

- dbt integration for transformation layer
- Kafka-based streaming ingestion
- Production deployment on Render (attempted; Airflow webserver exceeds Free tier 512MB RAM limit — Scheduler-only architecture identified as viable path forward)
- Expanded CI/CD pipeline

---

## Built By

Rhythm
