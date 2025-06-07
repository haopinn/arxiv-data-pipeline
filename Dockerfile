# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==2.0.1

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root
 
# Stage 2: Runtime
FROM python:3.12-slim as runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED='1'
ENV PYTHONPATH='/app/'

