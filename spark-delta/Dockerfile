FROM gcr.io/datamechanics/spark:3.1.1-hadoop-3.2.0-java-11-scala-2.12-python-3.8-latest as base

USER root:root

ENV PYSPARK_MAJOR_PYTHON_VERSION=3 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

WORKDIR /app

RUN apt-get update \
  && apt-get -y install netcat gcc libffi-dev \
  && apt-get clean

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --no-root --no-dev

COPY . .
RUN . /venv/bin/activate && poetry build

ENV PATH="/venv/bin:${PATH}" \
   VIRTUAL_ENV="/venv"

FROM base as final
WORKDIR /app

COPY --from=builder /venv /venv
COPY --from=builder /app/dist .

ENV PATH="/venv/bin:$PATH"

COPY src/ src/
RUN . /venv/bin/activate && pip install *.whl

ENTRYPOINT ["bash"]