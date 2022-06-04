FROM gcr.io/datamechanics/spark:3.1.1-hadoop-3.2.0-java-11-scala-2.12-python-3.8-latest

USER root:root

ENV PYSPARK_MAJOR_PYTHON_VERSION=3
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY run-spark-delta.py .
COPY config.cfg.template .