import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="Avocado SQL Agent - MIS Demo", layout="wide")
st.title("🥑 Avocado Data SQL Agent")
st.markdown("Convert natural language into SQL queries to analyze avocado market trends.")

# Sidebar for Configuration
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    
    st.divider()
    st.markdown("### Prepopulated Prompts")
    # Prepopulated prompts for direct selection
    sample_questions = [
        "Show the average price and total volume by region for 2018.",
        "What are the top 5 regions with the highest total volume of Organic avocados?",
        "Compare the average price of conventional vs organic avocados by quarter.",
        "Show the total volume per supplier for the year 2017."
    ]
    
    clicked_q = None
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            clicked_q = q

# ----------------------------
# Database Initialization (The "MIS Connection")
# ----------------------------
def init_db():
    df = pd.read_csv("AvocadoData.csv")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    df.to_sql('avocados', conn, index=False, if_exists='replace')
    # Get schema for the prompt
    schema = pd.io.sql.get_schema(df, 'avocados')
    return conn, schema

if "db_conn" not in st.session_state:
    st.session_state.db_conn, st.session_state.schema = init_db()

# ----------------------------
# SQL Generation Agent
# ----------------------------
query = st.text_input("Enter your request in plain English:", value=clicked_q if clicked_q else "")

if query and api_key:
    client = OpenAI(api_key=api_key)
    
    with st.spinner("Generating SQL..."):
        # System prompt instructs the model to act as an MIS data analyst
        sys_prompt = f"""
        You are an expert SQL assistant. Your job is to convert natural language into a SQLite query.
        The table name is 'avocados'. 
        The schema is as follows:
        {st.session_state.schema}
        
        Return ONLY the SQL code. Do not include triple backticks or explanations.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0
        )
        
        generated_sql = response.choices[0].message.content.strip()

        # Display the generated SQL (The "How it works" part)
        st.subheader("Generated SQL Code")
        st.code(generated_sql, language="sql")

        # ----------------------------
        # Execution & Result Display
        # ----------------------------
        try:
            results_df = pd.read_sql_query(generated_sql, st.session_state.db_conn)
            
            st.subheader("Query Results")
            st.dataframe(results_df, use_container_width=True)
            
            # Bonus: Simple visualization if there are numeric results
            if not results_df.empty and len(results_df.columns) >= 2:
                st.subheader("Quick Visualization")
                st.bar_chart(results_df.set_index(results_df.columns[0]))
                
        except Exception as e:
            st.error(f"Error executing SQL: {e}")
