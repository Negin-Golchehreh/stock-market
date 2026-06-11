# 📊 Big Data Assignment — Stock Market Analysis Pipeline

**Master's Assignment | Hadoop + Spark + Hive + MLlib**

---

## 🚀 Step-by-Step Guide

### OPTION A: Quick Test (No Docker, ~5 minutes)

Good for testing the ML code before setting up the full environment.

```bash
# 1. Install Python dependencies
pip install pandas numpy scikit-learn matplotlib seaborn xgboost joblib

# 2. Run the quick test (uses synthetic demo data)
cd ml/
python test_locally.py
```

**You'll see:** model training output + 4 plots saved in `ml/outputs/`

---

### OPTION B: Full Docker Setup (~30-60 minutes)

#### Prerequisites
- Docker Desktop installed → https://www.docker.com/products/docker-desktop/
- At least **8GB RAM** available for Docker
- **15GB+ free disk space**

#### Step 1: Install Docker Desktop

**Windows/Mac:**
1. Download from https://www.docker.com/products/docker-desktop/
2. Install and start it
3. Verify: `docker --version`

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
```

#### Step 2: Start the Stack

```bash
# Navigate to docker folder
cd docker/

# Pull all images and start containers (first time takes 10-20 min)
docker-compose up -d

# Check all containers are running
docker-compose ps
```

You should see these containers all `Up`:
```
namenode        Up    (port 9870)
datanode        Up    (port 9864)
resourcemanager Up    (port 8088)
spark-master    Up    (port 8080)
spark-worker    Up
hive-metastore  Up
hiveserver2     Up    (port 10002)
jupyter         Up    (port 8888)
```

#### Step 3: Run Setup Script

```bash
bash setup.sh
```

#### Step 4: Get Kaggle Data

1. Go to https://www.kaggle.com/account
2. Scroll to "API" section → click **"Create New API Token"**
3. This downloads `kaggle.json`
4. Copy it to your `data/` folder
5. Run:
```bash
bash download_data.sh
```

**Note on dataset size:** The Kaggle stock dataset has multiple exchanges.
To exceed 5GB, download ALL of them:
- NYSE stocks: `nyse/` folder
- NASDAQ stocks: `nasdaq/` folder  
- S&P 500: `sp500/` folder

#### Step 5: Run Spark Processing (Task 3)

```bash
# Copy script to Spark container
docker cp spark/01_spark_processing.py spark-master:/opt/spark-apps/

# Submit to Spark cluster
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --executor-memory 2g \
  /opt/spark-apps/01_spark_processing.py
```

Or open Jupyter: **http://localhost:8888** and upload + run the `.py` file.

#### Step 6: Run Hive Queries (Task 3)

```bash
# Copy SQL file to Hive container
docker cp hive/hive_queries.sql hiveserver2:/tmp/

# Run queries
docker exec -it hiveserver2 beeline \
  -u 'jdbc:hive2://localhost:10000/' \
  -f /tmp/hive_queries.sql
```

#### Step 7: Run ML Pipeline (Task 4)

**Option 1 - In Jupyter (recommended):**
1. Open http://localhost:8888
2. Upload `ml/02_ml_pipeline.py`
3. Open it and run cell by cell

**Option 2 - Command line:**
```bash
docker cp ml/02_ml_pipeline.py jupyter:/home/jovyan/ml/
docker exec jupyter python /home/jovyan/ml/02_ml_pipeline.py
```

---

## 🌐 Web UIs for Screenshots (Task 2 & 3)

| Service | URL | What to screenshot |
|---------|-----|-------------------|
| Jupyter Lab | http://localhost:8888 | Code execution |
| Spark Master | http://localhost:8080 | Running jobs |
| HDFS NameNode | http://localhost:9870 | File browser |
| YARN Manager | http://localhost:8088 | Resource usage |
| Hive Web UI | http://localhost:10002 | Query results |

---

## 📈 Expected Output Files

After running everything, you'll have in `ml/outputs/`:

| File | Description | Used in |
|------|-------------|---------|
| `confusion_matrix.png` | Per-model confusion matrices | Task 4 |
| `roc_curves.png` | ROC curves for all models | Task 4 |
| `feature_importance.png` | Top 15 features ranked | Task 4 |
| `model_comparison.png` | Dashboard comparing all models | Task 4 |
| `best_model.pkl` | Saved model (Random Forest) | Task 4 |
| `model_metadata.json` | Metrics summary | Task 4 |

---

## 🔧 Troubleshooting

**NameNode won't start:**
```bash
docker exec namenode hdfs namenode -format -force
docker-compose restart namenode
```

**Out of memory error:**
- Increase Docker Desktop memory to 8GB
- Settings → Resources → Memory → 8GB

**Port already in use:**
```bash
# Find what's using port 8888
lsof -i :8888  # Mac/Linux
netstat -ano | findstr 8888  # Windows
```

**Kaggle download fails:**
- Make sure `kaggle.json` is in the `data/` folder
- Verify your Kaggle account has accepted the dataset terms

**Stop everything:**
```bash
docker-compose down
```

**Complete reset (delete all data):**
```bash
docker-compose down -v
```

---
