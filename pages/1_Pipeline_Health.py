"""
pages/1_Pipeline_Health.py
──────────────────────────
Pipeline Health dashboard page.
Reads directly from stock_prices_raw and stock_prices_enriched.
No dependency on report JSON files.
"""

import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Pipeline Health",
    page_icon="⚙️",
    layout="wide",
)

# ── styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* dark terminal background */
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #58a6ff !important;
    letter-spacing: -0.5px;
}

/* metric cards */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px 20px;
}

[data-testid="metric-container"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #8b949e !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.6rem !important;
    color: #c9d1d9 !important;
}

/* status badge */
.status-pass {
    display: inline-block;
    background: #1a3a2a;
    color: #3fb950;
    border: 1px solid #3fb950;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 4px;
    letter-spacing: 2px;
}
.status-warn {
    display: inline-block;
    background: #3a2a1a;
    color: #d29922;
    border: 1px solid #d29922;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 4px;
    letter-spacing: 2px;
}
.status-error {
    display: inline-block;
    background: #3a1a1a;
    color: #f85149;
    border: 1px solid #f85149;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 4px 14px;
    border-radius: 4px;
    letter-spacing: 2px;
}

/* section divider */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 6px;
    margin: 28px 0 16px 0;
}

/* check row */
.check-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 6px;
    margin-bottom: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
}
.check-ok   { color: #3fb950; }
.check-fail { color: #f85149; }

/* anomaly pill */
.anomaly-pill {
    display: inline-block;
    background: #1c2128;
    border: 1px solid #30363d;
    border-left: 3px solid #d29922;
    color: #c9d1d9;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    padding: 6px 14px;
    border-radius: 4px;
    margin: 4px 0;
    width: 100%;
}

/* dataframe */
[data-testid="stDataFrame"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── db connection ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_engine():
    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        st.error("DB_URL environment variable not set.")
        st.stop()
    return create_engine(DB_URL)


@st.cache_data(ttl=300)   # cache for 5 minutes
def load_health_data():
    engine = get_engine()
    with engine.connect() as conn:

        # ── row counts ────────────────────────────────────────────────────────
        raw_count      = conn.execute(text("SELECT COUNT(*) FROM stock_prices_raw")).scalar()
        enriched_count = conn.execute(text("SELECT COUNT(*) FROM stock_prices_enriched")).scalar()

        # ── dates ─────────────────────────────────────────────────────────────
        latest_ingested = conn.execute(
            text("SELECT MAX(ingested_at) FROM stock_prices_raw")
        ).scalar()
        latest_trade = conn.execute(
            text("SELECT MAX(trade_date) FROM stock_prices_enriched")
        ).scalar()
        earliest_trade = conn.execute(
            text("SELECT MIN(trade_date) FROM stock_prices_raw")
        ).scalar()

        # ── ticker completeness ───────────────────────────────────────────────
        ticker_count = conn.execute(text("""
            SELECT COUNT(DISTINCT ticker)
            FROM stock_prices_enriched
            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
        """)).scalar()

        # ── quality checks ────────────────────────────────────────────────────
        null_close = conn.execute(text("""
            SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price IS NULL
        """)).scalar()
        invalid_price = conn.execute(text("""
            SELECT COUNT(*) FROM stock_prices_enriched WHERE close_price <= 0
        """)).scalar()

        # ── per-ticker latest row ─────────────────────────────────────────────
        ticker_df = pd.read_sql(text("""
            SELECT
                ticker,
                trade_date,
                close_price,
                daily_return_pct,
                rsi_14,
                vol_spike,
                CASE
                    WHEN sma_20 > sma_50 THEN 'bullish'
                    WHEN sma_20 < sma_50 THEN 'bearish'
                    ELSE 'neutral'
                END AS sma_signal
            FROM stock_prices_enriched
            WHERE trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
            ORDER BY ticker
        """), conn)

        # ── anomalies ─────────────────────────────────────────────────────────
        anomalies = []

        spikes = pd.read_sql(text("""
            SELECT ticker, vol_zscore FROM stock_prices_enriched
            WHERE vol_spike = TRUE
              AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
            ORDER BY vol_zscore DESC
        """), conn)
        for _, r in spikes.iterrows():
            anomalies.append(f"⚡ Volume spike  {r['ticker']}  (z = {r['vol_zscore']:.2f})")

        overbought = pd.read_sql(text("""
            SELECT ticker, rsi_14 FROM stock_prices_enriched
            WHERE rsi_14 > 70
              AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
        """), conn)
        for _, r in overbought.iterrows():
            anomalies.append(f"🔴 RSI overbought  {r['ticker']}  (RSI = {r['rsi_14']:.1f})")

        oversold = pd.read_sql(text("""
            SELECT ticker, rsi_14 FROM stock_prices_enriched
            WHERE rsi_14 < 30
              AND trade_date = (SELECT MAX(trade_date) FROM stock_prices_enriched)
        """), conn)
        for _, r in oversold.iterrows():
            anomalies.append(f"🟢 RSI oversold  {r['ticker']}  (RSI = {r['rsi_14']:.1f})")

    # ── freshness ─────────────────────────────────────────────────────────────
    today = datetime.now(timezone.utc).date()
    lag_days = (today - latest_trade).days if latest_trade else None
    freshness_ok = lag_days is not None and lag_days <= 3

    # ── overall status ────────────────────────────────────────────────────────
    checks_ok = (null_close == 0) and (invalid_price == 0)
    tickers_ok = (ticker_count == 10)
    overall = "PASS" if (checks_ok and tickers_ok and freshness_ok) else "WARN"

    return {
        "raw_count":        int(raw_count),
        "enriched_count":   int(enriched_count),
        "latest_ingested":  str(latest_ingested),
        "latest_trade":     str(latest_trade),
        "earliest_trade":   str(earliest_trade),
        "ticker_count":     int(ticker_count),
        "null_close":       int(null_close),
        "invalid_price":    int(invalid_price),
        "lag_days":         lag_days,
        "freshness_ok":     freshness_ok,
        "checks_ok":        checks_ok,
        "tickers_ok":       tickers_ok,
        "overall":          overall,
        "ticker_df":        ticker_df,
        "anomalies":        anomalies,
    }


# ── render ────────────────────────────────────────────────────────────────────

st.markdown("## ⚙️  Pipeline Health")
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.8rem;'>"
    "Live view of ETL run status, data freshness, and quality checks."
    "</p>",
    unsafe_allow_html=True,
)

with st.spinner("Querying database..."):
    try:
        d = load_health_data()
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

# ── overall status banner ─────────────────────────────────────────────────────

badge_class = "status-pass" if d["overall"] == "PASS" else "status-warn"
st.markdown(
    f"<div style='margin-bottom:24px;'>"
    f"Overall status &nbsp; <span class='{badge_class}'>{d['overall']}</span>"
    f"&nbsp;&nbsp;<span style='color:#8b949e; font-size:0.8rem; font-family: IBM Plex Mono, monospace;'>"
    f"as of {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── top metrics row ───────────────────────────────────────────────────────────

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Raw Rows",      f"{d['raw_count']:,}")
c2.metric("Enriched Rows", f"{d['enriched_count']:,}")
c3.metric("Tickers (latest date)", f"{d['ticker_count']} / 10")
c4.metric("Data Lag",      f"{d['lag_days']}d" if d['lag_days'] is not None else "—")
c5.metric("Latest Trade",  d["latest_trade"])

# ── quality checks ────────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Quality Checks</div>", unsafe_allow_html=True)

checks = [
    ("Null close prices",         d["null_close"]    == 0, f"{d['null_close']} violations"),
    ("Invalid prices (≤ 0)",      d["invalid_price"] == 0, f"{d['invalid_price']} violations"),
    ("Ticker completeness (10)",  d["tickers_ok"],          f"{d['ticker_count']}/10 tickers"),
    ("Data freshness (≤ 3 days)", d["freshness_ok"],        f"{d['lag_days']}d lag"),
]

for label, passed, detail in checks:
    icon  = "✓" if passed else "✗"
    cls   = "check-ok" if passed else "check-fail"
    color = "#3fb950" if passed else "#f85149"
    st.markdown(
        f"<div class='check-row'>"
        f"<span class='{cls}' style='font-size:1rem; font-weight:600;'>{icon}</span>"
        f"<span style='flex:1; color:#c9d1d9;'>{label}</span>"
        f"<span style='color:{color}; font-size:0.8rem;'>{detail}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── anomalies ─────────────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Anomalies Detected</div>", unsafe_allow_html=True)

if d["anomalies"]:
    for note in d["anomalies"]:
        st.markdown(f"<div class='anomaly-pill'>{note}</div>", unsafe_allow_html=True)
else:
    st.markdown(
        "<div class='anomaly-pill' style='border-left-color:#3fb950; color:#8b949e;'>"
        "✓ No anomalies detected on latest trade date."
        "</div>",
        unsafe_allow_html=True,
    )

# ── per-ticker snapshot table ─────────────────────────────────────────────────

st.markdown("<div class='section-label'>Per-Ticker Snapshot (Latest Date)</div>", unsafe_allow_html=True)

df = d["ticker_df"].copy()

# clean up display
df.columns = ["Ticker", "Date", "Close", "Return %", "RSI-14", "Vol Spike", "SMA Signal"]
df["Close"]    = df["Close"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "—")
df["Return %"] = df["Return %"].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "—")
df["RSI-14"]   = df["RSI-14"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
df["Vol Spike"]= df["Vol Spike"].apply(lambda x: "⚡ Yes" if x else "No")
df["SMA Signal"]= df["SMA Signal"].apply(
    lambda x: "▲ Bullish" if x == "bullish" else ("▼ Bearish" if x == "bearish" else "— Neutral")
)

st.dataframe(df, use_container_width=True, hide_index=True)

# ── pipeline metadata ─────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Pipeline Metadata</div>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("Last Ingestion",    d["latest_ingested"])
m2.metric("Earliest Trade Date", d["earliest_trade"])
m3.metric("Latest Trade Date",  d["latest_trade"])

# ── refresh note ──────────────────────────────────────────────────────────────

st.markdown(
    "<p style='color:#484f58; font-family: IBM Plex Mono, monospace; "
    "font-size:0.7rem; margin-top:40px;'>"
    "Data cached for 5 minutes. Reload page to force refresh."
    "</p>",
    unsafe_allow_html=True,
)