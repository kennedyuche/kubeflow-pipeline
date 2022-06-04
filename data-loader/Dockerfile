FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY download_10k_raw.py .
COPY config.cfg.template .