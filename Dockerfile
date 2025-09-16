FROM apache/airflow:2.9.0

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements and install Python packages
COPY services/looker/requirements-airflow.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy services to the container
COPY services/ /opt/airflow/services/
USER root
RUN chown -R airflow:0 /opt/airflow/services/
USER airflow
