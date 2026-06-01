# import streamlit as st

# st.set_page_config(
#     page_title="Stock ETL Dashboard",
#     page_icon="📈",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

# .stApp {
#     font-family: 'IBM Plex Sans', sans-serif !important;
#     background-color: #0d1117 !important;
#     color: #c9d1d9 !important;
# }
# .stApp p, .stApp li, .stApp span { color: #c9d1d9; }
# .stApp h1, .stApp h2, .stApp h3 {
#     color: #58a6ff !important;
#     font-family: 'IBM Plex Mono', monospace !important;
# }
# [data-testid="stSidebar"] {
#     background-color: #161b22 !important;
#     border-right: 1px solid #21262d;
# }
# #MainMenu, footer { visibility: hidden; }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("# 📈 Stock Market ETL Pipeline")
# st.markdown(
#     "<p style='color:#8b949e; font-family: IBM Plex Mono, monospace; font-size:0.85rem;'>"
#     "End-to-end batch ETL pipeline · Apache Airflow · PostgreSQL · Python"
#     "</p>",
#     unsafe_allow_html=True,
# )

# st.markdown("---")

# col1, col2 = st.columns(2)

# with col1:
#     st.markdown("### Navigate")
#     st.page_link("pages/1_Pipeline_Health.py", label="⚙️  Pipeline Health")
#     st.page_link("pages/2_Deep_Dive.py",        label="📊  Deep Dive — per ticker charts")

# with col2:
#     st.markdown("### Stack")
#     st.markdown("""
#     <p style='font-family: IBM Plex Mono, monospace; font-size: 0.8rem; color: #8b949e; line-height: 2;'>
#     Python &nbsp;·&nbsp; Apache Airflow &nbsp;·&nbsp; PostgreSQL<br>
#     SQLAlchemy &nbsp;·&nbsp; Pandas &nbsp;·&nbsp; Docker<br>
#     Streamlit &nbsp;·&nbsp; GitHub Actions
#     </p>
#     """, unsafe_allow_html=True)    


import streamlit as st

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Stock Market Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# Header
# -----------------------------------
st.title("📈 Stock Market Analytics Dashboard")
st.markdown(
    """
    Real-time stock market analytics pipeline powered by:

    **Apache Airflow · PostgreSQL · Docker Compose · Streamlit · GitHub**
    """
)

st.divider()

# -----------------------------------
# Project Overview
# -----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Data Pipeline", "Automated")

with col2:
    st.metric("Storage Layer", "PostgreSQL")

with col3:
    st.metric("Visualization", "Interactive")

# -----------------------------------
# Dashboard Sections
# -----------------------------------
st.subheader("Dashboard Modules")

st.markdown("""
### 📊 Pipeline Health
Monitor DAG execution, ingestion status, and pipeline reliability.

### 🔍 Stock Deep Dive
Analyze individual stock technical indicators and historical trends.

### 🏆 Stock Stack Comparison
Compare shortlisted stocks using composite technical scoring.
""")

st.divider()

# -----------------------------------
# Footer
# -----------------------------------
st.caption(
    "Built with Streamlit for portfolio demonstration | "
    "Deployed via GitHub"
)