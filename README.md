

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
- Automated ETL orchestration using Apache Airflow
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
│   └── airflow-success.png
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
├──  private.py
│
├──pages/
├── 1_Pipeline_Health.py
├── 2_Stock_Deep_Dive.py
└── 3_Stock_Stack_Comparison.py

.streamlit/
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
Generate summary outputs.

### 6. Orchestrate
Schedule and monitor execution through Apache Airflow.

---

## Setup Instructions

### Clone Repository

```bash
git clone https://github.com/Rhythm001/Stock-Market-ETL-Pipeline.git
cd Stock-Market-ETL-Pipeline
```

---

### Configure Environment

Create a `.env` file:

```env
DB_URL=postgresql://username:password@host:5432/database
```

---

### Run the Pipeline

```bash
docker compose up --build
```

---

### Run Dashboard

```powershell
$env:DB_URL="postgresql://postgres:***@localhost:5433/stock_market"
streamlit run app.py

---

### Access Airflow UI

```text
http://localhost:8080
```

Trigger DAG:

```text
stock_market_etl
```

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

**Database Validation**

```sql
SELECT COUNT(*) FROM stock_prices_enriched;
-- 599
```

---

## Key Learnings

This project strengthened understanding of:

- ETL pipeline architecture
- Workflow orchestration with Airflow
- PostgreSQL integration
- SQL transformations
- Data quality engineering
- Dockerized data pipelines
- Debugging distributed workflow failures

---

## Future Improvements

- CI/CD pipeline automation
- dbt integration
- Kafka-based streaming ingestion
- Cloud deployment (AWS/GCP)
- Hosted dashboard deployment

---

## Built By

Rhythm
