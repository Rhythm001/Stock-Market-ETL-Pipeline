-- stock_prices_row (the data landing zone)

CREATE TABLE stock_prices_raw (
    id  SERIAL PRIMARY KEY,
    ticker  VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    open_price NUMERIC(12,4),
    high_price NUMERIC(12,4),
    low_price NUMERIC(12,4),
    close_price NUMERIC(12,4),
    volume BIGINT,
    ingested_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (ticker, trade_date)
);


-- stock_price_enriched (transformed, with indicators)
CREATE TABLE stock_prices_enriched(
    ticker VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    close_price NUMERIC(12,4),
    volume BIGINT,
    daily_return_pct NUMERIC(8,4),
    sma_20 NUMERIC(12,4),
    sma_50 NUMERIC(12,4),
    rsi_14 NUMERIC(6,4),
    bb_upper NUMERIC(12,4),
    bb_lower NUMERIC(12,4),
    bb_bandwidth NUMERIC(8,4),
    vol_zscore NUMERIC(8,4),
    vol_spike BOOLEAN,
    computed_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (ticker, trade_date)
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    execution_date TIMESTAMP DEFAULT NOW(),
    report_json TEXT
);

--select * from stock_prices_raw;


--select table_name from information_schema."tables" t 
--where t.table_schema = 'public';


--drop table if exists stock_prices_raw;
--drop table if exists stock_prices_enriched;