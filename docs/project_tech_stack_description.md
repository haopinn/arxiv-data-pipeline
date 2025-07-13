# Project Technical Stack

This document outlines the technical stack chosen for the data pipeline project. It details the rationale behind selecting each tool and highlights their capabilities for scalability, parallelization, and handling large data volumes, demonstrating their potential for deployment across various cloud platforms.

---

Based on their primary objectives within the data pipeline, the tools are categorized into the following sections:

1.  **Workflow Orchestration Tools**: Tools responsible for defining, scheduling, and monitoring complex data workflows.
2.  **Storage System**: Tools used for storing and managing large volumes of data.
3.  **ETL Processing**: Tools designed for extracting, transforming, and loading data.
4.  **Data Validation & Quality**: Tools focused on ensuring the accuracy and consistency of data.
5.  **Pipeline Health Monitoring**: Tools for observing the performance and health of the data pipeline.
6.  **Containerization**: Tools for packaging and deploying applications consistently.

---

## **Workflow Orchestration Tools**

### **1. Airflow**

*   Orchestrates workflows for APIs with strict rate limits (e.g., *arXiv* APIs).
*   Provides **built-in retry mechanisms, scheduling**, and task modularity to avoid API blocking and maintain reliable ingestion.
*   Orchestrates scheduled API calls and triggers DAGs, establishing an observable DataOps pipeline.

### 2. **Kafka**

*   Used for APIs with higher throughput limits (e.g., *CrossRef*: 50 queries/sec) to **stream and decouple heavy metadata extraction tasks.**
*   Serves as a scalable backbone for ingestion and transformation, supporting **high-throughput ingestion and a parallel, scalable pipeline design for distributed data processing.**



## **Storage System**

### 3. **Apache Iceberg + MinIO (S3-compatible)**

*  Apache Iceberg is adopted as the **NoSQL**, data lakehouse storage format on top of MinIO for **handling large volumes of unstructured raw data.**
*   Supports schema evolution, time travel, and **Spark SQL** queries.
*   Acts as a central data sink, optimized for batch/parallel read/write, supporting data lake design and storage management.



## **ETL Processing**

### 4. **Apache Spark**

*   Installed to support distributed querying from Iceberg tables and for building batch ETL jobs to downstream systems.
*   Provides fault-tolerant, scalable transformations.
*   Supports analytics and transformation over data lakes.



## **Data Validation & Quality**

### 5. **Pydantic**

*   Used to **validate structured incoming data**, especially effective with **malformed or dirty records** from external APIs.
*   The `model_validation()` method helps eliminate invalid data early in the pipeline, ensuring data integrity at ingestion, and is fully compatible with **Python** stack.

### 6. **Great Expectations (GX)**

*   More powerful than Pydantic for **complex validations** involving **DataFrames**, regex rules, or **cross-field logic**.
*   Generates **human-readable, visual reports**, providing a data validation feedback loop for observability and monitoring.
*   Enables assertions on data consistency and logic and offers complementary layers of data validation, enhancing robustness and traceability.



## **Pipeline Health Monitoring**

### 7. **Prometheus + Grafana**

*   Prometheus is integrated to **collect and track real-time system metrics** via custom exporters or built-in service metrics.
*   Helps monitor **customized metrics** as well like ETL success rates, API request latency, and failures across different pipeline stages.
*   Grafana is installed to **visualize Prometheus-collected metrics and set up alert rules.**
*   Together, they form a scalable and extensible observability stack for real-time monitoring, alerting, health diagnostics, and integrates perfectly with other logging/monitoring systems.



## **Containerization**

### 8. **Docker / Docker Compose**

*   `Docker Compose` is used to containerize all services for reproducible demo deployment.
*   Allows modular tool development and serves as a **future base for scaling.**
*   Docker-based services can be **easily containerized and deployed to cloud-native infrastructure.**
