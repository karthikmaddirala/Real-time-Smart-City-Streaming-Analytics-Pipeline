# Smart City Real-Time Streaming & Analytics Pipeline

> *End-to-end demonstration of a real-time data pipeline simulating, processing, and querying smart city telemetry:* 


---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running the Pipeline](#running-the-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

In modern urban environments, real-time decision-making based on high-velocity data is essential for efficient traffic management, emergency response, and public safety. However, most traditional data systems are batch-oriented and fail to support timely insights. This project addresses that gap by building a scalable, real-time streaming architecture that can ingest, process, enrich, and analyze smart city data from various IoT sources. The goal is to enable immediate insights, improve situational awareness, and provide a foundation for intelligent city-wide automation and analytics.

The **Smart City Real-Time Streaming & Analytics Pipeline** ingests real-time smart city IoT data (vehicle telemetry, GPS, weather, traffic, emergency events) through Apache Kafka, processes and enriches it using Spark Structured Streaming, stores both raw and enriched data in Amazon S3, catalogs the schema using AWS Glue Crawlers and the Data Catalog, enables ad-hoc SQL querying via Amazon Athena, and loads analytics-ready datasets into Amazon Redshift for business intelligence and reporting.



This project demonstrates:

- **Scalable ingestion** with Apache Kafka and Zookeeper
- **Real-time processing** with Spark Structured Streaming (watermarks & windowed joins)
- **Data lake** storage on Amazon S3 (Parquet format)
- **Metadata management** using AWS Glue Crawler & Data Catalog
- **Serverless querying** with Amazon Athena
- **Event-driven ETL** to Amazon Redshift via AWS Glue Jobs

---

## Architecture

<img src="images/Data Flow.png" alt="Architecture Diagram" width="700"/>

Data flows through the pipeline in a continuous loop: first, IoT devices send streams of vehicle telemetry, GPS coordinates, weather updates, traffic snapshots, and emergency alerts, each published to its own Kafka topic. Spark Structured Streaming then subscribes to all five topics, applying predefined schemas, cleaning and splitting location fields into latitude and longitude, and using watermarks and timestamp‐based window joins to enrich vehicle records with the latest weather and emergency data. Both the raw individual streams and the joined “enriched” stream are written in Parquet format to Amazon S3. As soon as new Parquet files land, an S3 event triggers an AWS Glue Job that reads the enriched data—using schema definitions from the AWS Glue Data Catalog—to load it into Redshift. Meanwhile, AWS Glue Crawlers periodically scan the S3 folders, infer and register table schemas in the Data Catalog, and Athena uses that metadata to run ad-hoc SQL queries directly against the Parquet files in S3.



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
   git clone https://github.com/your-username/Real-time-Smart-City-Streaming-Analytics-Pipeline.git
   cd Real-time-Smart-City-Streaming-Analytics-Pipeline
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
Real-time-Smart-City-Streaming-Analytics-Pipeline/
├── README.md
├── .gitignore
├── Project Documentation.pdf 
├── docker-compose.yml
├── jobs/
│   ├── config.py          # AWS credentials (ignored)
│   ├── main.py
│   └── spark-city.py              
├── glue/                  # Glue crawler configs & ETL job script
│   ├── crawler_config.json
│   └── etl_job_script.py
└── images/                # Logos and screenshots
    ├── Data Flow.png
    ├── Athena_results.png
    ├── Crrawler Logs.png
    ├── Glue Job.png
    ├── S3.png
    ├── Spark Logs.png
    ├── kafka log.png
    └── redshift_results.png
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
- **Data quality checks** and anomaly detection integrations

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
