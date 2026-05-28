-- Computes all 5 indicators using window functions

INSERT INTO stock_prices_enriched(
    ticker,
    trade_date,
    close_price,
    volume,
    daily_return_pct,
    sma_20,
    sma_50,
    bb_upper,
    bb_lower,
    bb_bandwidth,
    vol_zscore,
    vol_spike,
    computed_at
)
SELECT 
    ticker,
    trade_date,
    close_price,
    volume,

    -- Daily Return
    ROUND(
        (close_price - LAG(close_price) OVER w) / NULLIF(LAG(close_price) over w , 0) * 100, 4)
        AS daily_return_pct,

    -- SMA-20
    ROUND (AVG(close_price) over (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
    AS sma_20,

    -- SMA-50
    ROUND (AVG(close_price) over (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
    AS sma_50,

    -- RSI-14 (computed in Python, stored here)
    -- rsi_14,

    -- Bollinger Bands
    ROUND(AVG(close_price) OVER w20 + 2*STDDEV(close_price) OVER w20, 2) AS bb_upper,
    ROUND(AVG(close_price) OVER w20 - 2*STDDEV(close_price) over w20, 2) AS bb_lower,

    -- BB bandwidth: (upper-lower) / sma_20
    ROUND( 4 * STDDEV(close_price) over w20 / NULLIF(AVG(close_price) over w20, 0), 4) AS bb_bandwidth,

    -- Volume Z-Score
    ROUND((volume - AVG(volume) OVER w20)/ NULLIF(STDDEV(volume) over w20, 0), 4) AS vol_zscore,

    -- Volume Spike Flag
    (volume - AVG(volume) over w20) / NULLIF(STDDEV(volume) OVER w20, 0) > 2 AS vol_spike,

    NOW() AS computed_at


    FROM stock_prices_raw

    WINDOW
        w as (PARTITION BY ticker ORDER BY trade_date),
        w20 AS (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w50 AS (PARTITION BY ticker ORDER BY trade_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW)
    ON CONFLICT (ticker, trade_date) DO NOTHING;


