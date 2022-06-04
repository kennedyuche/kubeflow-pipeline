FROM ubuntu:16.04

WORKDIR /app

RUN apt-get update -y && apt-get install --no-install-recommends -y -q ca-certificates python-dev python-setuptools wget unzip

RUN easy_install pip

RUN pip install pathlib2 kubernetes

COPY run_spark_job.py .

ENV PYTHONPATH /app