"""
pages/2_Deep_Dive.py
────────────────────
Per-ticker deep dive: price + SMAs, RSI, Bollinger Bands, Volume.
Ticker list pulled dynamically from DB.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text

# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Deep Dive",
    page_icon="📊",
    layout="wide",
)

# ── styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'IBM Plex Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #58a6ff !important;
}

/* selectbox */
[data-testid="stSelectbox"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #8b949e !important;
    text-transform: uppercase;
    letter-spacing: 1px;
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
    font-size: 1.4rem !important;
    color: #c9d1d9 !important;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 6px;
    margin: 32px 0 16px 0;
}

.ticker-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #58a6ff;
    margin: 0;
}

.signal-bull {
    display: inline-block;
    background: #1a3a2a;
    color: #3fb950;
    border: 1px solid #3fb950;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 4px;
    letter-spacing: 1px;
    margin-left: 12px;
    vertical-align: middle;
}
.signal-bear {
    display: inline-block;
    background: #3a1a1a;
    color: #f85149;
    border: 1px solid #f85149;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 4px;
    letter-spacing: 1px;
    margin-left: 12px;
    vertical-align: middle;
}
.signal-neutral {
    display: inline-block;
    background: #1c2128;
    color: #8b949e;
    border: 1px solid #30363d;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 4px;
    letter-spacing: 1px;
    margin-left: 12px;
    vertical-align: middle;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── plotly theme ──────────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono, monospace", color="#8b949e", size=11),
    xaxis=dict(
        gridcolor="#21262d", linecolor="#30363d",
        tickfont=dict(color="#8b949e"),
        rangeslider=dict(visible=False),
    ),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
    margin=dict(l=0, r=0, t=40, b=0),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#161b22", bordercolor="#30363d", font_family="IBM Plex Mono, monospace"),
    legend=dict(bgcolor="#0d1117", bordercolor="#21262d", font=dict(color="#8b949e")),
)

# ── db ────────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_engine():
    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        st.error("DB_URL not set.")
        st.stop()
    return create_engine(DB_URL)


@st.cache_data(ttl=300)
def load_tickers():
    with get_engine().connect() as conn:
        rows = conn.execute(text(
            "SELECT DISTINCT ticker FROM stock_prices_enriched ORDER BY ticker"
        )).fetchall()
    return [r[0] for r in rows]


@st.cache_data(ttl=300)
def load_ticker_data(ticker: str) -> pd.DataFrame:
    query = text("""
        SELECT
            trade_date,
            close_price,
            volume,
            daily_return_pct,
            sma_20,
            sma_50,
            rsi_14,
            bb_upper,
            bb_lower,
            bb_bandwidth,
            vol_zscore,
            vol_spike
        FROM stock_prices_enriched
        WHERE ticker = :ticker
        ORDER BY trade_date
    """)
    with get_engine().connect() as conn:
        df = pd.read_sql(query, conn, params={"ticker": ticker})
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


# ── chart builders ────────────────────────────────────────────────────────────

def chart_price_sma(df: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["close_price"],
        name="Close", line=dict(color="#58a6ff", width=2),
        hovertemplate="%{y:.2f}",
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["sma_20"],
        name="SMA-20", line=dict(color="#d29922", width=1.5, dash="dot"),
        hovertemplate="%{y:.2f}",
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["sma_50"],
        name="SMA-50", line=dict(color="#f85149", width=1.5, dash="dash"),
        hovertemplate="%{y:.2f}",
    ))

    layout = PLOTLY_LAYOUT.copy()
    layout.update(title=dict(text="Price & Moving Averages", font=dict(color="#c9d1d9", size=13)))
    fig.update_layout(**layout)
    return fig


def chart_rsi(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # overbought / oversold bands
    fig.add_hrect(y0=70, y1=100, fillcolor="#f85149", opacity=0.06, line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="#3fb950", opacity=0.06, line_width=0)
    fig.add_hline(y=70, line_dash="dot", line_color="#f85149", line_width=1,
                  annotation_text="Overbought 70", annotation_position="right",
                  annotation_font_color="#f85149", annotation_font_size=10)
    fig.add_hline(y=30, line_dash="dot", line_color="#3fb950", line_width=1,
                  annotation_text="Oversold 30", annotation_position="right",
                  annotation_font_color="#3fb950", annotation_font_size=10)

    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["rsi_14"],
        name="RSI-14", line=dict(color="#a371f7", width=2),
        hovertemplate="%{y:.1f}",
    ))

    layout = PLOTLY_LAYOUT.copy()
    layout.update(
        title=dict(text="RSI-14  (Relative Strength Index)", font=dict(color="#c9d1d9", size=13)),
        yaxis=dict(range=[0, 100], gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
    )
    fig.update_layout(**layout)
    return fig


def chart_bollinger(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # shaded band
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["bb_upper"],
        name="BB Upper", line=dict(color="#30363d", width=1),
        hovertemplate="%{y:.2f}",
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["bb_lower"],
        name="BB Lower", line=dict(color="#30363d", width=1),
        fill="tonexty", fillcolor="rgba(88,166,255,0.07)",
        hovertemplate="%{y:.2f}",
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["close_price"],
        name="Close", line=dict(color="#58a6ff", width=2),
        hovertemplate="%{y:.2f}",
    ))

    layout = PLOTLY_LAYOUT.copy()
    layout.update(title=dict(text="Bollinger Bands", font=dict(color="#c9d1d9", size=13)))
    fig.update_layout(**layout)
    return fig


def chart_bb_bandwidth(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["bb_bandwidth"],
        name="BB Bandwidth", line=dict(color="#d29922", width=2),
        fill="tozeroy", fillcolor="rgba(210,153,34,0.07)",
        hovertemplate="%{y:.4f}",
    ))
    layout = PLOTLY_LAYOUT.copy()
    layout.update(title=dict(text="BB Bandwidth  (Volatility Squeeze Indicator)", font=dict(color="#c9d1d9", size=13)))
    fig.update_layout(**layout)
    return fig


def chart_volume(df: pd.DataFrame) -> go.Figure:
    colors = ["#f85149" if spike else "#21262d" for spike in df["vol_spike"].fillna(False)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["trade_date"], y=df["volume"],
        name="Volume",
        marker_color=colors,
        hovertemplate="%{y:,.0f}",
    ))
    fig.add_trace(go.Scatter(
        x=df["trade_date"], y=df["vol_zscore"],
        name="Vol Z-Score", yaxis="y2",
        line=dict(color="#58a6ff", width=1.5),
        hovertemplate="%{y:.2f}",
    ))

    layout = PLOTLY_LAYOUT.copy()
    layout.update(
        title=dict(text="Volume  (red = spike)", font=dict(color="#c9d1d9", size=13)),
        yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickfont=dict(color="#8b949e")),
        yaxis2=dict(
            overlaying="y", side="right",
            gridcolor="#21262d", linecolor="#30363d",
            tickfont=dict(color="#8b949e"),
            title=dict(text="Z-Score", font=dict(color="#8b949e")),
            zeroline=True, zerolinecolor="#30363d",
        ),
        barmode="overlay",
    )
    fig.update_layout(**layout)
    return fig


def chart_daily_return(df: pd.DataFrame) -> go.Figure:
    colors = ["#3fb950" if r >= 0 else "#f85149"
              for r in df["daily_return_pct"].fillna(0)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["trade_date"], y=df["daily_return_pct"],
        name="Daily Return %",
        marker_color=colors,
        hovertemplate="%{y:+.2f}%",
    ))
    fig.add_hline(y=0, line_color="#30363d", line_width=1)

    layout = PLOTLY_LAYOUT.copy()
    layout.update(title=dict(text="Daily Return %", font=dict(color="#c9d1d9", size=13)))
    fig.update_layout(**layout)
    return fig


# ── render ────────────────────────────────────────────────────────────────────

st.markdown("## 📊  Deep Dive")
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.8rem;'>"
    "Select a ticker to explore price action, momentum, volatility, and volume."
    "</p>",
    unsafe_allow_html=True,
)

# ── ticker selector ───────────────────────────────────────────────────────────

with st.spinner("Loading tickers..."):
    try:
        tickers = load_tickers()
    except Exception as e:
        st.error(f"DB error: {e}")
        st.stop()

selected = st.selectbox("Select Ticker", tickers, index=0)

# ── load data ─────────────────────────────────────────────────────────────────

with st.spinner(f"Loading data for {selected}..."):
    try:
        df = load_ticker_data(selected)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

if df.empty:
    st.warning(f"No data found for {selected}")
    st.stop()

latest = df.iloc[-1]

# ── ticker header ─────────────────────────────────────────────────────────────

sma_signal = "bullish" if latest["sma_20"] > latest["sma_50"] else (
    "bearish" if latest["sma_20"] < latest["sma_50"] else "neutral"
)
signal_labels = {
    "bullish": ("▲ BULLISH", "signal-bull"),
    "bearish": ("▼ BEARISH", "signal-bear"),
    "neutral": ("— NEUTRAL", "signal-neutral"),
}
signal_text, signal_class = signal_labels[sma_signal]

st.markdown(
    f"<p class='ticker-header'>{selected} "
    f"<span class='{signal_class}'>{signal_text}</span></p>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.75rem; margin-top:4px;'>"
    f"Data: {df['trade_date'].min().date()} → {df['trade_date'].max().date()} "
    f"&nbsp;·&nbsp; {len(df)} trading days"
    f"</p>",
    unsafe_allow_html=True,
)

# ── summary metrics ───────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Latest Snapshot</div>", unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

ret = latest["daily_return_pct"]
rsi = latest["rsi_14"]

c1.metric("Close Price",    f"${latest['close_price']:,.2f}")
c2.metric("Daily Return",   f"{ret:+.2f}%" if pd.notna(ret) else "—",
          delta=f"{ret:+.2f}%" if pd.notna(ret) else None,
          delta_color="normal")
c3.metric("RSI-14",         f"{rsi:.1f}" if pd.notna(rsi) else "—")
c4.metric("SMA-20",         f"${latest['sma_20']:,.2f}" if pd.notna(latest["sma_20"]) else "—")
c5.metric("SMA-50",         f"${latest['sma_50']:,.2f}" if pd.notna(latest["sma_50"]) else "—")
c6.metric("Vol Spike",      "⚡ Yes" if latest["vol_spike"] else "No")

# ── charts ────────────────────────────────────────────────────────────────────

st.markdown("<div class='section-label'>Price & Moving Averages</div>", unsafe_allow_html=True)
st.plotly_chart(chart_price_sma(df, selected), use_container_width=True)

st.markdown("<div class='section-label'>Daily Return %</div>", unsafe_allow_html=True)
st.plotly_chart(chart_daily_return(df), use_container_width=True)

st.markdown("<div class='section-label'>RSI-14</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.75rem; margin-top:-8px;'>"
    "Above 70 = overbought &nbsp;·&nbsp; Below 30 = oversold"
    "</p>",
    unsafe_allow_html=True,
)
st.plotly_chart(chart_rsi(df), use_container_width=True)

st.markdown("<div class='section-label'>Bollinger Bands</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.75rem; margin-top:-8px;'>"
    "Price touching bands signals potential reversal · Shaded area = 2σ band"
    "</p>",
    unsafe_allow_html=True,
)
st.plotly_chart(chart_bollinger(df), use_container_width=True)

st.markdown("<div class='section-label'>BB Bandwidth (Volatility)</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.75rem; margin-top:-8px;'>"
    "Squeeze (low bandwidth) often precedes a big move"
    "</p>",
    unsafe_allow_html=True,
)
st.plotly_chart(chart_bb_bandwidth(df), use_container_width=True)

st.markdown("<div class='section-label'>Volume & Z-Score</div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.75rem; margin-top:-8px;'>"
    "Red bars = volume spike (z-score > 2) · Blue line = z-score (right axis)"
    "</p>",
    unsafe_allow_html=True,
)
st.plotly_chart(chart_volume(df), use_container_width=True)

st.markdown(
    "<p style='color:#484f58; font-family: IBM Plex Mono, monospace; font-size:0.7rem; margin-top:40px;'>"
    "Data cached for 5 minutes. Switch tickers to reload."
    "</p>",
    unsafe_allow_html=True,
)