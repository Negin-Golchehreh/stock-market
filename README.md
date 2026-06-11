# End-to-End Big Data Analytics Pipeline: Stock Market Direction Prediction

[cite_start]An enterprise-grade, distributed Big Data analytics pipeline designed to ingest, process, and analyze millions of rows of historical financial data[cite: 123, 124]. [cite_start]The system handles over 1.8 million raw records from major global indices, leveraging a containerized lambda-like cluster architecture to execute distributed data transformations and machine learning modeling[cite: 123, 136].

[cite_start]This project was developed as a core requirement for the **MSc Data Analytics** program at the **Berlin School of Business & Innovation (BSBI)**[cite: 97, 98, 99].

---

## 🏗️ System Architecture & Infrastructure

The entire pipeline is deployed on a high-performance production cloud node, migrating away from restrictive local localhost environments to eliminate compute bottlenecks and resource-induced crashes.

### Hardware Infrastructure
* **Cloud Platform:** Hetzner Cloud (Compute-Optimized Plan: **CPX62**)
* **Compute:** 16 vCPUs (AMD EPYC™ Dedicated Virtualization Architecture)
* **Memory:** 32 GB DDR4 ECC RAM
* **Storage:** 80 GB High-IOPS NVMe SSD
* **Network:** 20 TB High-Speed Transit Bandwidth

### Distributed Container Ecosystem
[cite_start]The topology is orchestrating a multi-container isolated workspace using **Docker & Docker Compose**, provisioning dedicated networks for coordinated inter-node shuffle boundaries and data replication tasks[cite: 136].

---

## 🛠️ Technology Stack & Component Matrix

| Technology | Production Version | Functional Mandate |
| :--- | :--- | :--- |
| **Apache Hadoop** | 3.2.1 | HDFS fault-tolerant distributed storage & YARN resource allocation [cite: 120, 121, 138] |
| **Apache Spark** | 3.3.0 | In-memory distributed data processing engine & batch query execution [cite: 123, 138] |
| **Apache Hive** | 3.1.2 | Analytical data warehousing layer & HiveQL structural querying [cite: 138, 139] |
| **PySpark** | 3.3.0 | Programmatic Python API interfacing with underlying Spark core runtime [cite: 138, 142] |
| **Scikit-Learn / XGBoost**| Latest | Statistical model execution, pipeline serialization, and metric logging [cite: 147, 148] |
| **Docker / Compose** | Enterprise v20+ | Multi-container component orchestration and resource isolation bounds [cite: 125, 136] |
| **Python Runtimes** | 3.9+ | Primary programmatic implementation language across processing steps [cite: 147] |
| **Jupyter Notebooks** | Core Server | Interactive kernel development and rapid pipeline visualization execution [cite: 166] |

---

## 📈 Pipeline Stages & Functional Implementation

### 1. Data Ingestion & Distributed Storage (HDFS)
* **Dataset Scope:** Multi-exchange financial timeseries dataset exceeding 5GB in flat volume[cite: 131, 158, 162].
* **Ingestion Profile:** Bulk file partition chunks uploaded sequentially into the Hadoop Distributed File System (HDFS)[cite: 139].
* **Data Metrics:** * Raw records processed: `1,835,480`
  * Deduplicated and structural cleaned records: `1,619,136`
  * Primary temporal bounds: `1970-01-02` $\rightarrow$ `2022-12-12`

### 2. Analytical Data Warehousing (Hive & PySpark)
* Schemas are enforced strictly at read/write layers using HiveQL definitions[cite: 139].
* Engineered specific tracking metrics including custom delta variables like `daily_return` and binary classification metrics (`direction`)[cite: 142].
* Distribution tracking indicates structured volume splits across dominant financial indexes:
  * **S&P 500 (`sp500`):** 562,962 records
  * **NASDAQ (`nasdaq`):** 384,881 records
  * **NYSE (`nyse`):** 364,698 records
  * **Forbes 2000 (`forbes2000`):** 306,595 records

### 3. Predictive Modeling & Machine Learning
Advanced predictive modeling maps features against multi-variable index movements using **Random Forest Classifier** and **Gradient Boosting Machine (GBM)** models[cite: 148].
* **Features Used:** `['Close', 'Open', 'High', 'Low', 'Volume', 'daily_return', 'price_range', 'month', 'day_of_week']`
* **Train/Test Bounds:** Evaluated using a robust deterministic split (`1,295,308` training samples; `323,828` out-of-sample testing records)[cite: 149].
* **Visual Diagnostics:** Features importance analysis shows structural reliance on calculated delta vectors (`daily_return`) to classify temporal indicators confidently[cite: 151].

---

## 🚀 Deployment & Local Replication

### Prerequisites
Ensure your infrastructure environment has Docker Engine and Docker Compose plugins installed.
```bash
docker --version
docker-compose --version
```

1. Fire up the Cluster
Clone this repository to your Hetzner Instance or local terminal context and deploy the active stack daemon:
```bash
git clone[https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
docker-compose up -d
```
Ensure that the spark-master, spark-worker, namenode, datanode, and hive-server services are perfectly healthy.

3. Running the Analytics Jupyter Workspace
Locate the container binding authentication token via docker logs to log into the UI workspace safely:
docker logs jupyter-spark-notebook

Open your preferred web browser window and route traffic to: http://your-server-ip:8888📊 Performance DashboardsThe programmatic execution exports visual diagnostic plots automatically to trace behavioral patterns:  results_dashboard.png: Documents the comparative model metrics, comprehensive ROC-AUC curves, confusion matrices, and feature importance mappings.  exchange_analysis.png: Traces the structural index directional variances and seasonal average monthly adjustments across the historical dataset.  📝 Academic AcknowledgementModule Code: Big Data Analytics   Documentation Standard: BSBI Template Guidelines (Harvard Referencing Architecture Style).  
