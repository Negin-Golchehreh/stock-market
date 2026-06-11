USE stock_db;

-- ── Query 1: Load Processed Data into Hive Table ──────────────
-- (Run this once after Spark processing is done)
INSERT OVERWRITE TABLE stock_prices_clean
SELECT
    TO_DATE(Date)         AS trade_date,
    'MULTI'               AS symbol,
    Open                  AS open_price,
    High                  AS high_price,
    Low                   AS low_price,
    Close                 AS close_price,
    Adj_Close             AS adj_close,
    Volume                AS volume,
    ROUND((Close - Open) / Open * 100, 4) AS daily_return,
    ROUND(High - Low, 4)  AS price_range,
    YEAR(TO_DATE(Date))   AS year,
    MONTH(TO_DATE(Date))  AS month
FROM stock_prices_raw
WHERE Close > 0 AND Volume > 0 AND Date IS NOT NULL;

-- ── Query 2: Basic Summary Statistics ─────────────────────────
SELECT
    'Summary Statistics' AS analysis,
    COUNT(*)             AS total_records,
    ROUND(AVG(close_price), 2) AS avg_close,
    ROUND(MIN(close_price), 2) AS min_close,
    ROUND(MAX(close_price), 2) AS max_close,
    ROUND(AVG(volume) / 1000000, 2) AS avg_volume_M,
    ROUND(AVG(daily_return), 4)     AS avg_daily_return_pct
FROM stock_prices_clean;

-- ── Query 3: Monthly Aggregation (for ML features) ────────────
INSERT OVERWRITE TABLE stock_monthly_summary
SELECT
    symbol,
    year,
    month,
    ROUND(AVG(close_price), 2)   AS avg_close,
    ROUND(MAX(high_price), 2)    AS max_high,
    ROUND(MIN(low_price), 2)     AS min_low,
    SUM(volume)                  AS total_volume,
    ROUND(AVG(daily_return), 4)  AS avg_daily_return,
    ROUND(STDDEV(close_price), 4) AS volatility
FROM stock_prices_clean
GROUP BY symbol, year, month;

-- Verify
SELECT * FROM stock_monthly_summary ORDER BY year, month LIMIT 20;

-- ── Query 4: Top Trading Volume Years ─────────────────────────
SELECT
    year,
    ROUND(AVG(avg_close), 2)    AS yearly_avg_price,
    SUM(total_volume) / 1000000 AS total_volume_M,
    ROUND(AVG(avg_daily_return), 4) AS avg_return_pct,
    ROUND(AVG(volatility), 4)   AS avg_volatility
FROM stock_monthly_summary
GROUP BY year
ORDER BY year DESC;

-- ── Query 5: Market Crash Detection (drops > 5% in one day) ──
SELECT
    trade_date,
    close_price,
    daily_return,
    volume,
    CASE
        WHEN daily_return < -5  THEN 'CRASH (>5% drop)'
        WHEN daily_return < -2  THEN 'Sharp drop (2-5%)'
        WHEN daily_return < 0   THEN 'Down day'
        WHEN daily_return < 2   THEN 'Up day'
        ELSE 'Strong rally (>2%)'
    END AS market_event
FROM stock_prices_clean
ORDER BY daily_return ASC
LIMIT 50;

-- ── Query 6: Seasonal Patterns (Monthly Avg Return) ───────────
SELECT
    month,
    CASE month
        WHEN 1 THEN 'January'   WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'     WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'       WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'      WHEN 8 THEN 'August'
        WHEN 9 THEN 'September' WHEN 10 THEN 'October'
        WHEN 11 THEN 'November' WHEN 12 THEN 'December'
    END AS month_name,
    ROUND(AVG(avg_daily_return), 4) AS avg_monthly_return,
    ROUND(AVG(volatility), 4)       AS avg_volatility,
    COUNT(*)                        AS years_of_data
FROM stock_monthly_summary
GROUP BY month
ORDER BY month;
