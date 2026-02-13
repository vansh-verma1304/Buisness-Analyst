import streamlit as st
import pandas as pd
import re

from analysis import load_data, suggest_prompts, ask_llm, run_code

st.set_page_config(page_title="AI Business Analyst", layout="wide")
st.title("📊 AI Business Analyst Dashboard")

uploaded_file = st.file_uploader("Upload CSV / Excel file", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.success("Dataset Loaded Successfully")
    st.dataframe(df.head())

    st.sidebar.header("📌 Suggested Business Queries")
    suggestions = suggest_prompts(df)

    selected_prompt = st.sidebar.selectbox(
        "Choose a suggestion",
        ["-- Select --"] + suggestions
    )

    user_prompt = st.text_area(
        "Or write your own custom query",
        value="" if selected_prompt == "-- Select --" else selected_prompt
    )

    if st.button("Run Analysis"):
        with st.spinner("Analyzing data..."):
            llm_response = ask_llm(user_prompt)

            match = re.search(r"```python(.*?)```", llm_response, re.S)
            if not match:
                st.error("Invalid response from AI")
            else:
                code = match.group(1)
                output = run_code(df, code)

                if output["type"] == "dataframe":
                    st.dataframe(output["df"])
                elif output["type"] == "image":
                    st.image(output["path"])
                else:
                    st.text(output["output"])

