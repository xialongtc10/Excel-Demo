import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="MIS Interactive Dashboard", layout="wide")
st.title("📊 Automated Business Intelligence Dashboard")
st.markdown("Upload your dataset to automatically generate an interactive MIS report.")

# ----------------------------
# Sidebar: Data Ingestion & Controls
# ----------------------------
with st.sidebar:
    st.header("1. Data Ingestion")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    st.divider()
    st.header("2. Dashboard Actions")
    create_button = st.button("🚀 Create Dashboard", use_container_width=True)
    
    if uploaded_file:
        st.success("File uploaded successfully!")
        # Global Filters (Interactive Element)
        st.divider()
        st.header("3. Global Filters")
        df_temp = pd.read_csv(uploaded_file)
        selected_year = st.multiselect("Select Year(s):", options=sorted(df_temp['year'].unique()), default=sorted(df_temp['year'].unique()))
        selected_type = st.radio("Select Avocado Type:", options=df_temp['type'].unique())

# ----------------------------
# ReAct Pattern: Processing & Rendering
# ----------------------------
if uploaded_file and create_button:
    # Read the data
    df = pd.read_csv(uploaded_file)
    
    # Apply Filters
    filtered_df = df[(df['year'].isin(selected_year)) & (df['type'] == selected_type)]
    
    # Dashboard Layout
    st.header(f"Executive Report: {selected_type} Avocados")
    
    # Row 1: Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Volume", f"{filtered_df['totalvolume'].sum():,.0f}")
    m2.metric("Avg Price", f"${filtered_df['averageprice'].mean():.2f}")
    m3.metric("Total Records", len(filtered_df))
    m4.metric("Market Reach (Regions)", filtered_df['region'].nunique())

    st.divider()

    # Row 2: Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price Trend Over Time")
        # Interactive Line Chart using Plotly
        fig_line = px.line(filtered_df.groupby('month')['averageprice'].mean().reset_index(), 
                           x='month', y='averageprice', title="Average Price by Month",
                           labels={'averageprice': 'Avg Price ($)', 'month': 'Month'})
        st.plotly_chart(fig_line, use_container_width=True)

        st.subheader("Top 10 Regions by Volume")
        top_regions = filtered_df.groupby('region')['totalvolume'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_bar = px.bar(top_regions, x='totalvolume', y='region', orientation='h', 
                         title="Volume by Region", color='totalvolume', color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("Quarterly Distribution")
        fig_pie = px.pie(filtered_df, values='totalvolume', names='quarter', title="Volume by Quarter",
                         hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Price vs. Volume Correlation")
        fig_scatter = px.scatter(filtered_df, x='averageprice', y='totalvolume', color='quarter',
                                 size='totalvolume', hover_data=['region'], title="Price vs. Volume Scatter")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Row 3: Raw Data Insight (Pivot Table)
    st.divider()
    st.subheader("Pivot Analysis: Monthly Pricing Strategy")
    pivot = filtered_df.pivot_table(index='month', columns='quarter', values='averageprice', aggfunc='mean')
    st.dataframe(pivot.style.highlight_max(axis=0), use_container_width=True)

elif not uploaded_file:
    st.info("Please upload a CSV file (like `AvocadoData.csv`) in the sidebar to begin.")
