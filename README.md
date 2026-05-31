# Stock Market ETL Pipeline

An end-to-end automated **ETL pipeline** that extracts stock market data, processes and validates it, stores it in PostgreSQL, and orchestrates the workflow using **Apache Airflow** and **Docker Compose**.

This project demonstrates practical data engineering concepts including workflow orchestration, data validation, SQL transformations, modular pipeline design, and containerized deployment.

---

## Architecture

```text
Stock API Extraction
       ↓
Raw Data Load (PostgreSQL)
       ↓
SQL Transformations
       ↓
Data Quality Validation
       ↓
Report Generation
       ↓
Airflow Orchestration & Monitoring
```

---

## Airflow DAG Execution

![Airflow DAG Success](assets/airflow-success.png)

---

## Features

- Automated ETL orchestration using Apache Airflow
- Modular Python-based pipeline design
- PostgreSQL raw and enriched data layers
- SQL-based transformation workflows
- Automated data quality validation checks
- Dockerized execution environment
- Airflow task monitoring and dependency management
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
└── private.py
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

- Interactive dashboard visualization
- Automated alerting for failures
- Cloud deployment (AWS/GCP)
- Real-time streaming ingestion
- CI/CD integration

---

## Author

**Rhythm**

Business Analyst transitioning into Data Engineering through hands-on ETL and workflow orchestration projects.