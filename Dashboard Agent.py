import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="MIS Agentic Dashboard", layout="wide")
st.title("🥑 MIS Executive Dashboard + AI Insight Agent")
st.markdown("Automating the transition from raw data to executive intelligence.")

# ----------------------------
# Sidebar: Configuration & Ingestion
# ----------------------------
with st.sidebar:
    st.header("1. Setup")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    uploaded_file = st.file_uploader("Upload AvocadoData.csv", type=["csv"])
    
    if uploaded_file:
        # Prevent EmptyDataError: Store in session state so we only read once
        if 'df' not in st.session_state:
            st.session_state.df = pd.read_csv(uploaded_file)
        
        main_df = st.session_state.df
        
        st.divider()
        st.header("2. Data Filters")
        years = st.multiselect("Select Years:", options=sorted(main_df['year'].unique()), default=sorted(main_df['year'].unique()))
        avocado_type = st.radio("Select Type:", options=main_df['type'].unique())

    st.divider()
    # Manual trigger for the "Agentic" loop
    create_dashboard = st.button("🚀 Create Dashboard", use_container_width=True)

# ----------------------------
# Main Dashboard & Agent Logic
# ----------------------------
if uploaded_file and create_dashboard:
    # 1. Filter Data (Processing)
    df = st.session_state.df
    mask = (df['year'].isin(years)) & (df['type'] == avocado_type)
    filtered_df = df[mask]

    if filtered_df.empty:
        st.error("No data found for the selected filters.")
    else:
        # 2. Information Layer: KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        total_vol = filtered_df['totalvolume'].sum()
        avg_price = filtered_df['averageprice'].mean()
        m1.metric("Total Volume", f"{total_vol:,.0f}")
        m2.metric("Avg Market Price", f"${avg_price:.2f}")
        m3.metric("Data Points", f"{len(filtered_df):,}")
        m4.metric("Top Region", filtered_df.groupby('region')['totalvolume'].sum().idxmax())

        st.divider()

        # 3. Visualization Layer: 5 Interactive Charts
        col1, col2 = st.columns(2)

        with col1:
            # Chart 1: Price Trend
            fig_line = px.line(filtered_df.groupby('month')['averageprice'].mean().reset_index(), 
                               x='month', y='averageprice', title="Average Price Seasonality", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)

            # Chart 2: Top Regions
            top_10 = filtered_df.groupby('region')['totalvolume'].sum().nlargest(10).reset_index()
            fig_bar = px.bar(top_10, x='totalvolume', y='region', orientation='h', title="Top 10 Regions by Volume", color='totalvolume')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Chart 3: Quarterly Share
            fig_pie = px.pie(filtered_df, values='totalvolume', names='quarter', title="Volume Distribution by Quarter", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

            # Chart 4: Price vs Volume Correlation
            fig_scatter = px.scatter(filtered_df, x='averageprice', y='totalvolume', color='quarter', size='totalvolume', title="Price vs. Volume Correlation")
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Chart 5: Pivot-style Analysis Table
        st.subheader("Monthly Market Pricing Analysis")
        pivot = filtered_df.pivot_table(index='month', columns='quarter', values='averageprice', aggfunc='mean')
        st.dataframe(pivot.style.background_gradient(cmap='Greens'), use_container_width=True)

        # 4. Agent Layer: The AI Summarizer (The "Knowledge" Step)
        if api_key:
            st.divider()
            st.subheader("🤖 AI Agent: Executive Insights")
            
            with st.spinner("Agent analyzing dataset trends..."):
                client = OpenAI(api_key=api_key)
                
                # We feed the agent a textual summary of the calculated results
                context = f"""
                Dataset: Avocado Market Data
                Filters Applied: {avocado_type} avocados for years {years}.
                Total Volume: {total_vol:,.0f} units.
                Average Price: ${avg_price:.2f}.
                Peak Pricing Month: {filtered_df.groupby('month')['averageprice'].mean().idxmax()}.
                Volume Trend: The highest volume was in Quarter {filtered_df.groupby('quarter')['totalvolume'].sum().idxmax()}.
                """
                
                agent_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional MIS consultant. Summarize the dashboard findings in 3 concise bullet points. Focus on what these trends mean for supply chain management."},
                        {"role": "user", "content": context}
                    ]
                )
                
                st.info(agent_response.choices[0].message.content)
        else:
            st.warning("Please provide an OpenAI API Key in the sidebar to enable the AI Insight Agent.")

elif not uploaded_file:
    st.info("👋 Welcome, Professor! Please upload 'AvocadoData.csv' in the sidebar to begin the automation demo.")
