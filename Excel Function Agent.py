import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="MIS Interactive Dashboard", layout="wide")
st.title("🥑 Automated Business Intelligence Dashboard")
st.markdown("Upload your dataset to automatically generate an interactive MIS report.")

# ----------------------------
# Sidebar: Data Ingestion & Controls
# ----------------------------
with st.sidebar:
    st.header("1. Data Ingestion")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    st.divider()
    st.header("2. Dashboard Actions")
    # The 'Create' button triggers the logic below
    create_button = st.button("🚀 Create Dashboard", use_container_width=True)
    
    if uploaded_file:
        # Step 1: Check if data is already in session to avoid re-reading the file
        if 'raw_df' not in st.session_state:
            # We only read the CSV once
            st.session_state.raw_df = pd.read_csv(uploaded_file)
        
        df = st.session_state.raw_df
        
        st.success("File ready for processing.")
        
        # Step 2: Global Filters (The "MIS Control Room")
        st.divider()
        st.header("3. Global Filters")
        
        selected_year = st.multiselect(
            "Select Year(s):", 
            options=sorted(df['year'].unique()), 
            default=sorted(df['year'].unique())
        )
        
        selected_type = st.radio(
            "Select Avocado Type:", 
            options=df['type'].unique()
        )

# ----------------------------
# Dashboard Rendering Logic
# ----------------------------
if uploaded_file and create_button:
    # Access the data from session state
    df = st.session_state.raw_df
    
    # Filter logic: Re-querying the data based on UI input
    filtered_df = df[(df['year'].isin(selected_year)) & (df['type'] == selected_type)]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Try adjusting your selections.")
    else:
        st.header(f"Executive Report: {selected_type} Avocados ({', '.join(map(str, selected_year))})")
        
        # Row 1: Key Performance Indicators (KPIs)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{filtered_df['totalvolume'].sum():,.0f}")
        m2.metric("Avg Market Price", f"${filtered_df['averageprice'].mean():.2f}")
        m3.metric("Total Transactions", len(filtered_df))
        m4.metric("Active Regions", filtered_df['region'].nunique())

        st.divider()

        # Row 2: Interactive Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Price Trend Over Time")
            # Plotly Line Chart for interactivity (hover/zoom)
            fig_line = px.line(
                filtered_df.groupby('month')['averageprice'].mean().reset_index(), 
                x='month', y='averageprice', 
                title="Average Price by Month",
                labels={'averageprice': 'Avg Price ($)', 'month': 'Month'},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

            st.subheader("Top 10 Regions by Volume")
            top_regions = filtered_df.groupby('region')['totalvolume'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_bar = px.bar(
                top_regions, x='totalvolume', y='region', orientation='h', 
                title="Highest Volume Markets", 
                color='totalvolume', color_continuous_scale='Greens'
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("Quarterly Market Share")
            fig_pie = px.pie(
                filtered_df, values='totalvolume', names='quarter', 
                title="Volume Distribution by Quarter",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            st.subheader("Price vs. Volume Correlation")
            fig_scatter = px.scatter(
                filtered_df, x='averageprice', y='totalvolume', 
                color='quarter', size='totalvolume', 
                hover_data=['region'], 
                title="Price Impact on Demand"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Row 3: Automated Pivot Analysis
        st.divider()
        st.subheader("Automated Pivot Analysis: Monthly Pricing")
        st.markdown("This table replicates the **PivotTable** logic from the Excel module, highlighting maximum prices per quarter.")
        
        pivot = filtered_df.pivot_table(index='month', columns='quarter', values='averageprice', aggfunc='mean')
        st.dataframe(pivot.style.highlight_max(axis=0, color='lightgreen'), use_container_width=True)

# Placeholder when no file is uploaded
elif not uploaded_file:
    st.info("👋 Welcome! Please upload your `AvocadoData.csv` in the sidebar and click 'Create Dashboard' to see the automation in action.")
