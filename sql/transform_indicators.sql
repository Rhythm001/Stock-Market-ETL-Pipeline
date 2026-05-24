-- Computes all 5 indicators using window functions

INSERT INTO stock_prices_enriched
SELECT
    ticker,
    trade_date,
    close_price,
    volume,

    -- Daily Return
    ROUND(
        (close_price - LAG(close_price) OVER w) / LAG(close_price) over w*100, 4)
        AS daily_return_pct,

    -- SMA-20
    ROUND (AVG(close_price) over (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
    AS sma_20,

    -- SMA-50
    ROUND (AVG(close_price) over (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
    AS sma_50,

    -- RSI-14 (computed in Python, stored here)
    rsi_14,

    -- Bollinger Bands
    ROUND(AVG(close_price) OVER w20 + 2*STDEV(close_price) OVER w20, 2) AS bb_upper,
    ROUND(AVG(close_price) OVER w20 - 2*STDEV(close_price) over w20, 2) AS bb_lower,

    -- Volume Spike Flag
    (volume - AVG(volume) over w20) / NULLIF(STDEV(volume) OVER w20, 0) > 2 AS vol_spike

    FROM stock_prices_staging
    WINDOW
    w as (PARTITION BY ticker ORDER BY trade_date),
    w20 AS (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
    ON CONFLICT (ticker, trade_date) DO UPDATE SET ...;


