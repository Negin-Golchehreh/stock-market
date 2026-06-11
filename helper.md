#  Big Data Assignment — Stock Market Analysis Pipeline

**Master's Assignment | Hadoop + Spark + Hive + MLlib**

---

##  Project Structure

```
bigdata-project/
├── docker/
│   ├── docker-compose.yml          ← Full Hadoop/Spark/Hive stack
│   ├── hadoop-config/
│   │   ├── core-site.xml
│   │   └── hdfs-site.xml
│   └── setup.sh                    ← Auto-setup script
│
├── data/                           ← Put Kaggle data here
│   └── stocks                      ← Your Kaggle API key
      └── forbes2000/
      |   └──  csv
      |   └──  json    
      └─── nasdaq/
      |    └──  csv
      |    └──  json  
      └── nyse/ 
      |    └──  csv
      |    └──  json 
      └── sp500/ 
           └──  csv
           └──  json               
│
├── spark/
│   └── 01_spark_processing.py      ← PySpark data pipeline (Task 3)
│
├── hive/
│   └── hive_queries.sql            ← HiveQL queries (Task 3)
│
└── ml/
    ├── 02_ml_pipeline.py           ← ML pipeline: RF + XGBoost (Task 4)
    ├── test_locally.py             ← Quick test (no Docker needed)
    └── outputs/                    ← Generated plots saved here
```

---

##  Step-by-Step Guide

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
Docker Ubuntu install → https://docs.docker.com/engine/install/ubuntu/

#### Install Docker Compose

```bash
sudo apt install -y docker-compose-plugin 
```

#### Step 2: Start Stack 

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
### OR Upload the Kaggle dataset file manually to the server (My way)

**Note on dataset size:** The Kaggle stock dataset has multiple exchanges.
To exceed 5GB, download ALL of them:
- NYSE stocks: `nyse/` folder
- NASDAQ stocks: `nasdaq/` folder  
- S&P500: `sp500/` folder
- forbes2000: `forbes2000/` folder

#### Step 5: Run Spark Processing in two ways (Task 3)

 ### First Ways (Python Command, My way)

```bash
# Create the data directory.
docker exec namenode hdfs dfs -mkdir -p /user/bigdata/stocks/raw/nasdaq
docker exec namenode hdfs dfs -mkdir -p /user/bigdata/stocks/raw/nyse
docker exec namenode hdfs dfs -mkdir -p /user/bigdata/stocks/raw/sp500
docker exec namenode hdfs dfs -mkdir -p /user/bigdata/stocks/raw/forbes2000
#place the dataset files in it
docker exec namenode hdfs dfs -put /data/stocks/nasdaq/csv/ /user/bigdata/stocks/raw/nasdaq/
docker exec namenode hdfs dfs -put /data/stocks/sp500/csv/ /user/bigdata/stocks/raw/sp500/
docker exec namenode hdfs dfs -put /data/stocks/nyse/csv/ /user/bigdata/stocks/raw/nyse/
docker exec namenode hdfs dfs -put /data/stocks/forbes2000/csv/ /user/bigdata/stocks/raw/forbes2000/

#Start Command for Run Spark Master
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

spark = SparkSession.builder \
    .appName("StockMarketAnalysis") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "12g") \
    .config("spark.driver.memory", "12g") \
    .config("spark.sql.shuffle.partitions", "8") \
    .config("spark.executor.cores", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"✓ Spark {spark.version} ready")
print(f"✓ Master: {spark.sparkContext.master}")
#End Command

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

#Start Command for LOADING DATA FROM ALL EXCHANGES 
import pandas as pd
import numpy as np
import glob
import os
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, roc_auc_score, roc_curve)

# Automatic and safe detection of the user's home directory
HOME = os.path.expanduser("~")
OUTPUT_DIR = os.path.join(HOME, "ml", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 55)
print("  LOADING DATA FROM ALL EXCHANGES")
print("=" * 55)

all_dfs = []
#Update dataset input paths based on the user's home directory 
exchanges = {
    'nasdaq':     os.path.join(HOME, 'data/stocks/nasdaq/csv/*.csv'),
    'nyse':       os.path.join(HOME, 'data/stocks/nyse/csv/*.csv'),
    'sp500':      os.path.join(HOME, 'data/stocks/sp500/csv/*.csv'),
    'forbes2000': os.path.join(HOME, 'data/stocks/forbes2000/csv/*.csv'),
}

for exchange, pattern in exchanges.items():
    files = glob.glob(pattern)[:80]
    if not files:
        print(f"⚠ {exchange}: no files found at {pattern}")
        continue
    count = 0
    for f in files:
        try:
            tmp = pd.read_csv(f,
                usecols=lambda c: c.strip() in
                    ['Date','Open','High','Low','Close','Volume'])
            tmp.columns = [c.strip() for c in tmp.columns]
            tmp['symbol']   = os.path.basename(f).replace('.csv','')
            tmp['exchange'] = exchange
            all_dfs.append(tmp)
            count += 1
        except:
            continue
    print(f"✓ {exchange}: {count} files loaded")

if not all_dfs:
    raise ValueError("No files found! Please make sure the data folder exists in your home directory.")

pdf = pd.concat(all_dfs, ignore_index=True)
print(f"\n✓ Raw rows: {len(pdf):,}")

# Clean data
pdf['Date']  = pd.to_datetime(pdf['Date'], dayfirst=True, errors='coerce')
pdf = pdf.dropna(subset=['Date','Close','Open','Volume'])
pdf = pdf[(pdf['Close'] > 0) & (pdf['Open'] > 0) & (pdf['Volume'] > 0)]

# Feature Engineering
pdf['daily_return'] = (pdf['Close'] - pdf['Open']) / pdf['Open'] * 100
pdf['price_range']  = pdf['High']  - pdf['Low']
pdf['year']         = pdf['Date'].dt.year
pdf['month']        = pdf['Date'].dt.month
pdf['day_of_week']  = pdf['Date'].dt.dayofweek
pdf['direction']    = (pdf['daily_return'] >= 0).astype(int)
pdf = pdf.dropna(subset=['daily_return'])

print(f"✓ Clean rows: {len(pdf):,}")
print(f"✓ Memory: {pdf.memory_usage().sum()/1024**2:.1f} MB")
print(f"✓ Date range: {pdf['Date'].min().date()} → {pdf['Date'].max().date()}")
print(f"\n✓ Records per exchange:")
print(pdf['exchange'].value_counts().to_string())
print(f"\n✓ Sample data:")
print(pdf[['Date','exchange','symbol','Close','daily_return','direction']].head(8).to_string())
#End of command 

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

#Start Command for EPLORATORY ANALYSIS (Spark SQL equiv.)
print("\n" + "="*55)
print("  TASK 3 - EXPLORATORY ANALYSIS (Spark SQL equiv.)")
print("="*55)

print("\n--- Query 1: Summary Statistics per Exchange ---")
summary = pdf.groupby('exchange').agg(
    total_records   = ('Close','count'),
    avg_close       = ('Close', lambda x: round(x.mean(),2)),
    min_close       = ('Close', lambda x: round(x.min(),2)),
    max_close       = ('Close', lambda x: round(x.max(),2)),
    avg_volume_M    = ('Volume', lambda x: round(x.mean()/1e6,2)),
    avg_daily_return= ('daily_return', lambda x: round(x.mean(),4)),
).reset_index()
print(summary.to_string(index=False))

print("\n--- Query 2: Yearly Analysis (last 15 years) ---")
yearly = pdf[pdf['year'] >= 2008].groupby('year').agg(
    avg_close    = ('Close',  lambda x: round(x.mean(),2)),
    total_vol_M  = ('Volume', lambda x: round(x.sum()/1e6,0)),
    avg_return   = ('daily_return', lambda x: round(x.mean(),4)),
    trading_days = ('Close','count')
).reset_index().sort_values('year', ascending=False).head(15)
print(yearly.to_string(index=False))

print("\n--- Query 3: Market Direction Distribution ---")
direction = pdf.groupby('exchange')['direction'].agg(['sum','count'])
direction['up_pct']   = (direction['sum']   / direction['count'] * 100).round(2)
direction['down_pct'] = (100 - direction['up_pct']).round(2)
direction.columns     = ['up_days','total_days','up_%','down_%']
print(direction.to_string())

print("\n--- Query 4: Top 10 Worst Days ---")
worst = pdf.nsmallest(10, 'daily_return')[
    ['Date','exchange','symbol','Close','daily_return','Volume']
].copy()
worst['daily_return'] = worst['daily_return'].round(3)
worst['Volume_M']     = (worst['Volume']/1e6).round(1)
print(worst[['Date','exchange','symbol','Close','daily_return','Volume_M']].to_string(index=False))

print("\n--- Query 5: Monthly Seasonal Patterns ---")
monthly = pdf.groupby('month').agg(
    avg_return  = ('daily_return', lambda x: round(x.mean(),4)),
    avg_range   = ('price_range',  lambda x: round(x.mean(),4)),
    days        = ('Close','count')
).reset_index()
month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
monthly['month_name'] = monthly['month'].map(month_names)
print(monthly[['month','month_name','avg_return','avg_range','days']].to_string(index=False))
#End of Command

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

#Start Command for MACHINE LEARNING PIPELINE
print("\n" + "="*55)
print("  TASK 4 - MACHINE LEARNING PIPELINE")
print("="*55)

FEATURES = ['Close','Open','High','Low','Volume',
            'daily_return','price_range','month','day_of_week']

pdf_ml  = pdf[FEATURES + ['direction']].dropna()
X = pdf_ml[FEATURES].values
y = pdf_ml['direction'].values

# Temporal split - Time-based train-test split for time series
split   = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

scaler  = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

print(f"✓ Train samples: {len(X_train):,}")
print(f"✓ Test samples:  {len(X_test):,}")
print(f"✓ Features:      {FEATURES}")

models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=100, max_depth=8,
        class_weight='balanced', random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100, learning_rate=0.1,
        max_depth=5, random_state=42),
}

results = {}
for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]
    results[name] = {
        'model':     model,
        'y_pred':    y_pred,
        'y_prob':    y_prob,
        'accuracy':  accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall':    recall_score(y_test, y_pred, zero_division=0),
        'f1':        f1_score(y_test, y_pred, zero_division=0),
        'auc':       roc_auc_score(y_test, y_prob),
    }
    r = results[name]
    print(f"  Accuracy:  {r['accuracy']:.4f}")
    print(f"  Precision: {r['precision']:.4f}")
    print(f"  Recall:    {r['recall']:.4f}")
    print(f"  F1-Score:  {r['f1']:.4f}")
    print(f"  ROC-AUC:   {r['auc']:.4f}")

best_name = max(results, key=lambda k: results[k]['f1'])
print(f"\n Best Model: {best_name} (F1={results[best_name]['f1']:.4f})")
#End of Command 

#────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

# Start Command for Generating plot
print("\nGenerating plots...")

plt.style.use('dark_background')
COLORS = ['#e94560','#06d6a0']

# ── Figure 1: Results Dashboard ───────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Stock Market Direction Prediction — Results Dashboard',
             fontsize=15, fontweight='bold', color='white')

# Confusion Matrix
best = results[best_name]
cm   = confusion_matrix(y_test, best['y_pred'])
sns.heatmap(cm, annot=True, fmt='d', ax=axes[0,0],
            cmap='Blues', xticklabels=['DOWN','UP'],
            yticklabels=['DOWN','UP'], linewidths=0.5)
axes[0,0].set_title(f'Confusion Matrix\n{best_name}', fontweight='bold')
axes[0,0].set_xlabel('Predicted Label')
axes[0,0].set_ylabel('True Label')

# ROC Curve
for (name, res), color in zip(results.items(), COLORS):
    fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
    axes[0,1].plot(fpr, tpr, color=color, lw=2.5,
                   label=f"{name}\n(AUC={res['auc']:.4f})")
axes[0,1].plot([0,1],[0,1],'w--', alpha=0.4, label='Random (0.50)')
axes[0,1].set_title('ROC Curves', fontweight='bold')
axes[0,1].set_xlabel('False Positive Rate')
axes[0,1].set_ylabel('True Positive Rate')
axes[0,1].legend(fontsize=8, loc='lower right')
axes[0,1].grid(alpha=0.2)
axes[0,1].set_xlim([0,1])
axes[0,1].set_ylim([0,1.05])

# Feature Importance
rf  = results['Random Forest']['model']
imp = rf.feature_importances_
idx = np.argsort(imp)[::-1]
bar_colors = ['#2E75B6' if i < 3 else '#5BA3D9' for i in range(len(FEATURES))]
axes[1,0].bar(range(len(FEATURES)), imp[idx], color=bar_colors, edgecolor='white', linewidth=0.5)
axes[1,0].set_xticks(range(len(FEATURES)))
axes[1,0].set_xticklabels([FEATURES[i] for i in idx], rotation=45, ha='right', fontsize=9)
axes[1,0].set_title('Feature Importance\nRandom Forest', fontweight='bold')
axes[1,0].set_ylabel('Importance Score')
axes[1,0].grid(axis='y', alpha=0.3)

# Model Comparison
metrics       = ['accuracy','precision','recall','f1','auc']
metric_labels = ['Accuracy','Precision','Recall','F1','ROC-AUC']
x     = np.arange(len(metrics))
width = 0.35
for i, (name, res) in enumerate(results.items()):
    vals = [res[m] for m in metrics]
    bars = axes[1,1].bar(x + i*width, vals, width,
                         label=name, color=COLORS[i], alpha=0.85, edgecolor='white')
    for bar, val in zip(bars, vals):
        axes[1,1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=7, color='white')
axes[1,1].set_xticks(x + width/2)
axes[1,1].set_xticklabels(metric_labels, fontsize=9)
axes[1,1].set_ylim([0, 1.18])
axes[1,1].set_title('Model Performance Comparison', fontweight='bold')
axes[1,1].legend(fontsize=9)
axes[1,1].grid(axis='y', alpha=0.3)

plt.tight_layout()
# Automatically save to the user's allowed folder
path1 = os.path.join(OUTPUT_DIR, "results_dashboard.png")
plt.savefig(path1, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print(f"✓ Saved: {path1}")

# ── Figure 2: Exchange Analysis ───────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle('Stock Market — Exchange Analysis', fontsize=14, fontweight='bold')

# Direction per exchange
ex_data = pdf.groupby('exchange')['direction'].agg(['sum','count']).reset_index()
ex_data['up_pct']   = ex_data['sum']   / ex_data['count'] * 100
ex_data['down_pct'] = 100 - ex_data['up_pct']
x2    = np.arange(len(ex_data))
axes2[0].bar(x2 - 0.2, ex_data['up_pct'],   0.4, label='UP days %',   color='#06d6a0', alpha=0.85)
axes2[0].bar(x2 + 0.2, ex_data['down_pct'], 0.4, label='DOWN days %', color='#e94560', alpha=0.85)
axes2[0].set_xticks(x2)
axes2[0].set_xticklabels(ex_data['exchange'], fontsize=10)
axes2[0].set_title('UP vs DOWN Days per Exchange', fontweight='bold')
axes2[0].set_ylabel('Percentage (%)')
axes2[0].legend()
axes2[0].grid(axis='y', alpha=0.3)
axes2[0].set_ylim([0, 80])

# Monthly returns
monthly_plot = pdf.groupby('month')['daily_return'].mean()
bar_c = ['#06d6a0' if v >= 0 else '#e94560' for v in monthly_plot.values]
axes2[1].bar(monthly_plot.index, monthly_plot.values, color=bar_c, edgecolor='white', linewidth=0.5)
axes2[1].set_xticks(range(1,13))
axes2[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun',
                           'Jul','Aug','Sep','Oct','Nov','Dec'], fontsize=9)
axes2[1].set_title('Average Monthly Return (%)', fontweight='bold')
axes2[1].set_ylabel('Avg Daily Return (%)')
axes2[1].axhline(y=0, color='white', linestyle='--', alpha=0.5)
axes2[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
# Automatically save to the user's allowed folder
path2 = os.path.join(OUTPUT_DIR, "exchange_analysis.png")
plt.savefig(path2, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print(f"✓ Saved: {path2}")

print("\n" + "="*55)
print("  ✓ ALL DONE!")
print("  Screenshots to take:")
print(f"  1. Cell 1 output  → Task 2 (data loading)")
print(f"  2. Cell 2 output  → Task 3 (SQL queries)")
print(f"  3. {path1}  → Task 4")
print(f"  4. {path2}  → Task 4")
print("="*55)
#End of Command
```


### Second Way (Script)
```bash
# Copy script to Spark container
docker cp spark/01_spark_processing.py spark-master:/opt/spark-apps/

# Submit to Spark cluster
docker exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --executor-memory 8g \
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

##  Web UIs for Screenshots (Task 2 & 3)

| Service | URL | What to screenshot |
|---------|-----|-------------------|
| Jupyter Lab | http://localhost:8888 | Code execution |
| Spark Master | http://localhost:8080 | Running jobs |
| HDFS NameNode | http://localhost:9870 | File browser |
| YARN Manager | http://localhost:8088 | Resource usage |
| Hive Web UI | http://localhost:10002 | Query results |

---

##  Expected Output Files

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

##  Troubleshooting

**NameNode won't start:**
```bash
docker exec namenode hdfs namenode -format -force
docker-compose restart namenode
```

**Out of memory error:**
- Increase Docker Desktop memory to 16GB
- Settings → Resources → Memory → 16GB

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

##  Assignment Checklist

- [ ] Task 1: Problem Definition written (20%)
- [ ] Task 2: Docker setup + HDFS + Hive tables (15%)
  - [ ] Screenshot: HDFS NameNode UI
  - [ ] Screenshot: Hive tables created
- [ ] Task 3: Spark processing + Hive queries (25%)
  - [ ] Screenshot: Spark job running
  - [ ] Screenshot: Hive query results
  - [ ] Spark vs Hive comparison table
- [ ] Task 4: ML model trained + visualizations (30%)
  - [ ] confusion_matrix.png
  - [ ] roc_curves.png
  - [ ] feature_importance.png
  - [ ] model_comparison.png
- [ ] Task 5: Reflection written (10%)

---

##  Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Apache Hadoop | 3.2.1 | HDFS distributed storage & cluster resource management (YARN) |
| Apache Spark | 3.3.0 | In-memory distributed data processing & core analytics |
| Apache Hive | 3.1.2 | Data warehousing infrastructure & HiveQL querying |
| PySpark | 3.3.0 | Python programmatic interface for distributed Spark operations |
| Scikit-learn | Latest | Core Machine Learning algorithms and evaluation metrics |
| XGBoost | Latest | Advanced Gradient Boosting classification models |
| Docker / Compose | Latest | Container orchestration and distributed cluster isolation |
| Python | 3.9+ | Primary language |
| Jupyter Lab | Latest | Interactive development |
