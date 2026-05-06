import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="MIS Agentic Dashboard", layout="wide")
st.title("🥑 MIS Executive Dashboard + AI Insight Agent")

# ----------------------------
# Sidebar: Data & API Settings
# ----------------------------
with st.sidebar:
    st.header("1. Data Ingestion")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    uploaded_file = st.file_uploader("Upload AvocadoData.csv", type=["csv"])
    
    if uploaded_file:
        if 'raw_df' not in st.session_state:
            st.session_state.raw_df = pd.read_csv(uploaded_file)
        df = st.session_state.raw_df
        
        st.divider()
        st.header("2. Filters")
        selected_year = st.multiselect("Years:", options=sorted(df['year'].unique()), default=sorted(df['year'].unique()))
        selected_type = st.radio("Type:", options=df['type'].unique())

    st.divider()
    create_button = st.button("🚀 Generate Dashboard & AI Summary", use_container_width=True)

# ----------------------------
# Main Application Logic
# ----------------------------
if uploaded_file and create_button:
    df = st.session_state.raw_df
    filtered_df = df[(df['year'].isin(selected_year)) & (df['type'] == selected_type)]
    
    # --- KPI Section ---
    m1, m2, m3, m4 = st.columns(4)
    total_vol = filtered_df['totalvolume'].sum()
    avg_price = filtered_df['averageprice'].mean()
    m1.metric("Total Volume", f"{total_vol:,.0f}")
    m2.metric("Avg Price", f"${avg_price:.2f}")
    m3.metric("Records", len(filtered_df))
    m4.metric("Top Region", filtered_df.groupby('region')['totalvolume'].sum().idxmax())

    # --- Charts Section ---
    c1, c2 = st.columns(2)
    with c1:
        fig_line = px.line(filtered_df.groupby('month')['averageprice'].mean().reset_index(), 
                           x='month', y='averageprice', title="Price Trend", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
    with c2:
        fig_pie = px.pie(filtered_df, values='totalvolume', names='quarter', title="Volume Share")
        st.plotly_chart(fig_pie, use_container_width=True)

    # ------------------------------------------------
    # 🤖 THE AI AGENT: Summarization Tool
    # ------------------------------------------------
    if api_key:
        st.divider()
        st.subheader("🤖 AI Consultant: Executive Summary")
        
        with st.spinner("Agent is analyzing the data..."):
            client = OpenAI(api_key=api_key)
            
            # Prepare a text-based summary for the agent to read
            top_3_regions = filtered_df.groupby('region')['totalvolume'].sum().nlargest(3).to_dict()
            
            agent_context = f"""
            DATA SUMMARY:
            - Product Type: {selected_type}
            - Years Analyzed: {selected_year}
            - Total Volume: {total_vol:,.0f}
            - Average Price: ${avg_price:.2f}
            - Top 3 Regions: {top_regions}
            - Monthly Price High: {filtered_df.groupby('month')['averageprice'].mean().idxmax()}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst. Summarize the findings from the dashboard in 3 bullet points. Focus on outliers and business implications."},
                    {"role": "user", "content": f"Analyze these findings: {agent_context}"}
                ]
            )
            
            st.info(response.choices[0].message.content)
    else:
        st.warning("Please enter an API Key in the sidebar to enable the AI Summary Agent.")

elif not uploaded_file:
    st.info("Please upload the dataset to start.")
