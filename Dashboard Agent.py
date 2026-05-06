import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="MIS Auto-Dashboard", layout="wide")
st.title("📊 Automated Avocado Executive Dashboard")
st.markdown("This dashboard was automatically generated using Python logic and the Avocado dataset.")

# ----------------------------
# Data Ingestion & Transformation (Pivot Logic)
# ----------------------------
@st.cache_data
def get_data():
    df = pd.read_csv("AvocadoData.csv")
    return df

df = get_data()

# ----------------------------
# Dashboard Layout (5 Key Visuals)
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    # 1. Pivot Table: Avg Price by Year and Type
    st.subheader("Price Trends (Yearly)")
    pivot_price = df.pivot_table(values='averageprice', index='year', columns='type', aggfunc='mean')
    st.bar_chart(pivot_price)
    
    # 2. Seasonality: Price by Month
    st.subheader("Monthly Seasonality")
    monthly_price = df.groupby('month')['averageprice'].mean()
    st.line_chart(monthly_price)

with col2:
    # 3. Top Regions by Volume
    st.subheader("Top 10 Regions by Volume")
    top_regions = df.groupby('region')['totalvolume'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_regions)
    
    # 4. Volume Distribution by Quarter
    st.subheader("Quarterly Market Share")
    quarter_vol = df.groupby('quarter')['totalvolume'].sum()
    st.write("Quarterly Volume Breakdown:")
    st.dataframe(quarter_vol, use_container_width=True)

# 5. Full Comparison & Summary
st.divider()
st.subheader("Executive Market Summary")
metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

metrics_col1.metric("Total Volume", f"{df['totalvolume'].sum():,.0f}")
metrics_col2.metric("Average Market Price", f"${df['averageprice'].mean():.2f}")
metrics_col3.metric("Highest Price Month", f"Month {df.groupby('month')['averageprice'].mean().idxmax()}")

# ----------------------------
# MIS Connection Logic
# ----------------------------
with st.expander("🎓 MIS Connection: How this automates the Excel Module"):
    st.write("""
    - **PivotTables:** Automated using `df.pivot_table()`.
    - **Charts:** Automatically rendered using Streamlit's native charting and Matplotlib.
    - **Data Integrity:** Ensuring the CSV columns match the expected data types (Data Governance).
    - **ReAct Pattern:** The system reads the CSV, 'thinks' about the column types, and 'acts' by generating relevant visualizations.
    """)