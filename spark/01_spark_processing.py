# ================================================================
#  Hive   query Spark SQL
#  Jupyter : http://localhost:8888
# ================================================================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

#Spark Hive-compatible SQL 
spark = SparkSession.builder \
    .appName("StockMarketHiveSQL") \
    .master("spark://spark-master:7077") \
    .config("spark.sql.warehouse.dir", "/home/jovyan/data/warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# enableHiveSupport:
# spark = SparkSession.builder \
#     .appName("StockMarketSQL") \
#     .master("spark://spark-master:7077") \
#     .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print(f"✓ Spark {spark.version} ready")

import os, glob
from pathlib import Path

#  Find CSV  
data_paths = [
    "/home/jovyan/data/stocks/",
    "/home/jovyan/data/",
    "/data/stocks/",
]

df = None
for path in data_paths:
    csvs = glob.glob(f"{path}**/*.csv", recursive=True)
    if csvs:
        df = spark.read.option("header","true").option("inferSchema","true").csv(f"{path}**/*.csv")
        print(f"✓ Loaded {df.count():,} rows from {path}")
        break

if df is None:
    # Synthetic data for test
    import pandas as pd, numpy as np
    np.random.seed(42)
    n = 100000
    dates = pd.date_range("2010-01-01", periods=n, freq="B")
    price = 100.0; prices = []
    for _ in range(n):
        price *= (1 + np.random.normal(0.0002, 0.015))
        prices.append(max(price, 1.0))
    pdf = pd.DataFrame({
        'Date': [str(d.date()) for d in dates],
        'Open':  [p*np.random.uniform(0.99,1.01) for p in prices],
        'High':  [p*np.random.uniform(1.00,1.02) for p in prices],
        'Low':   [p*np.random.uniform(0.98,1.00) for p in prices],
        'Close': prices,
        'Adj_Close': prices,
        'Volume': np.random.randint(1000000, 50000000, n),
    })
    df = spark.createDataFrame(pdf)
    print(f"✓ Using synthetic data: {df.count():,} rows")

# ── Create Temp View (average Hive Table)
df = df.withColumn("Date",   F.to_date("Date")) \
       .withColumn("year",   F.year("Date")) \
       .withColumn("month",  F.month("Date")) \
       .withColumn("daily_return",
           F.round((F.col("Close")-F.col("Open"))/F.col("Open")*100, 4)) \
       .withColumn("price_range", F.round(F.col("High")-F.col("Low"), 4))

df.createOrReplaceTempView("stock_prices")
print("✓ Temp view 'stock_prices' created")
print(f"  Columns: {df.columns}")

# Query 1: Summary Statistics  (average Hive Query 2)
print("\n" + "="*55)
print("Query 1: Summary Statistics")
print("="*55)
spark.sql("""
    SELECT
        COUNT(*)                        AS total_records,
        ROUND(AVG(Close), 2)            AS avg_close,
        ROUND(MIN(Close), 2)            AS min_close,
        ROUND(MAX(Close), 2)            AS max_close,
        ROUND(AVG(Volume)/1000000, 2)   AS avg_volume_M,
        ROUND(AVG(daily_return), 4)     AS avg_daily_return_pct
    FROM stock_prices
""").show()

# Query 2: Year-over-Year Analysis  (average Hive Query 4)
print("="*55)
print("Query 2: Year-over-Year Analysis")
print("="*55)
spark.sql("""
    SELECT
        year,
        ROUND(AVG(Close), 2)            AS avg_close_price,
        ROUND(SUM(Volume)/1000000, 0)   AS total_volume_M,
        ROUND(AVG(daily_return), 4)     AS avg_daily_return_pct,
        ROUND(STDDEV(Close), 2)         AS price_volatility,
        COUNT(*)                        AS trading_days
    FROM stock_prices
    GROUP BY year
    ORDER BY year DESC
""").show(20)

# Query 3: Market Crash Detection  (average Hive Query 5)

print("="*55)
print("Query 3: Extreme Market Days (Top 10 Drops)")
print("="*55)
spark.sql("""
    SELECT
        Date,
        ROUND(Close, 2)         AS close_price,
        ROUND(daily_return, 3)  AS daily_return_pct,
        ROUND(Volume/1000000,1) AS volume_M,
        CASE
            WHEN daily_return < -5 THEN 'CRASH (>5% drop)'
            WHEN daily_return < -2 THEN 'Sharp Drop'
            WHEN daily_return < 0  THEN 'Down Day'
            WHEN daily_return < 2  THEN 'Up Day'
            ELSE 'Strong Rally'
        END AS market_event
    FROM stock_prices
    ORDER BY daily_return ASC
    LIMIT 10
""").show()

# Query 4: Seasonal Patterns  (average Hive Query 6)

print("="*55)
print("Query 4: Monthly Seasonal Patterns")
print("="*55)
spark.sql("""
    SELECT
        month,
        CASE month
            WHEN 1 THEN 'Jan' WHEN 2 THEN 'Feb' WHEN 3 THEN 'Mar'
            WHEN 4 THEN 'Apr' WHEN 5 THEN 'May' WHEN 6 THEN 'Jun'
            WHEN 7 THEN 'Jul' WHEN 8 THEN 'Aug' WHEN 9 THEN 'Sep'
            WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dec'
        END AS month_name,
        ROUND(AVG(daily_return), 4)  AS avg_return_pct,
        ROUND(STDDEV(Close), 2)      AS avg_volatility,
        COUNT(DISTINCT year)         AS years_of_data
    FROM stock_prices
    GROUP BY month
    ORDER BY month
""").show()
# Query 5: Direction Distribution
print("="*55)
print("Query 5: Market Direction Distribution")
print("="*55)
spark.sql("""
    SELECT
        CASE WHEN daily_return >= 0 THEN 'UP' ELSE 'DOWN' END AS direction,
        COUNT(*) AS count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
    FROM stock_prices
    GROUP BY CASE WHEN daily_return >= 0 THEN 'UP' ELSE 'DOWN' END
""").show()

print("\n✓ All Hive-equivalent queries done via Spark SQL!")
spark.stop()
