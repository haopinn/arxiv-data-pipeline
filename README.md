# 🏗️Overview

![flow_chart.png]([attachment:c0182734-5019-4e01-9679-103c35a082b2:flow_chart.png](https://github.com/haopinn/arxiv-data-pipeline/blob/main/flow_chart.png?raw=true))


# 📂 Directory Structure
```docker
.
│
├── .env                       # Environment variables
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
│   ├── script/                # Initialization/demo scripts (e.g., create tables)
│   ├── storage/               # Save dataframes to Iceberg or other storage
│   └── utils/                 # Utility functions and configuration loaders
```


# ⚙️ Project Setup

Use **Docker Compose** to start all services:

```docker
docker compose --env-file .env.dev up -d
```

> ⚠️ Warning – Demo Environment Only ⚠️
> 
> 
> This project is intended for **demonstration purposes only**. It is **not recommended** to build or run the current Docker setup in a production or sensitive environment due to the following concerns:
> 
> 1. **Image size is not optimized**: The container images are large and may consume unnecessary disk space or memory.
> 2. **Potential security risk**: To enable cross-container operations (especially for Airflow), the Docker socket (`/var/run/docker.sock`) is mounted as a volume. This may pose **security risks** by exposing Docker daemon access from inside the container.


# 🧱 Docker Services Overview

| Service Name | Image / Component | Purpose / Role |
| --- | --- | --- |
| `airflow-webserver` | `airflow-custom` | Web UI for managing DAGs and Airflow tasks |
| `airflow-scheduler` | `airflow-custom` | Triggers tasks based on schedule |
| `airflow-worker` | `airflow-custom` | Executes Airflow tasks |
| `airflow-triggerer` | `airflow-custom` | Handles trigger-based tasks (e.g., sensors) |
| `postgres` | `postgres:13` | Metadata DB for Airflow |
| `redis` | `redis:7.2-bookworm` | Celery broker for Airflow task queues |
| `kafka` | `confluentinc/cp-kafka:7.8.0` | Message broker for event-driven architecture |
| `zookeeper` | `confluentinc/cp-zookeeper:7.8.0` | Required for Kafka cluster coordination |
| `kafka-schema-registry` | `confluentinc/cp-schema-registry:7.8.0` | Manages Avro/Protobuf/JSON schemas for Kafka messages |
| `kafka-connect` | `confluentinc/cp-kafka-connect:7.8.0` | Kafka Connect service for ingest/export pipelines (e.g., MinIO, Iceberg) |
| `arxiv-data-pipeline-kafka-consumer` | `arxiv-data-pipeline-kafka-consumer` | Custom Python consumer for processing arXiv metadata |
| `minio` | `minio/minio` | S3-compatible object storage for storing intermediate and final data |
| `minio-client` | `minio/mc` | Utility container to initialize/configure MinIO |
| `iceberg-rest` | `apache/iceberg-rest-fixture` | REST Catalog for Apache Iceberg metadata operations |
| `spark-iceberg` | `tabulario/spark-iceberg` | Spark engine for querying and writing to Iceberg tables |
| `prometheus` | `prom/prometheus` | Metrics collection for monitoring pipeline health |
| `statsd-exporter` | `prom/statsd-exporter` | Translates statsd metrics into Prometheus format |
| `grafana` | `grafana/grafana:latest` | Visualization layer for monitoring metrics |
