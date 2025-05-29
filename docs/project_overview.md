## 📘 Project Overview & Technical Documentation

This document provides a comprehensive overview of the system’s design decisions, challenges encountered, and proposed monitoring strategies for the metadata processing pipeline for **arXiv** and **CrossRef**.

---

### 1. ⚙️ Performance and Scalability Considerations

### 2. 🎯 Rationale Behind Architectural and Processing Design

These two aspects are covered in detail in the accompanying technical stack documentation. Tool and framework selection was guided by the need to fulfill functional requirements **while aligning with our internal technology stack** to ensure maintainability and extensibility.

Key decisions such as:

- Using **Airflow** for orchestrating time-sensitive API crawling tasks with retry logic.
- Adopting **Kafka** to distribute compute-heavy tasks such as parsing and enriching **arXiv** metadata.
- Storing data in **Apache Iceberg** (on **MinIO**) to support scalability and future querying via distributed computing engines like Spark.

This architecture is designed to support future analytical workflows, such as machine learning pipelines, exploratory queries by analysts, and visualizations.

---

### 3. 🧩 Challenges and Irregularities When Handling arXiv Metadata

Several challenges emerged while processing **arXiv** metadata:

- **Unstable API connections**: I frequently encountered `Connection closed by peer` errors when querying the **arXiv** API. This was mitigated by implementing a retry mechanism using persistent **HTTP** sessions (see `src/utils/http_client.py`), and by instrumenting **Prometheus** metrics to track failure rates and response times (`src/monitoring/fetcher_monitor.py`).
- **Pagination and completeness**: It was initially difficult to determine whether all data had been retrieved. By studying the **arXiv** API documentation, I discovered that sorting by `publish_date` (an always-increasing field) in combination with `start_idx` provided a reliable iteration strategy.
- **Schema inconsistency**: **arXiv** and especially **CrossRef** responses often contain irregular or inconsistent fields. For instance, the **CrossRef** `published` date may be represented as a list of 1–3 integers, requiring assumptions and normalization during preprocessing. This highlights the **importance of establishing data lineage**, which is not yet implemented but is a priority for future development.
- **Matching and enrichment issues**: Mapping **arXiv** entries to **CrossRef** metadata is error-prone due to differences in titles, abstracts, or post-publication edits. The **CrossRef** `score` field, used to assess match confidence, operates as a black box. In the future, I may need to establish heuristics or thresholds to tune its effectiveness.

---

### 4. ⚠️ Risks and Data Quality Assurance Strategies

- **Date handling issues**: Although I validate published dates with **GX** (e.g., ensuring they are not set in the future), I currently treat all timestamps as dates without full datetime granularity. This will be improved in the future.
- **Type validation**: I use **Pydantic** to validate incoming external data before internal preprocessing. Some fields use default values, and current missing-value handling is relatively permissive. I anticipate refining this based on feedback from data analysts and scientists.

---

### 5. 🔁 Fault Tolerance and Recovery Mechanisms

- **Resilient task orchestration**: Airflow jobs benefit from built-in retry logic. Additionally, the metadata crawling strategy is **persisted in a PostgreSQL table**, ensuring that **arXiv** records can be exhaustively and reliably traversed.
- **Kafka dead-letter queue (DLQ)**: For downstream consumers (e.g., **CrossRef** metadata fetchers), if processing fails, messages are not silently dropped or endlessly retried. Instead, they are redirected to a **DLQ**, where failures can be **tracked and manually inspected**.

---

### 6. 🖥️ Prototype for Monitoring Dashboard

Our monitoring and observability approach includes the following:

- **Prometheus instrumentation**: Metrics are embedded in key areas such as fetchers, processors, and validators. These metrics (e.g., failure counts, response latency) serve as health indicators.
- **Grafana integration**: I plan to configure alerting rules based on **Prometheus** metrics. Alerts can be routed to Slack or email to notify operators of anomalies in real-time.
- **Kafka DLQ monitoring**: A dedicated dashboard to track **DLQ** accumulation and message failure patterns is planned.
- **Future logging and testing**: Due to time constraints, detailed logging and automated testing are not fully implemented yet. These will be gradually added and integrated into centralized systems like **ELK stack** or **Amazon CloudWatch**.
- **Planned data lineage implementation**: I recognize the importance of tracking data transformation paths, especially for debugging and auditing. Tools like **AWS Glue**, **OpenLineage**, or **DataHub** are being considered for future adoption.

---

### 7. 🧠 Assumptions Made

- **arXiv’s** `publish_date` is strictly increasing and reliable for pagination.
- **CrossRef’s** `score` field offers a meaningful approximation of match confidence.
- Field consistency is not guaranteed; validation and enrichment pipelines must remain flexible and resilient to schema drift.
- Analysts and scientists may need tailored post-processing logic, which will evolve based on real-world usage.
