# Use an official Python runtime as a parent image
FROM python:3.12-slim as base

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies first if necessary
RUN apt-get update && apt install -y libpq-dev gcc

RUN pip3 install poetry==2.0.1

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.in-project true

RUN poetry install --no-root

COPY . /app/
