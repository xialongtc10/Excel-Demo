import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="AI Dashboard Agent", layout="wide")

st.title("🤖 AI Agent: Automated Dashboard Builder")
st.markdown("Upload data → Click **Create Dashboard** → AI analyzes & generates insights")

# -----------------------
# OPENAI SETUP
# -----------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------
# HELPER FUNCTIONS
# -----------------------

def load_data(file):
    return pd.read_csv(file)


def apply_filters(df, categorical_cols):
    st.sidebar.header("🔎 Filters")

    filtered_df = df.copy()

    for col in categorical_cols[:3]:
        options = df[col].dropna().unique()
        selected = st.sidebar.multiselect(f"{col}", options, default=options)

        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]

    return filtered_df


def create_charts(df):
    charts = []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    # Chart 1: Histogram
    if numeric_cols:
        fig = px.histogram(df, x=numeric_cols[0], title="Distribution")
        charts.append(fig)

    # Chart 2: Line
    if numeric_cols and categorical_cols:
        fig = px.line(df, x=categorical_cols[0], y=numeric_cols[0], title="Trend")
        charts.append(fig)

    # Chart 3: Bar (Pivot-style)
    if numeric_cols and categorical_cols:
        grouped = df.groupby(categorical_cols[0])[numeric_cols[0]].mean().reset_index()
        fig = px.bar(grouped, x=categorical_cols[0], y=numeric_cols[0], title="Average by Category")
        charts.append(fig)

    # Chart 4: Scatter
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title="Correlation")
        charts.append(fig)

    # Chart 5: Box
    if numeric_cols and categorical_cols:
        fig = px.box(df, x=categorical_cols[0], y=numeric_cols[0], title="Distribution by Category")
        charts.append(fig)

    return charts


def generate_insights(df):
    summary = df.describe(include="all").to_string()

    prompt = f"""
    You are a business analyst.

    Here is dataset summary:
    {summary}

    Provide 5 clear business insights.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -----------------------
# MAIN APP
# -----------------------

uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:

    df = load_data(uploaded_file)

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    if st.button("🚀 Create Dashboard"):

        st.info("🧠 Agent Thinking: Understanding data...")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        # Filters
        filtered_df = apply_filters(df, categorical_cols)

        st.success("⚙️ Agent Acting: Generating charts...")

        charts = create_charts(filtered_df)

        st.subheader("📊 Interactive Dashboard")

        for chart in charts:
            st.plotly_chart(chart, use_container_width=True)

        st.success("📊 Agent Output: Dashboard ready!")

        # AI Insights
        st.subheader("🧠 AI Insights")

        with st.spinner("Generating insights..."):
            insights = generate_insights(filtered_df)

        st.write(insights)

        st.success("✅ Completed!")
