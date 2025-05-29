# Smart City Real-Time Streaming & Analytics Pipeline

> **End-to-end demonstration** of a real-time data pipeline simulating, processing, and querying smart city telemetry: **Kafka → Spark → S3 → Glue Crawler → Data Catalog → Athena → Glue Job → Redshift**.

![Architecture Diagram](diagrams/architecture.png)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running the Pipeline](#running-the-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

The **Smart City Real-Time Streaming & Analytics Pipeline** ingests synthetic smart city data (vehicle telemetry, GPS, weather, traffic, emergency events) in real time, enriches it via Spark Structured Streaming, stores raw and enriched data in Amazon S3, catalogs schemas with AWS Glue, provides ad-hoc SQL querying via Athena, and loads analytic-ready datasets into Amazon Redshift for BI.

This project demonstrates:

- **Scalable ingestion** with Apache Kafka and Zookeeper
- **Real-time processing** with Spark Structured Streaming (watermarks & windowed joins)
- **Data lake** storage on Amazon S3 (Parquet format)
- **Metadata management** using AWS Glue Crawler & Data Catalog
- **Serverless querying** with Amazon Athena
- **Event-driven ETL** to Amazon Redshift via AWS Glue Jobs

---

## Architecture

```mermaid
flowchart TD
  A[Data Simulator] --> B[Kafka Topics<br/>(vehicle, gps, weather, traffic, emergency)]
  B --> C[Spark Structured Streaming<br/>(2×workers, schemas, watermarks, cleaning, joins)]
  C --> D[S3 (raw & enriched)]
  D -->|S3 Event| E[AWS Glue Job<br/>(event-driven load)]
  E --> F[Amazon Redshift]
  D --> G[AWS Glue Crawler<br/>& Data Catalog]
  G --> H[Amazon Athena<br/>(ad-hoc SQL)]
```

---

## Tech Stack

| Component                 | Role                                                              |
|---------------------------|-------------------------------------------------------------------|
| Docker Compose            | Orchestrates Kafka, Zookeeper, Spark                              |
| Apache Kafka & Zookeeper  | Real-time message ingestion & cluster coordination               |
| Apache Spark Structured Streaming | Stream processing, schema enforcement, windowed joins  |
| Amazon S3                 | Data lake for raw & enriched data (Parquet)                       |
| AWS Glue Crawler          | Schema inference & metadata registration in Glue Data Catalog     |
| AWS Glue Data Catalog     | Central metadata store for table definitions & partitions         |
| Amazon Athena             | Serverless SQL querying over S3 data                              |
| AWS Glue Job              | Event-driven ETL reading from Data Catalog → loading into Redshift|
| Amazon Redshift           | Dedicated analytic data warehouse                                 |

---

## Prerequisites

- **Git** (>=2.20)
- **Docker & Docker Compose**
- **Python 3.8+**
- **AWS CLI** configured with permissions for S3, Glue, Athena, Redshift
- **AWS credentials** (Access Key ID & Secret Key)

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/smart-city-pipeline.git
   cd smart-city-pipeline
   ```
2. **Set up your virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure AWS credentials** in `config.py` (ignored by Git):
   ```python
   AWS_ACCESS_KEY = "YOUR_ACCESS_KEY"
   AWS_SECRET_KEY = "YOUR_SECRET_KEY"
   AWS_REGION = "us-east-1"  # or your preferred region
   ```

---

## Project Structure

```
smart-city-pipeline/
├── README.md
├── .gitignore
├── docker-compose.yml
├── config.py              # AWS credentials (ignored)
├── requirements.txt       # Python dependencies
├── data-simulator/        # Kafka producers for each topic
│   └── simulator.py
├── spark/                 # Spark Structured Streaming job
│   └── main.py
├── glue/                  # Glue crawler configs & ETL job script
│   ├── crawler_config.json
│   └── etl_job_script.py
├── diagrams/              # Flowchart source + export
│   ├── architecture.mmd
│   └── architecture.png
└── assets/                # Logos and screenshots
    ├── kafka.png
    ├── spark.png
    ├── s3.png
    ├── glue.png
    ├── athena.png
    └── redshift.png
```

---

## Running the Pipeline

1. **Start local services**:
   ```bash
   docker-compose up -d
   ```
2. **Run the data simulator** (in its own terminal):
   ```bash
   python data-simulator/simulator.py
   ```
3. **Submit the Spark job**:
   ```bash
   spark-submit spark/main.py
   ```
4. **Trigger Glue Crawler** (manually or scheduled via AWS Console/CLI):
   ```bash
   aws glue start-crawler --name your_crawler_name
   ```
5. **Configure S3 event** to invoke the Glue ETL job (or schedule via CloudWatch Events).

---

## Monitoring & Logging

- **Kafka & Spark logs** available in Docker container logs: `docker-compose logs kafka spark`
- **AWS CloudWatch** for Glue Job run history & Athena query logs
- **Glue Data Catalog** console to validate table schemas and partitions

---

## Future Enhancements

- **Real-time dashboard** with QuickSight or Streamlit
- **CloudWatch metrics & Alerts** for pipeline health monitoring
- **Schema Registry** using AWS Glue Schema Registry (Avro/Protobuf)
- **Data quality checks** and anomaly detection integrations

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
