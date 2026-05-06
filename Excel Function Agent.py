import streamlit as st
import pandas as pd
from openai import OpenAI
import json

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(page_title="Avocado Excel Architect", layout="wide")
st.title("🥑 Avocado Excel Formula Generator")
st.markdown("Generate and test Excel formulas using real Avocado market data.")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    
    st.divider()
    st.markdown("### Avocado Demo Prompts")
    # Tailored prompts for the Avocado dataset
    avocado_prompts = [
        "Calculate the Revenue for row 2 (AveragePrice * TotalVolume).",
        "If TotalVolume > 10000, label it 'High Volume', else 'Low Volume'.",
        "Extract the first 5 characters of the Region name.",
        "Calculate a 10% price increase on the AveragePrice.",
        "Combine Region and Type into a single ID string (e.g., 'Albany_Organic')."
    ]
    
    clicked_task = None
    for task in avocado_prompts:
        if st.button(task, use_container_width=True):
            clicked_task = task

# ----------------------------
# Data Context (MIS Connection: Data Integrity)
# ----------------------------
@st.cache_data
def load_context():
    df = pd.read_csv("AvocadoData.csv")
    # Take a sample row to act as our "Excel Row" for the live test
    sample_row = df.iloc[0].to_dict()
    return sample_row

context_row = load_context()

# ----------------------------
# Agent Logic
# ----------------------------
task_input = st.text_input("Describe your Excel task:", value=clicked_task if clicked_task else "")

if task_input and api_key:
    client = OpenAI(api_key=api_key)
    
    with st.spinner("Generating formula..."):
        # We give the LLM the context of our specific columns
        sys_prompt = f"""
        You are an Excel Expert. The user is working with a table called 'AvocadoData'.
        Columns available: {list(context_row.keys())}.
        
        Current data for Row 2:
        {context_row}
        
        Task:
        1. Provide the Excel formula (assume columns are A to I).
        2. Explain the logic briefly.
        3. Perform the calculation using the provided Row 2 data.
        
        Return JSON: {{"formula": "...", "explanation": "...", "result": "..."}}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": task_input}],
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(response.choices[0].message.content)

        # ----------------------------
        # Display Results
        # ----------------------------
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🛠️ Generated Formula")
            st.code(data['formula'], language="excel")
            st.info(f"**Logic:** {data['explanation']}")

        with col2:
            st.subheader("🧪 Live Data Test (Row 2)")
            # Show the inputs so students see where the 'Result' comes from
            st.write(f"**Inputs:** Price: ${context_row['averageprice']} | Volume: {context_row['totalvolume']}")
            st.metric(label="Formula Output", value=data['result'])

        st.success("**MIS Lecture Tip:** Remind students that formulas are 'Logic as a Service'—AI helps with the syntax, but they define the business rule.")