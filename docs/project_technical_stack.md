## **Workflow Orchestration Tools**

### **1. Airflow**

With Apache Airflow to orchestrate workflows involving **arXiv** APIs with strict rate limits (e.g., 1 request every 3 seconds). **Airflow** provides built-in retry mechanisms, scheduling, and task modularity, helping us avoid API blocking and maintain a reliable ingestion process.

**Stack Integration & Interoperability**

- **Airflow** can orchestrate scheduled API calls and trigger DAGs via **CloudWatch**, establishing an observable DataOps pipeline.

**Requirement Mapping**

- **4.1 Data Collection Layer** (flexible, configurable ingestion with retry)
- **4.2 Distributed Data Processing** (modular DAG structure, traceable steps)

### 2. **Kafka**

For APIs with higher throughput limits (e.g., **Crossref**: 50 queries/sec), I adopt **Apache Kafka** to stream and decouple heavy metadata extraction tasks like parsing authors and references from **Crossref** data. Since these are more compute-intensive than IO-bound, **Kafka** serves as a scalable backbone for ingestion and transformation.

**Stack Integration & Interoperability**

- **Kafka** serves as a high-throughput data ingestion and transformation platform, suitable for receiving large-scale event streams pushed from Lambda.

**Requirement Mapping**

- **4.1 Data Collection Layer** (high-throughput ingestion)
- **4.2 Distributed Data Processing** (parallel, scalable pipeline design)

---

## **Storage System**

### 3. **Apache Iceberg + MinIO (S3-compatible)**

To handle large volumes of unstructured raw data, I adopt **Apache Iceberg** as our **NoSQL**, data lakehouse storage format on top of **MinIO** (S3-compatible). It supports schema evolution, time travel, and **Spark SQL** queries — ideal for scalable and future-proof data analytics pipelines.

**Stack Integration & Interoperability**

- Although the current development environment uses **MinIO**, it is fully compatible with **AWS S3**, allowing seamless migration in the future.

**Requirement Mapping**

- **4.1 Data Collection Layer** (central data sink)
- **4.2 Distributed Data Processing** (optimized for batch/parallel read/write)
- **4.4 Data Quality, Modeling & Storage** (data lake design and storage management)

---

## **ETL Processing**

### 4. **Apache Spark** (Planned)

Although not yet fully implemented, **Apache Spark** has been installed in the environment to support distributed querying from Iceberg tables, and for building batch ETL jobs to downstream systems (e.g., **AWS Lambda**, **OpenSearch**).

**Stack Integration & Interoperability**

- **Spark** compensates for **Pandas**’ limitations in handling large-scale data.
- **Spark SQL** supports Iceberg natively and can integrate with **AWS Glue Catalog** and **Athena**, ensuring compatibility with existing storage services.

**Requirement Mapping**

- **4.2 Distributed Data Processing** (fault-tolerant, scalable transformations)
- **4.4 Data Quality, Modeling & Storage** (supports analytics and transformation over data lakes)

---

## **Data Validation & Quality**

### 5. **Pydantic**

I use **Pydantic** models to validate structured incoming data. It is especially effective when dealing with malformed or dirty records from external APIs. The `model_validation()` method helps eliminate invalid data early in the pipeline.

**Stack Integration & Interoperability**

- Fully compatible with the existing **Python** stack.

**Requirement Mapping**

- **4.1 Data Collection Layer** (ensures data integrity at ingestion)
- **4.4 Data Quality, Modeling & Storage** (early validation of raw input)

### 6. **Great Expectations (GX)**

For more complex validations involving DataFrames derived from processed data, regex rules (e.g., DOI format), or cross-field logic (e.g., journal page ranges), **Great Expectations** is more powerful than **Pydantic**. It also generates human-readable, visual reports.

**Stack Integration & Interoperability**

- **GX** offer complementary layers of data validation, enhancing the robustness and traceability of data processing logic.

**Requirement Mapping**

- **4.3 Observability & Monitoring for Data Systems** (data validation feedback loop)
- **4.4 Data Quality, Modeling & Storage** (assertions on data consistency and logic)

---

## **Pipeline Health Monitoring**

### 7. **Prometheus + Grafana**

**Prometheus** is integrated to collect and track real-time system metrics via custom exporters or built-in service metrics. It helps monitor **ETL** success rates, API request latency, and failures across different pipeline stages. These metrics form the foundation for understanding system behaviors and detecting anomalies.

**Grafana**, though not yet fully implemented, is installed to visualize **Prometheus**-collected metrics and set up alert rules (e.g., via **Slack** or email). Together, they form a scalable and extensible observability stack to support real-time monitoring, alerting, and health diagnostics of data pipelines.

**Stack Integration & Interoperability**

- **Prometheus** collects custom metrics (e.g., **ETL** success rate, API latency) and integrates with **CloudWatch** logs.

**Requirement Mapping**

- **4.3 Observability & Monitoring for Data Systems** (real-time metrics and visualization, anomaly alerting and tracking)

---

## **Containerization**

### 8. **Docker / Docker Compose**

**Docker Compose** is used to containerize all services for reproducible demo deployment. While not yet critical for production, this setup allows modular tool development and will serve as a future base for scaling via **Kubernetes**. Currently supports development and testing; future-proofing for scalable deployment.

**Stack Integration & Interoperability**

- Docker-based services can be easily containerized and deployed to **AWS ECS** or **EKS**, aligning with cloud-native infrastructure.
