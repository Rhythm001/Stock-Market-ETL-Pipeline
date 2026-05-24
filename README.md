# Stock Market ETL Pipeline

An automated ETL pipeline built using Python, Apache Airflow, and PostgreSQL for extracting, transforming, storing, and reporting stock market data in a modular Linux-based workflow environment.

## Features

- Automated ETL orchestration using Apache Airflow DAGs
- Modular pipeline architecture for extraction, transformation, and reporting
- PostgreSQL database integration
- Automated scheduling and workflow execution
- Logging and error handling
- Linux/WSL development environment
- Scalable and maintainable project structure

## Tech Stack

- Python
- Apache Airflow
- PostgreSQL
- SQLAlchemy / psycopg2
- Pandas
- Linux (WSL)
- VS Code
- Git

## Project Structure

```bash
project/
│
├── dags/
│   └── stock_etl_dag.py
│
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── report.py
│
├── sql/
│   └── schema.sql
│
├── logs/
│
├── requirements.txt
│
└── README.md


## Workflow

1. Extract stock market data from source APIs/files
2. Transform and clean raw data
3. Load processed data into PostgreSQL
4. Generate reports and summaries
5. Schedule and monitor workflows using Airflow

---

## Setup Instructions

### Clone Repository

```bash
git clone https://github.com/Rhythm001/Stock-Market-ETL-Pipeline.git
cd Stock-Market-ETL-Pipeline
```

### Create Virtual Environment

```bash
python -m venv myenv
source myenv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Airflow

```bash
airflow standalone
```

### Access Airflow UI

```text
http://localhost:8080
```

---

## Future Improvements

- Docker containerization
- Cloud deployment
- Real-time streaming support
- Dashboard integration
- Automated alerting system

---

## Learning Outcomes

This project helped strengthen practical understanding of:

- ETL architecture
- Workflow orchestration
- Database integration
- Modular Python development
- Linux-based development workflows
- Airflow DAG scheduling
