# def generate_report():
#     print("Generating stock ETL report...")

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine, text
from src.logger import logger

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "/opt/airflow/reports"))
TICKERS_EXPECTED = int(os.getenv("TICKERS_EXPECTED", 10))


def get_engine():
    DB_URL = os.getenv("DB_URL")
    return create_engine(DB_URL)


# Helpers

def _scalar(conn, sql: str):
    return conn.execute(text(sql)).scalar()

def _rows(conn, sql: str) -> list[dict]:
    result = conn.execute(text(sql))
    keys = result.keys()
    return [dict(zip(keys, row)) for row in result.fetchall()]


def _pipeline_meta(conn) -> dict:
    """ When did the pipeline last runa nd over what date range."""
    latest_ingested = _scalar(conn, "SELECT MAX(ingested_at) FROM stock_prices_raw")
    latest_trade = _scalar(conn, "SELECT MAX(trade_date) FROM stock_prices_raw")
    earliest_trade = _scalar(conn, "SELECT MIN(trade_date) FROM stock_prices_raw")
    
    return {
        "report_generated_at" : datetime.now(timezone.utc).isoformat(),
        "last_ingestion_at" : str(latest_ingested),
        "latest_trade_date" : str(latest_trade),
        "earliest_trade_date" : str(earliest_trade),
    }
    
def _row_counts(conn) -> dict:
    """Row counts for both tables."""
    raw_count = _scalar(conn, "SELECT COUNT(*) FROM stock_prices_raw")
    enriched_count = _scalar(conn, "SELECT COUNT(*) FROM stock_prices_enriched")
    ticker_count = _scalary(conn, """
                            SELECT COUNT(DISTINCT ticker)
                            FROM stock_prices_enriched
                            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)""")
    
    return {
        "raw_row" : int(raw_count),
        "enriched_rows" : int(enriched_count),
        "tickers_latest_date" : TICKERS_EXPECTED, 
        "ticker_completeness_ok" : ticker_count == TICKERS_EXPECTED,
    }
    
    
def _quality_summary(conn) -> dict:
    """Re-run the same quality checks the piepline runs, capture counts."""
    null_close = _scalar(conn, """
                         SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price IS NULL""")
    invalid_price = _scalar(conn, """
                            SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price<=0""")
    checks = {
        "null_close_prices" : int(null_close),
        "invalid_prices" : int(invalid_price),
    }
    
    checks["all_passed"] = all(v == 0 for v in checks.values())
    
    return checks

def _freshness(conn) -> dict:
    """How stale is the data compared to today."""
    latest_trade = _scalar(conn, "SELECT MAX(trade_date) FROM stock_prices_enriched")
    today = datetime.now(timezone.utc).date()
    lag_days = (today - latest_trade).days if latest_trade else None
 
    return {
        "latest_trade_date": str(latest_trade),
        "today":             str(today),
        "lag_days":          lag_days,
        # Markets closed on weekends, so ≤3 is acceptable
        "freshness_ok":      lag_days is not None and lag_days <= 3,
    }
 
 
def _per_ticker_metrics(conn) -> list[dict]:
    """Latest snapshot of every ticker: price, return, RSI, SMA signal, vol spike."""
    rows = _rows(conn, """
        SELECT
            ticker,
            trade_date,
            close_price,
            daily_return_pct,
            sma_20,
            sma_50,
            rsi_14,
            bb_bandwidth,
            vol_zscore,
            vol_spike,
            CASE
                WHEN sma_20 > sma_50 THEN 'bullish'
                WHEN sma_20 < sma_50 THEN 'bearish'
                ELSE 'neutral'
            END AS sma_signal
        FROM stock_prices_enriched
        WHERE trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
        ORDER BY ticker
    """)
 
    # cast Decimal / date to plain Python types for JSON serialisation
    clean = []
    for r in rows:
        clean.append({k: (float(v) if hasattr(v, "__float__") else str(v) if hasattr(v, "isoformat") else v)
                      for k, v in r.items()})
    return clean
 
 
def _anomalies(conn) -> list[str]:
    """Surface any noteworthy conditions worth logging."""
    notes = []
 
    spikes = _rows(conn, """
        SELECT ticker, trade_date, vol_zscore
        FROM stock_prices_enriched
        WHERE vol_spike = TRUE
          AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
        ORDER BY vol_zscore DESC
    """)
    for s in spikes:
        notes.append(f"Volume spike: {s['ticker']} on {s['trade_date']} (z={s['vol_zscore']:.2f})")
 
    overbought = _rows(conn, """
        SELECT ticker, rsi_14
        FROM stock_prices_enriched
        WHERE rsi_14 > 70
          AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
    """)
    for o in overbought:
        notes.append(f"RSI overbought: {o['ticker']} (RSI={o['rsi_14']:.1f})")
 
    oversold = _rows(conn, """
        SELECT ticker, rsi_14
        FROM stock_prices_enriched
        WHERE rsi_14 < 30
          AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
    """)
    for o in oversold:
        notes.append(f"RSI oversold: {o['ticker']} (RSI={o['rsi_14']:.1f})")
 
    return notes
 
 
# ── main entry point ──────────────────────────────────────────────────────────
 
def generate_report() -> Path:
    """
    Build a full ETL run report, write it to REPORTS_DIR as JSON,
    and return the file path.
    """
    logger.info("Starting report generation")
 
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
    engine = get_engine()
 
    with engine.connect() as conn:
        report = {
            "pipeline_meta":    _pipeline_meta(conn),
            "row_counts":       _row_counts(conn),
            "quality_summary":  _quality_summary(conn),
            "freshness":        _freshness(conn),
            "per_ticker":       _per_ticker_metrics(conn),
            "anomalies":        _anomalies(conn),
        }
 
    # ── overall status ────────────────────────────────────────────────────────
    report["status"] = (
        "PASS"
        if report["quality_summary"]["all_passed"]
        and report["row_counts"]["ticker_completeness_ok"]
        and report["freshness"]["freshness_ok"]
        else "WARN"
    )
 
    # ── write JSON ────────────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path  = REPORTS_DIR / f"etl_report_{timestamp}.json"
 
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
 
    logger.info(f"Report written → {out_path}  |  status={report['status']}")
    logger.info(f"Anomalies detected: {len(report['anomalies'])}")
 
    return out_path
 
 
if __name__ == "__main__":
    generate_report()
 