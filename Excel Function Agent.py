import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# -----------------------
# Setup
# -----------------------
client = OpenAI(api_key="YOUR_API_KEY")

st.set_page_config(page_title="AI Dashboard Agent", layout="wide")
st.title("🤖 AI Agent: Automated Excel Dashboard Builder")

st.markdown("""
Upload a dataset → Click **Create Dashboard** → AI analyzes & summarizes insights.

This simulates an **AI Agent (ReAct pattern):**
- 🧠 Reason: Understand data
- ⚙️ Act: Generate charts
- 📊 Output: Dashboard + insights
""")

# -----------------------
# Upload File
# -----------------------
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    if st.button("🚀 Create Dashboard"):

        # -----------------------
        # Basic Data Processing
        # -----------------------
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(exclude='number').columns.tolist()

        st.subheader("📊 Interactive Dashboard")

        # -----------------------
        # Filters (INTERACTIVITY)
        # -----------------------
        st.sidebar.header("🔎 Filters")
        filters = {}

        for col in categorical_cols[:3]:  # limit for simplicity
            options = df[col].dropna().unique()
            selected = st.sidebar.multiselect(f"Filter {col}", options, default=options)
            filters[col] = selected

        filtered_df = df.copy()
        for col, vals in filters.items():
            filtered_df = filtered_df[filtered_df[col].isin(vals)]

        # -----------------------
        # Chart 1: Histogram
        # -----------------------
        if numeric_cols:
            fig1 = px.histogram(filtered_df, x=numeric_cols[0], title="Distribution")
            st.plotly_chart(fig1, use_container_width=True)

        # -----------------------
        # Chart 2: Line Chart
        # -----------------------
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            fig2 = px.line(filtered_df, x=categorical_cols[0], y=numeric_cols[0], title="Trend")
            st.plotly_chart(fig2, use_container_width=True)

        # -----------------------
        # Chart 3: Bar Chart
        # -----------------------
        if categorical_cols and numeric_cols:
            grouped = filtered_df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index()
            fig3 = px.bar(grouped, x=categorical_cols[0], y=numeric_cols[0], title="Average by Category")
            st.plotly_chart(fig3, use_container_width=True)

        # -----------------------
        # Chart 4: Scatter Plot
        # -----------------------
        if len(numeric_cols) >= 2:
            fig4 = px.scatter(filtered_df, x=numeric_cols[0], y=numeric_cols[1], title="Correlation")
            st.plotly_chart(fig4, use_container_width=True)

        # -----------------------
        # Chart 5: Box Plot
        # -----------------------
        if numeric_cols and categorical_cols:
            fig5 = px.box(filtered_df, x=categorical_cols[0], y=numeric_cols[0], title="Distribution by Category")
            st.plotly_chart(fig5, use_container_width=True)

        # -----------------------
        # AI AGENT: Insight Summary
        # -----------------------
        st.subheader("🧠 AI-Generated Insights")

        summary_data = filtered_df.describe(include='all').to_string()

        prompt = f"""
        You are a business analyst.

        Here is summary statistics of a dataset:
        {summary_data}

        Provide 5 business insights in simple language.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        insights = response.choices[0].message.content

        st.write(insights)

        st.success("✅ Dashboard + AI insights generated!")

# -----------------------
# Instructions
# -----------------------
st.markdown("""
---
### 🎓 Teaching Notes
- This demonstrates an **AI Agent** automating Excel tasks
- Equivalent to: PivotTables + Charts + Analysis
- Shows how AI transforms **data → insights → decisions**
""")
