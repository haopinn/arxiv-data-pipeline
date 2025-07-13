# Overview

## 1. Project Background

In today's fast-paced digital world, the ability to harness and connect knowledge separates winning teams from the rest. This project builds an **intelligent, scalable, real-time academic metadata pipeline** that doesn't just store scholarly data, it actively learns, adapts, and evolves.

Unlike static knowledge bases gathering dust, this system continuously ingests *arXiv* and *CrossRef* metadata, automatically discovering research patterns and **powering downstream magic**: recommendation engines, interactive dashboards, and AI-driven insights for data analysts and scientists. The goal is for transforming how we **discover, understand, and connect** knowledge.

## 2. Personal Motivation

This project doubles as my playground for mastering production-grade data engineering, especially for **data monitoring and pipeline health checking**. I'm diving headfirst into areas I've wanted to explore:

- **Data schema validation** using **Pydantic**
- **Data quality assurance** via **Great Expectations**
- **Monitoring infrastructure** with **Prometheus + Grafana**
- **Distributed data orchestration** via **Kafka and Airflow**

By treating this project as both a practical pipeline and a learning platform, I hope to sharpen my ability to build resilient, observable, and production-grade data systems.

## 3. Dataset Selection: A Microcosm of Knowledge Collaboration

This project builds upon metadata from [*arXiv*](https://arxiv.org/) and [*CrossRef*](https://www.crossref.org/), with reference to publicly available datasets such as the Cornell-University/arxiv Scholarly Articles Dataset. Academic publications offer rich, interconnected metadata including:

- Titles and categories
- Author collaboration networks
- DOI, citation, and reference structures
- Temporal patterns and topic evolution

Such data is ideal for simulating **real-world knowledge dynamics**, supporting experimentation on document recommendation, author profiling, and interdisciplinary research mapping.

## 4. System Architecture

This project features a modular and distributed architecture, designed for scalability and observability:

- **Data Ingestion Layer**
    
    Using **Airflow** and **Kafka**, *arXiv* and *CrossRef* APIs are queried on a schedule, with metadata normalized and validated before storage.
    
- **Storage Layer**
    
    **Apache Iceberg** (backed by **MinIO** as an object store) acts as the core metadata lakehouse, storing *arXiv* and *CrossRef* metadata in structured formats.
    
- **Distributed Transformation and Validation**
    
    All data undergoes validation using **Great Expectations** and schema checks using **Pydantic**, ensuring clean and query-ready data.
    
- **Monitoring Layer**
    
    **Prometheus** and **Grafana** are integrated for metrics tracking and alerting, providing health checks at every stage of the pipeline.
    
- **Data Access Layer**
    
    Includes RESTful APIs, OpenSearch for full-text indexing and vectorization, and dashboarding or downstream analysis.
    

If you’re intereted in detail of selecting tools, check  `docs/project_tech_stack_description.md`  for full rationale.

# Diagram

![flow_chart.png](https://github.com/haopinn/arxiv-data-pipeline/blob/main/flow_chart.png?raw=true)


# Directory Structure
```docker
.
│
├── .env                       # Environment variables for 'dev' environment
├── .env.demo                  # Environment variables for 'demo' environment
├── Dockerfile                 # Kafka consumer Docker image definition
├── Dockerfile.airflow         # Airflow container Docker image definition
│
├── docker-compose.yaml        # Docker Compose services setup
│
├── poetry.lock                # Poetry dependency lock file
├── poetry.toml                # Poetry tool settings
├── pyproject.toml             # Project and dependency definition
│
├── README.md                  # Project documentation (this file)
│
├── docker/                    # Container-specific setup and configs
│   └── airflow/               # Airflow DAGs and runtime logic
│       └── dags/              # DAG definition scripts
│   └── grafana_data/          # Configuration of Grafana dashboards
│   └── prometheus/            # Configuration of Prometheus
│
├── src/                       # Core Python source code
│   ├── client/                # Connectors for PostgreSQL, Kafka, Iceberg, etc.
│   ├── data_fetcher/          # Fetch raw data from arXiv and Crossref APIs
│   ├── data_processor/        # Transform and clean raw fetched data
│   ├── data_validator/        # Validate data using Great Expectations
│   ├── kafka_message/         # Kafka message generators and transformers
│   ├── monitoring/            # Prometheus metric collection and tracking
│   ├── pipeline/              # High-level pipeline orchestration logic
│   ├── schema/                # Pydantic and internal data schemas
│   ├── schema_validator/      # Pydantic model validator implementation and metrics collection for Prometheus Gateway
│   ├── script/                # Initialization/demo scripts (e.g., create Iceberg tables)
│   ├── storage/               # Save dataframes to Iceberg or other storage
│   └── utils/                 # Utility functions and configuration loaders
```


# Project Setup

Use `Docker Compose` to start all services:

```docker
docker compose --env-file .env.demo up -d
```

> ⚠️ Warning – Demo Environment Only ⚠️
> 
> 
> This project is intended for **demonstration purposes only**. It is **not recommended** to build or run the current Docker setup in a production or sensitive environment due to the following concerns:
> 
> 1. **Image size is not optimized**: The container images are large and may consume unnecessary disk space or memory.
> 2. **Potential security risk**: To enable cross-container operations (especially for Airflow), the Docker socket (`/var/run/docker.sock`) is mounted as a volume. This may pose **security risks** by exposing Docker daemon access from inside the container.


# Docker Services Overview

Here is a hierarchical classification of the Docker services defined in `docker-compose.yaml`:

*   **Database**
    *   `postgres`: PostgreSQL database used by Airflow and Iceberg catalog.
*   **Messaging / Streaming**
    *   `redis`: Redis instance used by Airflow's Celery executor.
    *   `zookeeper`: Zookeeper service, a dependency for Kafka.
    *   `kafka`: Apache Kafka broker for message queuing.
    *   `kafka-schema-registry`: Confluent Schema Registry for managing Kafka message schemas.
    *   `kafka-connect`: Confluent Kafka Connect for streaming data between Kafka and other systems.
    *   `ksqldb-server`: KSQLDB server for stream processing.
*   **Data Storage**
    *   `minio`: S3-compatible object storage server (used for Iceberg warehouse).
    *   `iceberg-rest`: Iceberg REST Catalog service.
    *   `minio-client`: Client to initialize MinIO (create buckets).
*   **Data Processing (ETL)**
    *   `spark-iceberg`: Apache Spark environment configured to work with Iceberg.
*   **Airflow (Orchestration)**
    *   `airflow-webserver`: Provides the web-based user interface for Airflow.
    *   `airflow-scheduler`: Monitors and triggers tasks based on DAG definitions.
    *   `airflow-worker`: Executes the actual Airflow tasks (Celery worker).
    *   `airflow-triggerer`: Handles deferred tasks in Airflow.
    *   `airflow-init`: Service to initialize the Airflow database and create the default user.
    *   `flower`: Web-based tool for monitoring Celery workers used by Airflow.
*   **Monitoring**
    *   `kafka-exporter`: Exports Kafka metrics for Prometheus.
    *   `statsd-exporter`: Exports StatsD metrics (used by Airflow) for Prometheus.
    *   `prometheus`: Prometheus server for collecting and storing metrics.
    *   `pushgateway`: Prometheus Pushgateway for handling short-lived job metrics.
    *   `grafana`: Grafana server for visualizing metrics from Prometheus.
    *   `conduktor-console`: Kafka monitoring and management tool (enabled via `monitoring` profile).
*   **Application Consumers**
    *   `kafka-consumer`: instances of the custom application consumer service.