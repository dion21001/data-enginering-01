FROM apache/airflow:latest

# Jangan pakai USER root
# Install kafka-python langsung dengan user airflow
RUN pip install kafka-python
