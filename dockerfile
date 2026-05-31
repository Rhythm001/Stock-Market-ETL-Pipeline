FROM apache/airflow:2.10.5
USER root
COPY requirements.txt /requirements.txt
USER airflow
ENV PATH="/home/airflow/.local/bin:$PATH"
RUN pip install --no-cache-dir -r /requirements.txt