# End-to-End Big Data Analytics Pipeline: Stock Market Direction Prediction

This project implements an end-to-end Big Data analytics pipeline for stock market direction prediction. It is designed to ingest, store, process, analyze, and model large-scale historical financial data using a distributed container-based environment.

The pipeline processes more than 1.8 million raw records from major global stock market indices. It uses Hadoop, Spark, Hive, PySpark, and machine learning models to transform raw historical market data into structured analytical outputs and predictive results.

This project was developed as part of the MSc Data Analytics programme at the Berlin School of Business & Innovation (BSBI).

---

## System Architecture and Infrastructure

The project was moved from a local development environment to a cloud-based server to avoid common local resource limitations such as memory crashes, slow processing, and restricted compute capacity.

### Hardware Infrastructure

| Requirement | Specification |
| ----------- | ------------- |
| Compute     | 8 vCPUs       |
| Memory      | 16 GB RAM     |
| Storage     | 20 GB         |

The system runs as a distributed multi-container environment using Docker and Docker Compose. Each core service is deployed in its own container, allowing Hadoop, Spark, Hive, and Jupyter to work together in an isolated and reproducible setup.

---

## Technology Stack

| Technology              |     Version | Purpose                                                             |
| ----------------------- | ----------: | ------------------------------------------------------------------- |
| Apache Hadoop           |       3.2.1 | Distributed storage using HDFS and resource management through YARN |
| Apache Spark            |       3.3.0 | Distributed in-memory data processing and batch execution           |
| Apache Hive             |       3.1.2 | Data warehousing and structured querying using HiveQL               |
| PySpark                 |       3.3.0 | Python interface for Spark-based data processing                    |
| Scikit-Learn / XGBoost  |      Latest | Machine learning model training, evaluation, and metric reporting   |
| Docker / Docker Compose |        v20+ | Container orchestration and service isolation                       |
| Python                  |        3.9+ | Main programming language for data processing and modeling          |
| Jupyter Notebook        | Core Server | Interactive development, testing, and visualization                 |

---

## Pipeline Stages

### 1. Data Ingestion and Distributed Storage

The raw stock market dataset is uploaded into the Hadoop Distributed File System (HDFS). The dataset contains historical market data from multiple financial indices and has a total size of more than 5GB.

Key dataset statistics:

| Metric                           |                    Value |
| -------------------------------- | -----------------------: |
| Raw records processed            |                1,835,480 |
| Cleaned and deduplicated records |                1,619,136 |
| Date range                       | 1970-01-02 to 2022-12-12 |

The ingestion stage prepares the raw files for distributed processing and ensures that the data can be accessed efficiently by Spark and Hive.

---

### 2. Data Warehousing and Transformation

Hive is used to define structured schemas over the processed financial data. PySpark is then used to clean, transform, and engineer new features from the raw market values.

The main engineered fields include:

* `daily_return`
* `price_range`
* `month`
* `day_of_week`
* `direction`

The `direction` field is used as the binary target variable for predicting whether the market movement is positive or negative.

The cleaned data is distributed across the following index groups:

| Index       | Records |
| ----------- | ------: |
| S&P 500     | 562,962 |
| NASDAQ      | 384,881 |
| NYSE        | 364,698 |
| Forbes 2000 | 306,595 |

---

### 3. Machine Learning and Prediction

The machine learning stage uses supervised classification models to predict stock market movement direction. The models are trained using historical price and volume-based features.

The main models used in this project are:

* Random Forest Classifier
* Gradient Boosting Machine

The selected features are:

```python
['Close', 'Open', 'High', 'Low', 'Volume', 'daily_return', 'price_range', 'month', 'day_of_week']
```

The dataset is split into training and testing sets using a deterministic train-test split:

| Dataset      | Number of Records |
| ------------ | ----------------: |
| Training set |         1,295,308 |
| Testing set  |           323,828 |

Model evaluation is performed using standard classification metrics, including accuracy, confusion matrix analysis, ROC-AUC evaluation, and feature importance analysis.

The feature importance results show that calculated market movement indicators, especially `daily_return`, play a major role in predicting the direction of market movement.

---

## Deployment and Local Replication

### Prerequisites

Before running the project, make sure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### Clone the Repository

```bash
git clone https://github.com/Negin-Golchehreh/stock-market.git
cd stock-market
```

### Start the Cluster

```bash
docker-compose up -d
```

After starting the containers, check that the required services are running correctly, including:

* Spark master
* Spark worker
* Hadoop namenode
* Hadoop datanode
* Hive server
* Jupyter notebook container

### Access the Jupyter Workspace

To get the Jupyter authentication token, run:

```bash
docker logs jupyter-spark-notebook
```

Then open Jupyter in your browser:

```text
http://YOUR-SERVER-IP:8888
```

---

## Output Dashboards and Visual Reports

The pipeline exports visual outputs to help analyze model performance and market behavior.

### `results_dashboard.png`

This dashboard includes:

* Model performance comparison
* ROC-AUC curves
* Confusion matrices
* Feature importance results

### `exchange_analysis.png`

This visualization includes:

* Market direction distribution across exchanges
* Index-level movement comparison
* Monthly and seasonal trend analysis

---

## Academic Context

This project was completed as part of the Big Data Analytics module for the MSc Data Analytics programme at BSBI.

The project follows an academic reporting structure and uses Harvard-style referencing in the accompanying report documentation.
