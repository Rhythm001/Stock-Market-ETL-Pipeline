import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Stock Comparison", layout="wide")
st.title("Stock Stack Comparison 🏆")
st.caption("Rank and compare shortlisted equities using technical scoring models")

# -----------------------------
# DB Connection
# -----------------------------
DB_URL = os.getenv("DB_URL")

if not DB_URL:
    st.error("DB_URL environment variable not set")
    st.stop()

engine = create_engine(DB_URL)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    query = """
    SELECT
        ticker,
        date,
        close,
        volume,
        rsi_14,
        sma_20,
        sma_50,
        bb_upper,
        bb_lower
    FROM stock_prices_enriched
    ORDER BY date
    """
    return pd.read_sql(query, engine)

df = load_data()

if df.empty:
    st.warning("No data available")
    st.stop()

# -----------------------------
# Latest Snapshot
# -----------------------------
latest_date = df["date"].max()
latest = df[df["date"] == latest_date].copy()

# -----------------------------
# Derived Metrics
# -----------------------------
latest["momentum"] = (
    (latest["close"] - latest["sma_20"]) / latest["sma_20"]
)

latest["trend_strength"] = (
    (latest["sma_20"] - latest["sma_50"]) / latest["sma_50"]
)

latest["volatility"] = (
    (latest["bb_upper"] - latest["bb_lower"]) / latest["close"]
)

latest["rsi_score"] = 100 - abs(latest["rsi_14"] - 50)

# Normalize
for col in ["momentum", "trend_strength", "volatility", "rsi_score"]:
    latest[col] = (
        (latest[col] - latest[col].min()) /
        (latest[col].max() - latest[col].min())
    )

# Composite Score
latest["composite_score"] = (
    0.30 * latest["momentum"] +
    0.30 * latest["trend_strength"] +
    0.20 * latest["rsi_score"] +
    0.20 * (1 - latest["volatility"])
)

latest = latest.sort_values(
    "composite_score",
    ascending=False
).reset_index(drop=True)

latest["rank"] = latest.index + 1

# -----------------------------
# Top Ranking Table
# -----------------------------
st.subheader("🏆 Stock Ranking")

display_cols = [
    "rank",
    "ticker",
    "close",
    "rsi_14",
    "composite_score"
]

st.dataframe(
    latest[display_cols],
    use_container_width=True
)

# -----------------------------
# Bar Chart
# -----------------------------
st.subheader("📈 Composite Score Comparison")

fig = px.bar(
    latest,
    x="ticker",
    y="composite_score",
    text="composite_score",
    title="Composite Ranking Across Stocks"
)

fig.update_traces(texttemplate="%{text:.2f}")

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Radar Chart
# -----------------------------
st.subheader("🕸 Indicator Breakdown")

selected = st.selectbox(
    "Select a stock",
    latest["ticker"].tolist()
)

stock = latest[latest["ticker"] == selected].iloc[0]

radar_df = pd.DataFrame({
    "Metric": [
        "Momentum",
        "Trend",
        "RSI",
        "Low Volatility"
    ],
    "Score": [
        stock["momentum"],
        stock["trend_strength"],
        stock["rsi_score"],
        1 - stock["volatility"]
    ]
})

fig2 = px.line_polar(
    radar_df,
    r="Score",
    theta="Metric",
    line_close=True,
    title=f"{selected} Indicator Profile"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Best Pick
# -----------------------------
best = latest.iloc[0]

st.success(
    f"Top ranked stock: {best['ticker']} "
    f"(Score: {best['composite_score']:.2f})"
)